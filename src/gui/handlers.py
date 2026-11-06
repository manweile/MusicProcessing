'''
@class EventHandlers
@file handlers.py
@author Gerald Manweiler

@brief Defines the event handlers for the wxPython GUI application.

@details Provides the implementation of event handlers for the wxPython GUI application.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
from typing import TYPE_CHECKING                            # for type checking without circular imports

# Third Party Modules
import wx                                                   # for wxPython GUI components

# Local Module Classes
from src.audio_info import AudioArt                         # audio art handling class
from src.audio_info import AudioMetadata                    # audio metadata handling class
from src.audio_info import AudioPlaylist                    # audio playlist handling class
from src.audio_normalize import AudioNormalization          # audio normalization handling class
from src.dir_processing import DirectoryProcessing          # directory processing handling class

## @var art
# @brief instance of AudioArt class
# @details used for accessing class functionality
art = AudioArt()

## @var directory
# @brief instance of DirectoryProcessing class
# @details used for accessing class functionality
directory = DirectoryProcessing()

## @var metadata
# @brief instance of AudioMetadata class
# @details used for accessing class functionality
metadata = AudioMetadata()

## @var normalization
# @brief instance of AudioNormalization class
# @details used for accessing class functionality
normalization = AudioNormalization()

## @var playlist
# @brief instance of AudioPlaylist class
# @details used for accessing class functionality
playlist = AudioPlaylist()

if TYPE_CHECKING:
    from wx_app import MainFrame


class EventHandlers:
    '''
    @brief Defines the event handlers for the wxPython GUI application.

    @details This class provides methods for handling various events triggered by user interactions with the GUI,<br>
    such as browsing for files or directories, converting files, normalizing audio, extracting album art, and updating playlists.
    '''

    def __init__(self, main_frame: "MainFrame"):
        '''
        @brief Initialize the EventHandlers class.

        @details A basic class implementation with no instantiation parameters.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param main_frame {wx.Frame} The main frame of the application.
        '''

        self.mainFrame = main_frame


    def on_browse_dir(self, event, textctrl):
        '''
        @brief Handle the event for browsing a directory.

        @details Opens a directory dialog for the user to select a directory.<br>
        The selected directory path is then set in the provided text control.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        @param textctrl {wx.TextCtrl} The text control to update with the selected directory path.
        '''

        # prevent typing or picking a non-existent path
        dlg = wx.DirDialog(self.mainFrame, "Select directory", style=wx.DD_DIR_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            textctrl.SetValue(path)
            textctrl.SetFocus()

        dlg.Destroy()


    def on_browse_file(self, event, textctrl, wildcard=None):
        '''
        @brief Handle the event for browsing a file.

        @details Opens a file dialog for the user to select a file.<br>
        The selected file path is then set in the provided text control.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        @param textctrl {wx.TextCtrl} The text control to update with the selected file path.
        @param wildcard {str} Optional, the file type filter for the dialog.
        '''

        if wildcard is None:
            wildcard = ""

        # open/select existing file; trying to type or choose a non-existent file name will trigger a warning
        dlg = wx.FileDialog(self.mainFrame, "Select file", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST, wildcard=wildcard)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            textctrl.SetValue(path)
            textctrl.SetFocus()

        dlg.Destroy()


    def on_convert_file(self, event):
        '''
        @brief Handle the event for converting a single file.

        @details Retrieves the file path from the GUI, validates it, and then runs the conversion task.<br>
        The conversion task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the file path from the GUI and validate it before conversion
        path = self.mainFrame.convert_file_path.GetValue().strip()
        if not self.mainFrame._validate_file(path):
            return

        self.mainFrame.run_task(metadata.convert_file, path, on_success=self.mainFrame._show_generated_files_dialog)


    def on_convert_walk(self, event):
        '''
        @brief Handle the event for converting files in a directory walk.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the conversion task.<br>
        The conversion task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the top-level directory and validate it before conversion
        tld = self.mainFrame.convert_walk_tld.GetValue().strip()
        if not self.mainFrame._validate_dir(tld):
            return

        # Get the file type pattern selection from the GUI
        selection = self.mainFrame.convert_walk_pattern.GetSelection()
        pattern = None if selection == 0 else self.mainFrame.convert_walk_pattern.GetString(selection)
        self.mainFrame.run_task(metadata.convert_walk, tld, pattern, on_success=self.mainFrame._show_generated_files_dialog)


    def on_ebu_file(self, event):
        '''
        @brief Handle the event for EBU normalization of a single file.

        @details Retrieves the file path from the GUI, validates it, and then runs the EBU normalization task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the result file.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the file path from the GUI and validate it before EBU normalization
        path = self.mainFrame.ebu_file_path.GetValue().strip()
        if not self.mainFrame._validate_file(path):
            return

        self.mainFrame.run_task(normalization.ebu_normalize_file, path, on_success=lambda: self.mainFrame._show_result_file("ebu_normalize_file"))


    def on_extract_file_art(self, event):
        '''
        @brief Handle the event for extracting album art from a single file.

        @details Retrieves the file path from the GUI, validates it, and then runs the album art extraction task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the file path from the GUI and validate it before extracting album art
        file_path = self.mainFrame.filePathText.GetValue().strip()

        if not self.mainFrame._validate_file(file_path):
            return

        self.mainFrame.run_task(art.extract_album_art, file_path)


    def on_extract_walk_art(self, event):
        '''
        @brief Handle the event for extracting album art from a directory walk.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the album art extraction task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the top-level directory and validate it before extracting album art from a directory walk
        start_path = self.mainFrame.bulkPathText.GetValue().strip()
        if not self.mainFrame._validate_dir(start_path):
            return

        # Get the file type pattern selection from the GUI
        selection = self.mainFrame.patternChoice.GetSelection()
        pattern = None if selection == 0 else self.mainFrame.patternChoice.GetString(selection)
        self.mainFrame.run_task(art.extract_walk, start_path, pattern)


    def on_get_media_info_walk(self, event):
        '''
        @brief Handle the event for retrieving media information from a directory walk.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the media information retrieval task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the top-level directory and validate it before retrieving media information from a directory walk
        tld = self.mainFrame.media_info_tld.GetValue().strip()
        if not self.mainFrame._validate_dir(tld):
            return

        # Get the file type pattern from the GUI
        pattern = self.mainFrame.media_info_pattern.GetValue().strip() or None
        self.mainFrame.run_task(metadata.get_media_info_walk, tld, pattern, on_success=self.mainFrame._show_generated_files_dialog)


    def on_get_tags_walk(self, event):
        '''
        @brief Handle the event for retrieving media tags from a directory walk.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the media tags retrieval task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the top-level directory and validate it before retrieving media tags from a directory walk
        tld = self.mainFrame.tags_walk_tld.GetValue().strip()
        if not self.mainFrame._validate_dir(tld):
            return

        # Get the file type pattern and ffprobe path from the GUI
        pattern = self.mainFrame.tags_walk_pattern.GetValue().strip() or None
        ffprobe = self.mainFrame.tags_walk_ffprobe.GetValue()
        self.mainFrame.run_task(metadata.get_tags_walk, tld, pattern, ffprobe, on_success=self.mainFrame._show_generated_files_dialog)


    def on_get_unique_media(self, event):
        '''
        @brief Handle the event for retrieving unique media files from a directory walk.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the unique media retrieval task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the top-level directory and validate it before retrieving unique media files
        tld = self.mainFrame.unique_media_tld.GetValue().strip()
        if not self.mainFrame._validate_dir(tld):
            return

        self.mainFrame.run_task(metadata.get_unique_media, tld, on_success=self.mainFrame._show_generated_files_dialog)


    def on_list_audio(self, event):
        '''
        @brief Handle the event for listing audio files in a directory.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the audio listing task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the top-level directory and validate it before listing audio files``
        tld = self.mainFrame.list_audio_tld.GetValue().strip()
        if not self.mainFrame._validate_dir(tld):
            return

        self.mainFrame.run_task(directory.list_audio, tld, on_success=self.mainFrame._show_generated_files_dialog)


    def on_list_type(self, event):
        '''
        @brief Handle the event for listing files of a specific type in a directory.

        @details Retrieves the top-level directory and file extension from the GUI, validates them, and then runs the file type listing task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the top-level directory and validate it before listing files of a specific type
        tld = self.mainFrame.list_type_tld.GetValue().strip()
        if not self.mainFrame._validate_dir(tld):
            return

        # Get the file extension from the GUI and validate it before listing files of a specific type
        ext = self.mainFrame.list_type_ext.GetValue().strip()
        if not ext:
            wx.MessageBox("Please enter a file extension", "Error", wx.ICON_ERROR)
            return

        self.mainFrame.run_task(directory.list_type, tld, ext, on_success=self.mainFrame._show_generated_files_dialog)


    def on_normalize_walk(self, event):
        '''
        @brief Handle the event for normalizing audio files in a directory walk.

        @details Retrieves the top-level directory and normalization type from the GUI, validates them, and then runs the normalization task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the top-level directory and validate it before normalizing audio files in a directory walk
        tld = self.mainFrame.norm_walk_tld.GetValue().strip()
        if not self.mainFrame._validate_dir(tld):
            return

        # Get the normalization type from the GUI
        norm_type = self.mainFrame.norm_type_choice.GetStringSelection().lower()
        self.mainFrame.run_task(normalization.normalize_walk, tld, norm_type, on_success=self.mainFrame._show_generated_files_dialog)


    def on_peak_file(self, event):
        '''
        @brief Handle the event for peak normalizing a single audio file.

        @details Retrieves the file path from the GUI, validates it, and then runs the peak normalization task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the result file.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the file path from the GUI and validate it before peak normalizing the audio file
        path = self.mainFrame.peak_file_path.GetValue().strip()
        if not self.mainFrame._validate_file(path):
            return

        self.mainFrame.run_task(normalization.peak_normalize_file, path, on_success=lambda: self.mainFrame._show_result_file("peak_normalize_file"))


    def on_remove_albums(self, event):
        '''
        @brief Handle the event for removing albums from a directory.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the album removal task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the top-level directory and validate it before removing albums
        tld = self.mainFrame.remove_albums_tld.GetValue().strip()
        if not self.mainFrame._validate_dir(tld):
            return

        self.mainFrame.run_task(directory.remove_albums, tld, on_success=self.mainFrame._show_generated_files_dialog)


    def on_remove_pattern(self, event):
        '''
        @brief Handle the event for removing files matching a pattern from a directory.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the pattern removal task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the top-level directory and validate it before removing files matching a pattern
        tld = self.mainFrame.remove_pattern_tld.GetValue().strip()
        if not self.mainFrame._validate_dir(tld):
            return

        # Get the pattern from the GUI and validate it before removing files matching a pattern
        pattern = self.mainFrame.remove_pattern_pattern.GetValue().strip()
        if not pattern:
            wx.MessageBox("Please enter a pattern to remove", "Error", wx.ICON_ERROR)
            return

        self.mainFrame.run_task(directory.remove_pattern, tld, pattern, on_success=self.mainFrame._show_generated_files_dialog)


    def on_rms_file(self, event):
        '''
        @brief Handle the event for RMS normalizing a single audio file.

        @details Retrieves the file path from the GUI, validates it, and then runs the RMS normalization task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the result file.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the file path from the GUI and validate it before RMS normalizing the audio file
        path = self.mainFrame.rms_file_path.GetValue().strip()
        if not self.mainFrame._validate_file(path):
            return

        self.mainFrame.run_task(normalization.rms_normalize_file, path, on_success=lambda: self.mainFrame._show_result_file("rms_normalize_file"))


    def on_set_album_art(self, event):
        '''
        @brief Handle the event for setting album art for audio files in a directory.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the album art setting task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the top-level directory and validate it before setting album art for audio files in a directory
        tld = self.mainFrame.settingPathText.GetValue().strip()
        if not self.mainFrame._validate_dir(tld):
            return

        self.mainFrame.run_task(art.set_album_art, tld)


    def on_update_m3u(self, event):
        '''
        @brief Handle the event for updating an M3U playlist.

        @details Retrieves the M3U file path from the GUI, validates it, and then runs the playlist update task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with generated playlist files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the M3U file path from the GUI and validate it before updating the playlist
        m3u_file = self.mainFrame.update_m3u_file.GetValue().strip()
        if not self.mainFrame._validate_file(m3u_file):
            return

        self.mainFrame.run_task(playlist.update_playlist, m3u_file, on_success=self.mainFrame._show_generated_playlist_dialog)


    def on_update_walk(self, event):
        '''
        @brief Handle the event for updating a directory walk.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the directory walk update task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with generated playlist files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # Get the top-level directory from the GUI and validate it before updating a directory walk
        tld = self.mainFrame.update_walk_tld.GetValue().strip()
        if not self.mainFrame._validate_dir(tld):
            return

        self.mainFrame.run_task(playlist.update_walk, tld, on_success=self.mainFrame._show_generated_playlist_dialog)
