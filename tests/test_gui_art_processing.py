'''
@class TestGuiArtProcessing
@file test_gui_art_processing.py
@author Gerald Manweiler

@brief Defines the GUI tests for art processing.

@details Verifies the behavior of the GUI for art processing.

@version 1.0.0
@date 2024-06-24

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import os                                                   # for file and directory operations
import shutil                                               # for high-level file operations
import tempfile                                             # for creating temporary directories
import time                                                 # for time-related functions
import unittest                                             # for direct test-suite execution
from unittest import TestCase                               # for creating test cases
from unittest.mock import patch                             # for mocking objects in tests

# Third-Party Modules
import wx                                                   # for wxPython GUI components

# Local Module Methods
from tests.support import get_method_names                  # for direct test-suite construction
from tests.support import get_wx_app                        # for shared wx application instance

# Local Module Constants
from src.core.constants import ALBUM_ART                    # for album art directory
from src.core.constants import FOLDER_ART                   # for album-art fixture filenames
from src.core.constants import MP3_EXT                      # for MP3 file-pattern extraction tests

from tests import TEST_M4A_DAVIS                            # for M4A album-art extraction tests
from tests import TEST_MP3_ABBA                             # for existing album-art file tests
from tests import TEST_MP3_CRUSH                            # for MP3 album-art extraction tests
from tests import TEST_MP3_NO_TAG                           # for absent album-art tests
from tests import TEST_WMA_JOHN                             # for WMA stream album-art tests
from tests import TESTS_TLD                                 # for test music fixture paths

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


class TestGuiArtProcessing(TestCase):
    '''
    @brief Tests for the GUI art processing functionality.

    @details Verifies that the GUI correctly handle art processing operations, including art extraction and setting.
    '''

    def _destroy_frame(self):
        '''
        @brief Destroys the MainFrame instance if it exists.

        @details Ensures proper cleanup of the GUI frame to prevent resource leaks.

        @param self {TestGuiArtProcessing} Test instance containing the frame to destroy.
        '''

        if self.frame:
            self.frame.Destroy()
            wx.YieldIfNeeded()


    def _wait_until(self, predicate, timeout=10):
        '''
        @brief Waits until a specified condition is met or a timeout occurs.

        @details Continuously checks the provided predicate function until it returns True or the timeout is reached.<br>
        Yields to the GUI event loop to keep the interface responsive.

        @param self {TestGuiArtProcessing} Test instance invoking the wait.
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
        @brief Initializes data for for the GUI art processing tests.

        @details Initializes the wx.App instance and sets up the list of source file paths to be used in the tests.

        @param cls {TestGuiArtProcessing} Test class receiving shared fixtures.
        '''

        # reuse the wx.App instance for the GUI tests, else could get a segmentation fault due to multiple wx.App instances
        cls.app = get_wx_app()

        # prepare the list of source file paths for the tests
        cls.prepped_src_file_paths = [TEST_M4A_DAVIS, TEST_MP3_CRUSH, TEST_WMA_JOHN]


    def setUp(self):
        '''
        @brief Sets up the test environment for each test method.

        @details Creates temporary directories for prepped and generated files, patches the GENERATED_PATH, and initializes the MainFrame instance.

        @param self {TestGuiArtProcessing} Test instance receiving the setup environment.
        '''

        temp_dir = tempfile.TemporaryDirectory(prefix="musicprocessing-gui-art-")
        self.addCleanup(temp_dir.cleanup)

        self.prepped = os.path.join(temp_dir.name, "PreppedMusic")
        self.generated = os.path.join(temp_dir.name, "generated")
        self.album_art_dir = os.path.join(self.generated, ALBUM_ART)
        os.makedirs(self.album_art_dir)

        # patch the GENERATED_PATH constant to point to the temporary generated directory
        generated_path_patcher = patch("src.models.audio_info.audio_art.GENERATED_PATH", self.generated)
        generated_path_patcher.start()
        self.addCleanup(generated_path_patcher.stop)

        # copy in the fixtures
        for source in self.prepped_src_file_paths:
            relative_source_path = os.path.relpath(source, TESTS_TLD)
            destination = os.path.join(self.prepped, relative_source_path)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)

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


    def test_extract_album_art(self):
        '''
        @brief Test album-art extraction from an audio file.

        @details Simulates user interaction to verify extraction creates the expected album-art file.

        @test Happy path.

        @param self {TestGuiArtProcessing} The instance of the test class.
        '''

        # find the path control and extract button for album-art extraction
        path_control = self.frame.FindWindowByName("extractArtFilePath")
        extract_button = self.frame.FindWindowByName("extractArtFile")

        self.assertIsNotNone(path_control)
        self.assertIsNotNone(extract_button)

        # set the source audio file for extraction and the expected album-art path
        source = os.path.join(self.prepped, os.path.relpath(TEST_WMA_JOHN, TESTS_TLD))
        expected_art = os.path.join(os.path.dirname(source), FOLDER_ART)

        # set the path control value to the source audio file and simulate clicking the extract button
        path_control.SetValue(source)
        wx.PostEvent(extract_button, wx.CommandEvent(wx.EVT_BUTTON.typeId, wx.ID_ANY))

        # wait until the log indicates that album-art extraction has completed
        self._wait_until(lambda: "extract_album_art completed." in self.frame.mainLog.GetValue())

        # verify that the expected album-art file exists
        self.assertTrue(os.path.isfile(expected_art), expected_art)


    def test_extract_walk(self):
        '''
        @brief Test album-art extraction from all valid audio files.

        @details Simulates user interaction to verify walk extraction creates artwork for prepared files without a pattern.

        @test Happy path.

        @param self {TestGuiArtProcessing} The instance of the test class.
        '''

        # find the path control and extract button for album-art extraction from a directory
        path_control = self.frame.FindWindowByName("extractArtPath")
        extract_button = self.frame.FindWindowByName("extractArtDir")

        self.assertIsNotNone(path_control)
        self.assertIsNotNone(extract_button)

        # set the path control value to the prepared directory and simulate clicking the extract button
        path_control.SetValue(self.prepped)
        wx.PostEvent(extract_button, wx.CommandEvent(wx.EVT_BUTTON.typeId, wx.ID_ANY))

        # wait until the log indicates that walk extraction has completed
        self._wait_until(lambda: "extract_walk completed." in self.frame.mainLog.GetValue())

        # verify that the expected album-art files exist for all prepared source files
        for source in self.prepped_src_file_paths:
            album_dir = os.path.join(self.prepped, os.path.relpath(os.path.dirname(source), TESTS_TLD))
            expected_art = os.path.join(album_dir, FOLDER_ART)
            self.assertTrue(os.path.isfile(expected_art), expected_art)


    def test_extract_walk_pattern(self):
        '''
        @brief Test album-art extraction with an MP3 file pattern.

        @details Simulates user interaction to verify walk extraction creates artwork only for matching prepared MP3 files.

        @test Happy path.

        @param self {TestGuiArtProcessing} The instance of the test class.
        '''

        # find the path control, pattern choice, and extract button for album-art extraction from a directory
        path_control = self.frame.FindWindowByName("extractArtPath")
        pattern_choice = self.frame.FindWindowByName("extractArtChoice")
        extract_button = self.frame.FindWindowByName("extractArtDir")

        self.assertIsNotNone(path_control)
        self.assertIsNotNone(pattern_choice)
        self.assertIsNotNone(extract_button)

        # set the path control value, select the MP3 pattern, and simulate clicking the extract button
        path_control.SetValue(self.prepped)
        pattern_choice.SetStringSelection(MP3_EXT)
        wx.PostEvent(extract_button, wx.CommandEvent(wx.EVT_BUTTON.typeId, wx.ID_ANY))

        # wait until the log indicates that walk extraction has completed
        self._wait_until(lambda: "extract_walk completed." in self.frame.mainLog.GetValue())

        # verify that the expected album-art file exists for the MP3 album
        mp3_album_dir = os.path.join(self.prepped, os.path.relpath(os.path.dirname(TEST_MP3_CRUSH), TESTS_TLD))
        self.assertTrue(os.path.isfile(os.path.join(mp3_album_dir, FOLDER_ART)))

        # verify that no album-art files exist for non-MP3 albums
        for source in (TEST_M4A_DAVIS, TEST_WMA_JOHN):
            album_dir = os.path.join(self.prepped, os.path.relpath(os.path.dirname(source), TESTS_TLD))
            self.assertFalse(os.path.exists(os.path.join(album_dir, FOLDER_ART)))


    def test_set_album_art(self):
        '''
        @brief Test setting album-art files in an audio directory.

        @details Simulates user interaction to verify existing artwork is retained and matching artwork is copied from an isolated fixture.

        @test Happy path.

        @param self: (TestGuiArtProcessing) The instance of the test class.
        '''

        # verify set_album_art preserves artwork already present in an album
        existing_album_dir = os.path.join(self.prepped, "Abba", "Waterloo")
        os.makedirs(existing_album_dir)
        shutil.copy2(TEST_MP3_ABBA, os.path.join(existing_album_dir, os.path.basename(TEST_MP3_ABBA)))

        # ensure set_album_art skips an album that already contains Folder.jpg
        existing_art_source = os.path.join(os.path.dirname(TEST_MP3_ABBA), FOLDER_ART)
        existing_art = os.path.join(existing_album_dir, FOLDER_ART)
        shutil.copy2(existing_art_source, existing_art)

        # provide an album without art whose name matches the generated image
        target_album_dir = os.path.join(self.prepped, "Albert Collins", "Best Of The Blues, Vol. 1",)
        os.makedirs(target_album_dir)
        shutil.copy2(TEST_MP3_NO_TAG, os.path.join(target_album_dir, os.path.basename(TEST_MP3_NO_TAG)))

        # supply matching source artwork so set_album_art can populate the target album
        generated_art = os.path.join(self.album_art_dir, "Best Of The Blues, Vol. 1.jpg")
        shutil.copy2(existing_art_source, generated_art)

        # find the path control and button for setting album art
        path_control = self.frame.FindWindowByName("setArtPath")
        set_button = self.frame.FindWindowByName("setArtDir")

        self.assertIsNotNone(path_control)
        self.assertIsNotNone(set_button)

        # set the path control value to the prepped directory and trigger the set album art action
        path_control.SetValue(self.prepped)
        wx.PostEvent(set_button, wx.CommandEvent(wx.EVT_BUTTON.typeId, wx.ID_ANY))

        # wait until the set_album_art process completes as indicated in the main log
        self._wait_until(lambda: "set_album_art completed." in self.frame.mainLog.GetValue())

        # verify that the target album now contains the expected artwork file
        target_art = os.path.join(target_album_dir, FOLDER_ART)
        self.assertTrue(os.path.isfile(target_art), target_art)

        # verify that the target album now contains the expected artwork file
        with open(existing_art_source, "rb") as source_file, open(target_art, "rb") as target_file:
            self.assertEqual(source_file.read(), target_file.read())

        # verify that the existing artwork remains unchanged
        with open(existing_art_source, "rb") as source_file, open(existing_art, "rb") as existing_file:
            self.assertEqual(source_file.read(), existing_file.read())


if __name__ == "__main__":
    '''
    @brief Run the TestGuiArtProcessing test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.

    @note This test module can be run directly with `python tests/test_gui_art_processing.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestGuiArtProcessing)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestGuiArtProcessing(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
