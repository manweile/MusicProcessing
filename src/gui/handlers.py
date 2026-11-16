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

# Local Module Methods
from src.controllers.validation import validate_dir         # for checking directory paths
from src.controllers.validation import validate_file        # for checking file paths

# Local Module Classes
from src.models.audio_info.audio_art import AudioArt        # audio art handling class
# audio metadata handling class
from src.models.audio_info.audio_metadata import AudioMetadata
# audio playlist handling class
from src.models.audio_info.audio_playlist import AudioPlaylist
# normalization handling class
from src.models.audio_normalize.audio_normalization import AudioNormalization
# directory processing class
from src.models.dir_processing.directory_processing import DirectoryProcessing

if TYPE_CHECKING:
    from wx_app import MainFrame


class EventHandlers:
    '''
    @brief Defines the event handlers for the wxPython GUI application.

    @details This class provides methods for handling various events triggered by user interactions with the GUI,<br>
    such as browsing for files or directories, converting files, normalizing audio, extracting album art, and updating playlists.
    '''

    def __init__(
        self,
        main_frame: "MainFrame",
        art: AudioArt,
        directory: DirectoryProcessing,
        metadata: AudioMetadata,
        normalization: AudioNormalization,
        playlist: AudioPlaylist
    ):
        '''
        @brief Initialize the EventHandlers class.

        @details Stores the main frame and the model instances supplied by the composition root.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param main_frame {wx.Frame} The main frame of the application.
        @param art {AudioArt} The audio-art model instance.
        @param directory {DirectoryProcessing} The directory-processing model instance.
        @param metadata {AudioMetadata} The audio-metadata model instance.
        @param normalization {AudioNormalization} The audio-normalization model instance.
        @param playlist {AudioPlaylist} The audio-playlist model instance.
        '''

        self.mainFrame = main_frame
        self.art = art
        self.directory = directory
        self.metadata = metadata
        self.normalization = normalization
        self.playlist = playlist


    def _validate_dir(self, path: str) -> bool:
        '''
        @brief Validate a directory path and display a message if it is invalid.

        @details Delegates the path check to the shared validator and reports failures in the GUI.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param path {str} The directory path to validate.

        @retval {bool} Whether the path identifies an existing directory.
        '''

        if validate_dir(path):
            return True

        if not path:
            wx.MessageBox("Please specify a directory path.", "Validation", wx.ICON_WARNING)
        else:
            wx.MessageBox(f"Directory not found: {path}", "Validation", wx.ICON_ERROR)

        return False


    def _validate_file(self, path: str) -> bool:
        '''
        @brief Validate a file path and display a message if it is invalid.

        @details Delegates the path check to the shared validator and reports failures in the GUI.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param path {str} The file path to validate.

        @retval {bool} Whether the path identifies an existing file.
        '''

        if validate_file(path):
            return True

        if not path:
            wx.MessageBox("Please specify a file path.", "Validation", wx.ICON_WARNING)
        else:
            wx.MessageBox(f"File not found: {path}", "Validation", wx.ICON_ERROR)

        return False


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


    def on_convert_file_audio(self, event):
        '''
        @brief Handle the event for converting a single file.

        @details Retrieves the file path from the GUI, validates it, and then runs the conversion task.<br>
        The conversion task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the file path from the GUI and validate it before conversion
        path = self.mainFrame.convertAudioPath.GetValue().strip()

        # not a valid file, return early
        if not self._validate_file(path):
            return

        callback = self.mainFrame.show_generated_files
        self.mainFrame.taskRunner.run_task(self.metadata.convert_file, path, on_success=callback)


    def on_convert_directory_audio(self, event):
        '''
        @brief Handle the event for converting files in a directory walk.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the conversion task.<br>
        The conversion task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the top-level directory and validate it before conversion
        tld = self.mainFrame.convertWalkTld.GetValue().strip()

        # not a valid directory, return early
        if not self._validate_dir(tld):
            return

        # get the file type pattern selection from the GUI
        selection = self.mainFrame.convertAudioChoice.GetSelection()
        if selection == 0:
            pattern = None
        else:
            pattern = self.mainFrame.convertAudioChoice.GetString(selection)

        callback = self.mainFrame.show_generated_files
        self.mainFrame.taskRunner.run_task(self.metadata.convert_walk, tld, pattern, on_success=callback)


    def on_ebu_file(self, event):
        '''
        @brief Handle the event for EBU normalization of a single file.

        @details Retrieves the file path from the GUI, validates it, and then runs the EBU normalization task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the result file.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the file path from the GUI and validate it before EBU normalization
        path = self.mainFrame.ebu_file_path.GetValue().strip()

        # not a valid file, return early
        if not self._validate_file(path):
            return

        # define the callback function to display the result file after EBU normalization
        def callback():
            '''
            @brief Display the EBU normalization result file.

            @details Opens the result file after the ebu normalization task succeeds.
            '''

            self.mainFrame._show_result_file("ebu_normalize_file")

        self.mainFrame.taskRunner.run_task(self.normalization.ebu_normalize_file, path, on_success=callback)


    def on_extract_file_art(self, event):
        '''
        @brief Handle the event for extracting album art from a single file.

        @details Retrieves the file path from the GUI, validates it, and then runs the album art extraction task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the file path from the GUI and validate it before extracting album art
        file_path = self.mainFrame.extractArtPath.GetValue().strip()

        # not a valid file, return early
        if not self._validate_file(file_path):
            return

        self.mainFrame.taskRunner.run_task(self.art.extract_album_art, file_path)


    def on_extract_directory_art(self, event):
        '''
        @brief Handle the event for extracting album art from a directory walk.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the album art extraction task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the top-level directory and validate it before extracting album art from a directory walk
        start_path = self.mainFrame.extractArtTld.GetValue().strip()

        # not a valid directory, return early
        if not self._validate_dir(start_path):
            return

        # get the file type pattern selection from the GUI
        selection = self.mainFrame.extractArtChoice.GetSelection()
        if selection == 0:
            pattern = None
        else:
            pattern = self.mainFrame.extractArtChoice.GetString(selection)

        self.mainFrame.taskRunner.run_task(self.art.extract_walk, start_path, pattern)


    def on_get_media_info_walk(self, event):
        '''
        @brief Handle the event for retrieving media information from a directory walk.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the media information retrieval task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the top-level directory and validate it before retrieving media information from a directory walk
        tld = self.mainFrame.media_info_tld.GetValue().strip()

        # not a valid directory, return early
        if not self._validate_dir(tld):
            return

        # get the file type pattern from the GUI
        pattern = None
        stripped_input = self.mainFrame.media_info_pattern.GetValue().strip()
        if stripped_input != "":
            pattern = stripped_input

        callback = self.mainFrame.show_generated_files
        self.mainFrame.taskRunner.run_task(self.metadata.get_media_info_walk, tld, pattern, on_success=callback)


    def on_get_tags_walk(self, event):
        '''
        @brief Handle the event for retrieving media tags from a directory walk.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the media tags retrieval task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the top-level directory and validate it before retrieving media tags from a directory walk
        tld = self.mainFrame.tags_walk_tld.GetValue().strip()

        # not a valid directory, return early
        if not self._validate_dir(tld):
            return

        # get the file type pattern and ffprobe path from the GUI
        pattern = None
        stripped_input = self.mainFrame.tags_walk_pattern.GetValue().strip()
        if stripped_input != "":
            pattern = stripped_input

        ffprobe = self.mainFrame.tags_walk_ffprobe.GetValue()

        callback = self.mainFrame.show_generated_files
        self.mainFrame.taskRunner.run_task(self.metadata.get_tags_walk, tld, pattern, ffprobe, on_success=callback)


    def on_get_unique_media(self, event):
        '''
        @brief Handle the event for retrieving unique media files from a directory walk.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the unique media retrieval task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the top-level directory and validate it before retrieving unique media files
        tld = self.mainFrame.unique_media_tld.GetValue().strip()

        # not a valid directory, return early
        if not self._validate_dir(tld):
            return

        callback = self.mainFrame.show_generated_files
        self.mainFrame.taskRunner.run_task(self.metadata.get_unique_media, tld, on_success=callback)


    def on_list_audio(self, event):
        '''
        @brief Handle the event for listing audio files in a directory.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the audio listing task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the top-level directory and validate it before listing audio files
        tld = self.mainFrame.list_audio_tld.GetValue().strip()

        # not a valid directory, return early
        if not self._validate_dir(tld):
            return

        callback = self.mainFrame.show_generated_files
        self.mainFrame.taskRunner.run_task(self.directory.list_audio, tld, on_success=callback)


    def on_list_type(self, event):
        '''
        @brief Handle the event for listing files of a specific type in a directory.

        @details Retrieves the top-level directory and file extension from the GUI, validates them, and then runs the file type listing task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the top-level directory and validate it before listing files of a specific type
        tld = self.mainFrame.list_type_tld.GetValue().strip()

        # not a valid directory, return early
        if not self._validate_dir(tld):
            return

        # get the file extension from the GUI and validate it before listing files of a specific type
        ext = self.mainFrame.list_type_ext.GetValue().strip()

        # not a valid file extension, return early
        if not ext:
            wx.MessageBox("Please enter a file extension", "Error", wx.ICON_ERROR)
            return

        callback = self.mainFrame.show_generated_files
        self.mainFrame.taskRunner.run_task(self.directory.list_type, tld, ext, on_success=callback)


    def on_level_directory_audio(self, event):
        '''
        @brief Handle the event for normalizing audio files in a directory walk.

        @details Retrieves the top-level directory and normalization type from the GUI, validates them, and then runs the normalization task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the top-level directory and validate it before normalizing audio files in a directory walk
        tld = self.mainFrame.norm_walk_tld.GetValue().strip()

        # not a valid directory, return early
        if not self._validate_dir(tld):
            return

        # get the normalization type from the GUI
        norm_type = self.mainFrame.norm_type_choice.GetStringSelection().lower()

        callback = self.mainFrame.show_generated_files
        self.mainFrame.taskRunner.run_task(self.normalization.normalize_walk, tld, norm_type, on_success=callback)


    def on_peak_file(self, event):
        '''
        @brief Handle the event for peak normalizing a single audio file.

        @details Retrieves the file path from the GUI, validates it, and then runs the peak normalization task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the result file.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the file path from the GUI and validate it before peak normalizing the audio file
        path = self.mainFrame.peak_file_path.GetValue().strip()

        # not a valid file, return early
        if not self._validate_file(path):
            return

        # define the callback function to display the result file after EBU normalization
        def callback():
            '''
            @brief Display the Peak normalization result file.

            @details Opens the result file after the peak normalization task succeeds.
            '''

            self.mainFrame._show_result_file("peak_normalize_file")

        self.mainFrame.taskRunner.run_task(self.normalization.peak_normalize_file, path, on_success=callback)


    def on_remove_albums(self, event):
        '''
        @brief Handle the event for removing albums from a directory.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the album removal task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the top-level directory and validate it before removing albums
        tld = self.mainFrame.remove_albums_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return

        callback = self.mainFrame.show_generated_files
        self.mainFrame.taskRunner.run_task(self.directory.remove_albums, tld, on_success=callback)


    def on_remove_pattern(self, event):
        '''
        @brief Handle the event for removing files matching a pattern from a directory.

        @details Retrieves the top-level directory and pattern from the GUI, validates them, and then runs the pattern removal task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the top-level directory and validate it before removing files matching a pattern
        tld = self.mainFrame.remove_pattern_tld.GetValue().strip()

        # not a valid directory, return early
        if not self._validate_dir(tld):
            return

        # get the pattern from the GUI and validate it before removing files matching a pattern
        pattern = self.mainFrame.remove_pattern_pattern.GetValue().strip()

        # not a valid pattern, return early
        if not pattern:
            wx.MessageBox("Please enter a pattern to remove", "Error", wx.ICON_ERROR)
            return

        callback = self.mainFrame.show_generated_files
        self.mainFrame.taskRunner.run_task(self.directory.remove_pattern, tld, pattern, on_success=callback)


    def on_rms_file(self, event):
        '''
        @brief Handle the event for RMS normalizing a single audio file.

        @details Retrieves the file path from the GUI, validates it, and then runs the RMS normalization task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the result file.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the file path from the GUI and validate it before RMS normalizing the audio file
        path = self.mainFrame.rms_file_path.GetValue().strip()

        # not a valid file, return early
        if not self._validate_file(path):
            return

        # define the callback function to display the result file after RMS normalization
        def callback():
            '''
            @brief Display the RMS normalization result file.

            @details Opens the result file after the normalization task succeeds.
            '''

            self.mainFrame._show_result_file("rms_normalize_file")

        self.mainFrame.taskRunner.run_task(self.normalization.rms_normalize_file, path, on_success=callback)


    def on_set_album_art(self, event):
        '''
        @brief Handle the event for setting album art for audio files in a directory.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the album art setting task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with the generated files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the top-level directory and validate it before setting album art for audio files in a directory
        tld = self.mainFrame.setArtTld.GetValue().strip()

        # not a valid directory, return early
        if not self._validate_dir(tld):
            return

        callback = self.mainFrame.show_generated_files
        self.mainFrame.taskRunner.run_task(self.art.set_album_art, tld, on_success=callback)


    def on_update_m3u(self, event):
        '''
        @brief Handle the event for updating an M3U playlist.

        @details Retrieves the M3U file path from the GUI, validates it, and then runs the playlist update task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with generated playlist files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the M3U file path from the GUI and validate it before updating the playlist
        m3u_file = self.mainFrame.update_m3u_file.GetValue().strip()

        # not a valid file, return early
        if not self._validate_file(m3u_file):
            return

        callback = self.mainFrame._show_generated_playlist_dialog
        self.mainFrame.taskRunner.run_task(self.playlist.update_playlist, m3u_file, on_success=callback)


    def on_update_walk(self, event):
        '''
        @brief Handle the event for updating a directory walk.

        @details Retrieves the top-level directory from the GUI, validates it, and then runs the directory walk update task.<br>
        The task is executed asynchronously, and upon success, a dialog is shown with generated playlist files.

        @param self {EventHandlers} The instance of the class the method belongs to.
        @param event {object} The event object.
        '''

        # get the top-level directory from the GUI and validate it before updating a directory walk
        tld = self.mainFrame.bulk_tld.GetValue().strip()

        # not a valid directory, return early
        if not self._validate_dir(tld):
            return

        callback = self.mainFrame._show_generated_playlist_dialog
        self.mainFrame.taskRunner.run_task(self.playlist.update_walk, tld, on_success=callback)
