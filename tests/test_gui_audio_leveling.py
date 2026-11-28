'''
@class TestGuiLeveling
@file test_gui_leveling.py
@author Gerald Manweiler

@brief Defines the GUI tests for audio leveling.

@details Verifies the behavior of the GUI for audio leveling.

@version 1.0.0
@date 2026-11-27

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import unittest                                             # for direct test-suite execution
from unittest import TestCase                               # for creating test cases
from unittest.mock import Mock                              # for mocking directory dialogs
from unittest.mock import patch                             # for patching the directory dialog

# Third Party Modules
import wx                                                   # for wxPython GUI components

# Local Module Methods
from tests.support import get_method_names                  # for direct test-suite construction
from tests.support import get_wx_app                        # for shared wx application instance

# Local Module Classes
from src.gui.wx_app import MainFrame                        # for the main GUI frame class
from src.models.audio_info.audio_art import AudioArt        # for audio-art operations
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


class TestGuiLeveling(TestCase):
    '''
    @brief Tests the GUI audio-leveling controls.

    @details Verifies that leveling controls respond to user interactions.
    '''


    def setUp(self):
        '''
        @brief Initialize the GUI frame for testing.

        @details Reuses the shared wx application and creates a main frame.

        @param self {TestGuiLeveling} The test instance.
        '''

        self.app = get_wx_app()
        self.frame = MainFrame(
            None,
            art=AudioArt(),
            directory=DirectoryProcessing(),
            metadata=AudioMetadata(),
            normalization=AudioNormalization(),
            utilities=AudioUtilities(),
            playlist=AudioPlaylist(),
        )
        self.addCleanup(wx.YieldIfNeeded)
        self.addCleanup(self.frame.Destroy)


    def test_level_file_target_button_opens_directory_dialog(self):
        '''
        @brief Test that the single-file leveling target button opens a directory dialog.

        @details Verifies that clicking the target button selects and displays a destination path.

        @param self {TestGuiLeveling} The test instance.
        '''

        target_button = self.frame.FindWindowByName("levelAudioFileTarget")
        target_path = self.frame.FindWindowByName("levelAudioFileDestPath")
        selected_path = "C:\\music\\leveled"
        dialog = Mock()
        dialog.ShowModal.return_value = wx.ID_OK
        dialog.GetPath.return_value = selected_path

        with patch("src.gui.handlers.wx.DirDialog", return_value=dialog) as dir_dialog:
            wx.PostEvent(target_button, wx.CommandEvent(wx.EVT_BUTTON.typeId, target_button.GetId()))
            wx.YieldIfNeeded()

        dir_dialog.assert_called_once_with(self.frame, "Select directory", style=wx.DD_DIR_MUST_EXIST)
        dialog.Destroy.assert_called_once_with()
        self.assertEqual(target_path.GetValue(), selected_path)


if __name__ == "__main__":
    '''
    @brief Run the TestGuiLeveling test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.

    @note This test module can be run directly with `python tests/test_gui_art_processing.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestGuiLeveling)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestGuiLeveling(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
