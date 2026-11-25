'''
@class TestGuiNameManagement
@file test_gui_name_management.py
@author Gerald Manweiler

@brief Defines the GUI tests for name management.

@details Verifies the behavior of the GUI for name management.

@version 1.0.0
@date 2026-11-09

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import os                                                   # for file and directory operations
import shutil                                               # for high-level file operations
import tempfile                                             # for creating temporary directories
import time                                                 # for time-related functions
from unittest import TestCase                               # for creating test cases
import unittest
from unittest.mock import patch                             # for mocking objects in tests

# Third-Party Modules
import wx                                                   # for wxPython GUI components

# Local Module Methods
from tests.support import get_method_names                  # for direct test-suite construction
from tests.support import get_wx_app                        # for shared wx application instance

# Local Module Constants
from tests import TEST_FLAC_CREAM                           # test data for Cream FLAC audio file
from tests import TEST_M4A_DAVIS                            # test data for M4A Joshua Davis audio file
from tests import TEST_M4A_EAGLES                           # test data for M4A Eagles audio file
from tests import TEST_MP3_10CC                             # test data for MP3 10cc audio file
from tests import TEST_MP3_ABBA                             # test data for MP3 ABBA audio file
from tests import TEST_MP3_GENESIS                          # test data for MP3 Genesis audio file
from tests import TEST_MP3_NO_METADATA                      # test data for MP3 file without metadata
from tests import TEST_WMA_CCR                              # test data for WMA CCR audio file
from tests import TEST_WMA_JOHN                             # test data for WMA Elton John audio file
from tests import TESTS_TLD                                 # test music directory

from src.core.constants import CSV_DIR                      # for the CSV directory path
from src.core.constants import CSV_EXT                      # for the CSV file extension

# Local Module Classes
from src.gui.wx_app import MainFrame                        # for the main GUI frame class

from src.models.audio_info.audio_art import AudioArt        # for handling audio artwork
# for handling audio metadata
from src.models.audio_info.audio_metadata import AudioMetadata
# for handling audio playlists
from src.models.audio_info.audio_playlist import AudioPlaylist
# for audio utility functions
from src.models.audio_info.audio_utilities import AudioUtilities
# for audio normalization
from src.models.audio_normalize.audio_normalization import AudioNormalization
# for directory processing
from src.models.dir_processing.directory_processing import DirectoryProcessing

## @var art
# @brief AudioArt instance under test.
# @details Provides access to album-art functionality.
art = AudioArt()

## @var metadata
# @brief AudioMetadata instance under test.
# @details Provides access to audio metadata functionality.
metadata = AudioMetadata()

## @var normalization
# @brief AudioNormalization instance under test.
# @details Provides access to normalization functionality.
normalization = AudioNormalization()

## @var playlist
# @brief AudioPlaylist instance under test.
# @details Provides access to playlist parsing and path-update functionality.
playlist = AudioPlaylist()

## @var utilities
# @brief AudioUtilities instance under test.
# @details Provides access to audio utility functionality.
utilities = AudioUtilities()

## @var directory
# @brief DirectoryProcessing instance under test.
# @details Provides access to directory processing functionality.
directory = DirectoryProcessing()


class TestGuiNameManagement(TestCase):
    ''''
    @brief Tests for the GUI name management functionality.

    @details Verifies that the GUI correctly handles name management operations, including adding, editing, and removing album folders.
    '''

    def _destroy_frame(self):
        '''
        @brief Destroys the MainFrame instance if it exists.

        @details Ensures proper cleanup of the GUI frame to prevent resource leaks.

        @param self {TestGuiNameManagement} Test instance containing the frame to destroy.
        '''

        if self.frame:
            self.frame.Destroy()
            wx.YieldIfNeeded()


    def _wait_until(self, predicate, timeout=10):
        '''
        @brief Waits until a specified condition is met or a timeout occurs.

        @details Continuously checks the provided predicate function until it returns True or the timeout is reached.<br>
        Yields to the GUI event loop to keep the interface responsive.

        @param self {TestGuiNameManagement} Test instance invoking the wait.
        @param predicate {Callable} Function that returns a boolean indicating if the condition is met.
        @param timeout {int} Maximum time to wait in seconds (default is 10).
        '''

        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            wx.YieldIfNeeded()
            if predicate():
                return

            time.sleep(0.01)

        self.fail(f"Condition was not met within {timeout} seconds")


    @classmethod
    def setUpClass(cls):
        '''
        @brief Initializes data for for the GUI name management tests.

        @details Initializes the wx.App instance and sets up the list of source file paths to be used in the tests.

        @param cls {TestGuiNameManagement} Test class receiving shared fixtures.
        '''

        # reuse the wx.App instance for the GUI tests, else could get a segmentation fault due to multiple wx.App instances
        cls.app = get_wx_app()

        # prepare the list of source file paths for the tests
        cls.prepped_src_file_paths = [TEST_M4A_EAGLES, TEST_MP3_ABBA, TEST_MP3_GENESIS, TEST_MP3_NO_METADATA, TEST_WMA_CCR]


    def setUp(self):
        '''
        @brief Sets up the test environment for each test method.

        @details Creates temporary directories for prepped and generated files, patches the GENERATED_PATH, and initializes the MainFrame instance.

        @param self {TestGuiNameManagement} Test instance receiving the setup environment.
        '''

        temp_dir = tempfile.TemporaryDirectory(prefix="musicprocessing-gui-")
        self.addCleanup(temp_dir.cleanup)

        self.prepped = os.path.join(temp_dir.name, "PreppedMusic")
        self.generated = os.path.join(temp_dir.name, "generated")
        os.makedirs(os.path.join(self.generated, CSV_DIR), exist_ok=True)

        # patch the GENERATED_PATH constant to point to the temporary generated directory
        generated_path_patcher = patch("src.models.dir_processing.directory_processing.GENERATED_PATH", self.generated)
        generated_path_patcher.start()
        self.addCleanup(generated_path_patcher.stop)

        # copy in the fixtures
        for source in self.prepped_src_file_paths:
            relative_source_path = os.path.relpath(source, TESTS_TLD)
            artist = relative_source_path.split(os.sep, 1)[0]
            artist_dir = os.path.join(self.prepped, artist)
            os.makedirs(artist_dir, exist_ok=True)
            shutil.copy2(source, os.path.join(artist_dir, os.path.basename(source)))

        # initialize the MainFrame instance for the GUI tests
        self.frame = MainFrame(
            None,
            art=AudioArt(),
            directory=DirectoryProcessing(),
            metadata=AudioMetadata(),
            normalization=AudioNormalization(),
            utilities=AudioUtilities(),
            playlist=AudioPlaylist(),
        )

        # yield to the GUI event loop to ensure the frame is fully initialized
        wx.YieldIfNeeded()
        # add cleanup to destroy the frame after the test completes
        self.addCleanup(self._destroy_frame)


    def test_add_album_folders(self):
        '''
        @brief Tests creating an album sub-directory in an artist directory.

        @details Simulates user interaction to add the album sub-directory should be created for each album within the artist directory.

        @test Happy path.

        @param self {TestGuiNameManagement} The instance of the test class.
        '''

        # find the path control and add button for adding album folders
        path_control = self.frame.FindWindowByName("addAlbumsWalkTld")
        add_button = self.frame.FindWindowByName("addAlbumsWalk")

        self.assertIsNotNone(path_control)
        self.assertIsNotNone(add_button)

        # set the path control value to the prepped directory and simulate clicking the add button
        path_control.SetValue(self.prepped)
        wx.PostEvent(add_button, wx.CommandEvent(wx.EVT_BUTTON.typeId, wx.ID_ANY))

        # wait until the log indicates that album directories have been created
        self._wait_until(lambda: "create_album_dirs completed." in self.frame.mainLog.GetValue())

        # define the expected moves for verification
        expected_moves = [
            ("The Eagles", "Desperado", "The Eagles-Desperado.m4a"),
            ("Abba", "Waterloo", "ABBA-Waterloo.mp3"),
            ("Creedence Clearwater Revival", "Chronicle, Vol. 1", "Creedence Clearwater Revival-Fortunate Son.wma"),
            ("Genesis", "In Too Deep - I'd Rather Be You", "Genesis-In Too Deep.mp3"),
        ]

        # verify files were moved correctly into created album folders
        for artist, album, filename in expected_moves:
            artist_dir = os.path.join(self.prepped, artist)
            album_file = os.path.join(artist_dir, album, filename)
            original_file = os.path.join(artist_dir, filename)

            self.assertTrue(os.path.isfile(album_file), album_file)
            self.assertFalse(os.path.exists(original_file), original_file)

        # verify that files without metadata remain in place, without any album folders created
        no_metadata_dir = os.path.join(self.prepped, "NoMetadata")
        self.assertEqual(os.listdir(no_metadata_dir), ["No_tag_Crush-Live.mp3"])

        # verify that the report for created album directories exists
        report_path = os.path.join(self.generated, CSV_DIR, "create_album_dirs" + CSV_EXT)
        self.assertTrue(os.path.isfile(report_path))


    def test_rename_album_folders(self):
        '''
        @brief tests renaming album directory from album metadata.

        @details Copies the Genesis fixture into a temporary artist directory.

        @test Happy path, already-correct name, and name collision.

        @param self {TestGuiNameManagement} The instance of the test class.
        '''

        # create the artist directory and the incorrectly named album directory
        artist_dir = os.path.join(self.prepped, "Genesis")
        wrong_dir = os.path.join(artist_dir, "In Too Deep-I’d Rather Be You")
        expected_dir = os.path.join(artist_dir, "In Too Deep - I'd Rather Be You")
        genesis_file = os.path.join(artist_dir, os.path.basename(TEST_MP3_GENESIS))

        # create the incorrectly named album directory and move the Genesis file into it
        os.makedirs(wrong_dir)
        shutil.move(genesis_file, os.path.join(wrong_dir, os.path.basename(TEST_MP3_GENESIS)))

        # find the path control and button for renaming album folders
        path_control = self.frame.FindWindowByName("renameAlbumsWalkTld")
        rename_button = self.frame.FindWindowByName("renameAlbumsWalk")

        self.assertIsNotNone(path_control)
        self.assertIsNotNone(rename_button)

        # set the path control value to the prepped directory
        path_control.SetValue(self.prepped)


        def rename_albums():
            '''
            @brief Helper function to trigger the renaming of album directories and wait for completion.

            @details Clears the main log, posts button event starting renaming process, waits until completion message is in log.

            @note This function is used within the test to simulate user interaction with the GUI.
            '''

            self.frame.mainLog.Clear()
            wx.PostEvent(rename_button, wx.CommandEvent(wx.EVT_BUTTON.typeId, wx.ID_ANY))
            self._wait_until(lambda: "rename_album_directories completed." in self.frame.mainLog.GetValue())

        # verify an incorrectly named directory is renamed
        rename_albums()
        self.assertFalse(os.path.exists(wrong_dir))
        self.assertTrue(os.path.isfile(os.path.join(expected_dir, os.path.basename(TEST_MP3_GENESIS))))

        # an already correctly named directory remains unchanged
        rename_albums()
        self.assertTrue(os.path.isdir(expected_dir))

        # an existing destination causes the renamed directory to use a counter suffix
        os.makedirs(wrong_dir)
        shutil.copy2(TEST_MP3_GENESIS, os.path.join(wrong_dir, os.path.basename(TEST_MP3_GENESIS)))

        # trigger the renaming process and verify the results
        rename_albums()
        self.assertFalse(os.path.exists(wrong_dir))
        self.assertTrue(os.path.isfile(os.path.join(expected_dir, os.path.basename(TEST_MP3_GENESIS))))
        self.assertTrue(os.path.isfile(os.path.join(f"{expected_dir} (1)", os.path.basename(TEST_MP3_GENESIS))))


    def test_rename_files_walk(self):
        '''
        @brief Tests normalizing filenames during a directory walk.

        @details Verifies all supported audio files are renamed.

        @test Happy path.

        @param self {TestGuiNameManagement} The instance of the test class.
        '''

        # prepare a generated album-art file for the target album
        test_dir = os.path.join(self.prepped, "normalize_filename_walk")
        os.makedirs(test_dir)

        # copy the audio fixtures into the test directory with incorrect names
        audio_files = [
            (TEST_MP3_10CC, "10cc-Donna.mp3"),
            (TEST_FLAC_CREAM, "Cream-Politician.flac"),
            (TEST_M4A_DAVIS, "Joshua Davis-The Workingman’s Hymn.m4a"),
            (TEST_M4A_EAGLES, "The Eagles-Desperado.m4a"),
            (TEST_WMA_CCR, "Creedence Clearwater Revival-Fortunate Son.wma"),
            (TEST_WMA_JOHN, "Elton John-Saturday Night’s Alright (for Fighting).wma")
        ]

        # prepare lists to track the source and normalized file paths
        source_files = []
        normalized_files = []

        # copy the audio fixtures to the test directory with incorrect names and track their paths
        for index, (fixture, normalized_name) in enumerate(audio_files):
            _, file_ext = os.path.splitext(fixture)
            source_file = os.path.join(test_dir, f"incorrect-name-{index}{file_ext}")
            shutil.copy2(fixture, source_file)
            source_files.append(source_file)
            normalized_files.append(os.path.join(test_dir, normalized_name))

        # create a non-audio file to ensure it is not affected by the renaming process
        notes_file = os.path.join(test_dir, "notes.txt")
        with open(notes_file, "w", encoding="utf-8") as notes:
            notes.write("not an audio file")

        # find the path control and button for renaming files
        path_control = self.frame.FindWindowByName("renameFilesWalkTld")
        rename_button = self.frame.FindWindowByName("renameFilesWalk")

        self.assertIsNotNone(path_control)
        self.assertIsNotNone(rename_button)

        # set the path control value and simulate clicking the rename button
        path_control.SetValue(test_dir)
        wx.PostEvent(rename_button, wx.CommandEvent(wx.EVT_BUTTON.typeId, wx.ID_ANY))

        # wait until the log indicates that filename normalization has completed
        self._wait_until(lambda: "normalize_filename_walk completed." in self.frame.mainLog.GetValue())

        # verify that all source files have been removed after renaming
        for source_file in source_files:
            self.assertFalse(os.path.exists(source_file), source_file)

        # verify that all normalized files exist after renaming
        for normalized_file in normalized_files:
            self.assertTrue(os.path.isfile(normalized_file), normalized_file)

        # verify that the non-audio file remains unaffected by the renaming process
        self.assertTrue(os.path.isfile(notes_file), notes_file)


    def test_rename_file(self):
        '''
        @brief Tests renaming an audio file using its album artist and title metadata.

        @details Verifies that an audio file is renamed according to its album artist and title metadata.

        @test Happy path.

        @param self {TestGuiNameManagement} The instance of the test class.
        '''

        # prepare the test directory for renaming a single audio file
        test_dir = os.path.join(self.prepped, "rename_single_file")
        os.makedirs(test_dir)

        # define the source and normalized file paths for the test
        wrong_file = os.path.join(test_dir, "incorrect-name.mp3")
        normalized_file = os.path.join(test_dir, "10cc-Donna.mp3")
        shutil.copy2(TEST_MP3_10CC, wrong_file)

        # find the path control and button for renaming a single audio file
        path_control = self.frame.FindWindowByName("renameAudioFilePath")
        rename_button = self.frame.FindWindowByName("renameAudioFile")

        self.assertIsNotNone(path_control)
        self.assertIsNotNone(rename_button)

        # set the path control value and simulate clicking the rename button
        path_control.SetValue(wrong_file)
        wx.PostEvent(rename_button, wx.CommandEvent(wx.EVT_BUTTON.typeId, wx.ID_ANY))

        # wait until the log indicates that filename normalization has completed
        self._wait_until(lambda: "normalize_filename completed." in self.frame.mainLog.GetValue())

        self.assertFalse(os.path.exists(wrong_file), wrong_file)
        self.assertTrue(os.path.isfile(normalized_file), normalized_file)

        # verify that the report for the normalized filename exists
        report_path = os.path.join(self.generated, CSV_DIR, "normalize_filename" + CSV_EXT)
        self.assertTrue(os.path.isfile(report_path))


if __name__ == "__main__":
    '''
    @brief Run the TestGuiNameManagement test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.

    @note This test module can be run directly with `python tests/test_gui_name_management.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestGuiNameManagement)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestGuiNameManagement(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
