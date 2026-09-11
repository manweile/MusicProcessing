'''
@file handlers.py
@brief Defines the event handlers for the wxPython GUI application.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# third party modules
import wx
# local module classes
from src.audio_info import AudioArt, AudioMetadata, AudioPlaylist
from src.audio_normalize import AudioNormalization
from src.dir_processing import DirectoryProcessing

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


class EventHandlers:
    '''
    @brief Defines the event handlers for the wxPython GUI application.

    @details This class provides methods for handling various events triggered by user interactions with the GUI, such as browsing for files or directories, converting files, normalizing audio, extracting album art, and updating playlists.

    @param main_frame The main frame of the application.
    '''

    def __init__(self, main_frame):
        '''
        @brief Initialize the EventHandlers class.

        @details A basic class implementation with no instantiation parameters.

        @param main_frame The main frame of the application.
        '''

        self.frame = main_frame

    def on_browse_dir(self, event, textctrl):
        '''
        @brief Handle the event for browsing a directory.

        @details Opens a directory dialog for the user to select a directory.
        The selected directory path is then set in the provided text control.

        @param event {object} The event object.
        @param textctrl {wx.TextCtrl} The text control to update with the selected directory path.
        '''

        dlg = wx.DirDialog(self.frame, "Select directory", style=wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            textctrl.SetValue(path)
            textctrl.SetFocus()

        dlg.Destroy()

    def on_browse_file(self, event, textctrl, wildcard=None):
        '''
        @brief Handle the event for browsing a file.

        @details Opens a file dialog for the user to select a file.
        The selected file path is then set in the provided text control.

        @param event {object} The event object.
        @param textctrl {wx.TextCtrl} The text control to update with the selected file path.
        @param wildcard {str} The file type filter for the dialog.
        '''

        if wildcard is None:
            wildcard = ""

        dlg = wx.FileDialog(self.frame, "Select file", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST, wildcard=wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            textctrl.SetValue(path)
            textctrl.SetFocus()

        dlg.Destroy()

    def on_convert_file(self, event):
        '''
        @brief Handle the event for converting a single file.

        @details Retrieves the file path from the GUI, validates it, and then runs the conversion task.
        The conversion task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param event {object} The event object.
        '''

        path = self.frame.convert_file_path.GetValue().strip()
        if not self.frame._validate_file(path):
            return

        self.frame.run_task(metadata.convert_file, path, on_success=self.frame._show_generated_files_dialog)

    def on_convert_walk(self, event):
        '''
        @brief Handle the event for converting files in a directory walk.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the conversion task.
        The conversion task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param event {object} The event object.
        '''

        tld = self.frame.convert_walk_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return

        selection = self.frame.convert_walk_pattern.GetSelection()
        pattern = None if selection == 0 else self.frame.convert_walk_pattern.GetString(selection)
        self.frame.run_task(metadata.convert_walk, tld, pattern, on_success=self.frame._show_generated_files_dialog)

    def on_ebu_file(self, event):
        '''
        @brief Handle the event for EBU normalization of a single file.

        @details Retrieves the file path from the GUI, validates it, and then runs the EBU normalization task.
        The task is executed asynchronously, and upon success, a dialog is shown with the result file.

        @param event {object} The event object.
        '''

        path = self.frame.ebu_file_path.GetValue().strip()
        if not self.frame._validate_file(path):
            return

        self.frame.run_task(normalization.ebu_normalize_file, path, on_success=lambda: self.frame._show_result_file("ebu_normalize_file"))

    def on_extract_file_art(self, event):
        '''
        @brief Handle the event for extracting album art from a single file.

        @details Retrieves the file path from the GUI, validates it, and then runs the album art extraction task.
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param event {object} The event object.
        '''

        path = self.frame.extract_file_art_path.GetValue().strip()
        if not self.frame._validate_file(path):
            return

        self.frame.run_task(art.extract_album_art, path, on_success=self.frame._show_generated_files_dialog)

    def on_extract_walk_art(self, event):
        '''
        @brief Handle the event for extracting album art from a directory walk.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the album art extraction task.
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param event {object} The event object.
        '''

        tld = self.frame.extract_walk_art_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return

        selection = self.frame.extract_walk_art_pattern.GetSelection()
        pattern = None if selection == 0 else self.frame.extract_walk_art_pattern.GetString(selection)
        self.frame.run_task(art.extract_walk, tld, pattern, on_success=self.frame._show_generated_files_dialog)

    def on_get_media_info_walk(self, event):
        '''
        @brief Handle the event for retrieving media information from a directory walk.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the media information retrieval task.
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param event {object} The event object.
        '''

        tld = self.frame.media_info_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return

        pattern = self.frame.media_info_pattern.GetValue().strip() or None
        self.frame.run_task(metadata.get_media_info_walk, tld, pattern, on_success=self.frame._show_generated_files_dialog)

    def on_get_tags_walk(self, event):
        '''
        @brief Handle the event for retrieving media tags from a directory walk.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the media tags retrieval task.
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param event {object} The event object.
        '''

        tld = self.frame.tags_walk_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return

        pattern = self.frame.tags_walk_pattern.GetValue().strip() or None
        ffprobe = self.frame.tags_walk_ffprobe.GetValue()
        self.frame.run_task(metadata.get_tags_walk, tld, pattern, ffprobe, on_success=self.frame._show_generated_files_dialog)

    def on_get_unique_media(self, event):
        '''
        @brief Handle the event for retrieving unique media files from a directory walk.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the unique media retrieval task.
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param event {object} The event object.
        '''

        tld = self.frame.unique_media_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return

        self.frame.run_task(metadata.get_unique_media, tld, on_success=self.frame._show_generated_files_dialog)

    def on_list_audio(self, event):
        '''
        @brief Handle the event for listing audio files in a directory.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the audio listing task.
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param event {object} The event object.
        '''

        tld = self.frame.list_audio_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return

        self.frame.run_task(directory.list_audio, tld, on_success=self.frame._show_generated_files_dialog)

    def on_list_type(self, event):
        '''
        @brief Handle the event for listing files of a specific type in a directory.

        @details Retrieves the top-level directory and file extension from the GUI, validates them, and then runs the file type listing task.
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param event {object} The event object.
        '''

        tld = self.frame.list_type_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return

        ext = self.frame.list_type_ext.GetValue().strip()
        if not ext:
            wx.MessageBox("Please enter a file extension", "Error", wx.ICON_ERROR)
            return

        self.frame.run_task(directory.list_type, tld, ext, on_success=self.frame._show_generated_files_dialog)

    def on_normalize_walk(self, event):
        '''
        @brief Handle the event for normalizing audio files in a directory walk.

        @details Retrieves the top-level directory and normalization type from the GUI, validates them, and then runs the normalization task.
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param event {object} The event object.
        '''

        tld = self.frame.norm_walk_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return

        norm_type = self.frame.norm_type_choice.GetStringSelection().lower()
        self.frame.run_task(normalization.normalize_walk, tld, norm_type, on_success=self.frame._show_generated_files_dialog)

    def on_peak_file(self, event):
        '''
        @brief Handle the event for peak normalizing a single audio file.

        @details Retrieves the file path from the GUI, validates it, and then runs the peak normalization task.
        The task is executed asynchronously, and upon success, a dialog is shown with the result file.

        @param event {object} The event object.
        '''

        path = self.frame.peak_file_path.GetValue().strip()
        if not self.frame._validate_file(path):
            return

        self.frame.run_task(normalization.peak_normalize_file, path, on_success=lambda: self.frame._show_result_file("peak_normalize_file"))

    def on_remove_albums(self, event):
        '''
        @brief Handle the event for removing albums from a directory.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the album removal task.
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param event {object} The event object.
        '''

        tld = self.frame.remove_albums_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return

        self.frame.run_task(directory.remove_albums, tld, on_success=self.frame._show_generated_files_dialog)

    def on_remove_pattern(self, event):
        '''
        @brief Handle the event for removing files matching a pattern from a directory.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the pattern removal task.
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param event {object} The event object.
        '''

        tld = self.frame.remove_pattern_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return

        pattern = self.frame.remove_pattern_pattern.GetValue().strip()
        if not pattern:
            wx.MessageBox("Please enter a pattern to remove", "Error", wx.ICON_ERROR)
            return

        self.frame.run_task(directory.remove_pattern, tld, pattern, on_success=self.frame._show_generated_files_dialog)

    def on_rms_file(self, event):
        '''
        @brief Handle the event for RMS normalizing a single audio file.

        @details Retrieves the file path from the GUI, validates it, and then runs the RMS normalization task.
        The task is executed asynchronously, and upon success, a dialog is shown with the result file.

        @param event {object} The event object.
        '''

        path = self.frame.rms_file_path.GetValue().strip()
        if not self.frame._validate_file(path):
            return

        self.frame.run_task(normalization.rms_normalize_file, path, on_success=lambda: self.frame._show_result_file("rms_normalize_file"))

    def on_set_album_art(self, event):
        '''
        @brief Handle the event for setting album art for audio files in a directory.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the album art setting task.
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param event {object} The event object.
        '''

        tld = self.frame.set_album_art_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return

        self.frame.run_task(art.set_album_art, tld, on_success=self.frame._show_generated_files_dialog)

    def on_update_m3u(self, event):
        '''
        @brief Handle the event for updating an M3U playlist.

        @details Retrieves the M3U file path from the GUI, validates it, and then runs the playlist update task.
        The task is executed asynchronously, and upon success, a dialog is shown with generated playlist files.

        @param event {object} The event object.
        '''

        m3u_file = self.frame.update_m3u_file.GetValue().strip()
        if not self.frame._validate_file(m3u_file):
            return

        self.frame.run_task(playlist.update_playlist, m3u_file, on_success=self.frame._show_generated_playlist_dialog)

    def on_update_walk(self, event):
        '''
        @brief Handle the event for updating a directory walk.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the directory walk update task.
        The task is executed asynchronously, and upon success, a dialog is shown with generated playlist files.

        @param event {object} The event object.
        '''

        tld = self.frame.update_walk_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return

        self.frame.run_task(playlist.update_walk, tld, on_success=self.frame._show_generated_playlist_dialog)
