"""
@file handlers.py
@brief Event handlers for the wxPython GUI application.
"""

import wx

from src.audio_info import AudioArt, AudioMetadata, AudioPlaylist
from src.audio_normalize import AudioNormalization
from src.dir_processing import DirectoryProcessing

# Import modules for handlers
metadata = AudioMetadata()
art = AudioArt()
normalization = AudioNormalization()
directory = DirectoryProcessing()
playlist = AudioPlaylist()


class EventHandlers:
    """Event handlers for the GUI application."""

    def __init__(self, main_frame):
        self.frame = main_frame

    def on_browse_file(self, event, textctrl, wildcard=None):
        if wildcard is None:
            wildcard = ""
        dlg = wx.FileDialog(self.frame, "Select file", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST, wildcard=wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            textctrl.SetValue(path)
            textctrl.SetFocus()
        dlg.Destroy()

    def on_browse_dir(self, event, textctrl):
        dlg = wx.DirDialog(self.frame, "Select directory", style=wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            textctrl.SetValue(path)
            textctrl.SetFocus()
        dlg.Destroy()

    def on_convert_file(self, event):
        path = self.frame.convert_file_path.GetValue().strip()
        if not self.frame._validate_file(path):
            return
        self.frame.run_task(metadata.convert_file, path, on_success=self.frame._show_generated_files_dialog)

    def on_convert_walk(self, event):
        tld = self.frame.convert_walk_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return
        selection = self.frame.convert_walk_pattern.GetSelection()
        pattern = None if selection == 0 else self.frame.convert_walk_pattern.GetString(selection)
        self.frame.run_task(metadata.convert_walk, tld, pattern, on_success=self.frame._show_generated_files_dialog)

    def on_normalize_walk(self, event):
        tld = self.frame.norm_walk_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return
        norm_type = self.frame.norm_type_choice.GetStringSelection().lower()
        self.frame.run_task(normalization.normalize_walk, tld, norm_type, on_success=self.frame._show_generated_files_dialog)

    def on_ebu_file(self, event):
        path = self.frame.ebu_file_path.GetValue().strip()
        if not self.frame._validate_file(path):
            return
        self.frame.run_task(normalization.ebu_normalize_file, path, on_success=lambda: self.frame._show_result_file("ebu_normalize_file"))

    def on_peak_file(self, event):
        path = self.frame.peak_file_path.GetValue().strip()
        if not self.frame._validate_file(path):
            return
        self.frame.run_task(normalization.peak_normalize_file, path, on_success=lambda: self.frame._show_result_file("peak_normalize_file"))

    def on_rms_file(self, event):
        path = self.frame.rms_file_path.GetValue().strip()
        if not self.frame._validate_file(path):
            return
        self.frame.run_task(normalization.rms_normalize_file, path, on_success=lambda: self.frame._show_result_file("rms_normalize_file"))

    def on_get_tags_walk(self, event):
        tld = self.frame.tags_walk_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return
        pattern = self.frame.tags_walk_pattern.GetValue().strip() or None
        ffprobe = self.frame.tags_walk_ffprobe.GetValue()
        self.frame.run_task(metadata.get_tags_walk, tld, pattern, ffprobe, on_success=self.frame._show_generated_files_dialog)

    def on_get_media_info_walk(self, event):
        tld = self.frame.media_info_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return
        pattern = self.frame.media_info_pattern.GetValue().strip() or None
        self.frame.run_task(metadata.get_media_info_walk, tld, pattern, on_success=self.frame._show_generated_files_dialog)

    def on_get_unique_media(self, event):
        tld = self.frame.unique_media_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return
        self.frame.run_task(metadata.get_unique_media, tld, on_success=self.frame._show_generated_files_dialog)

    def on_extract_file_art(self, event):
        path = self.frame.extract_file_art_path.GetValue().strip()
        if not self.frame._validate_file(path):
            return
        self.frame.run_task(art.extract_album_art, path, on_success=self.frame._show_generated_files_dialog)

    def on_extract_walk_art(self, event):
        tld = self.frame.extract_walk_art_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return
        selection = self.frame.extract_walk_art_pattern.GetSelection()
        pattern = None if selection == 0 else self.frame.extract_walk_art_pattern.GetString(selection)
        self.frame.run_task(art.extract_walk, tld, pattern, on_success=self.frame._show_generated_files_dialog)

    def on_set_album_art(self, event):
        tld = self.frame.set_album_art_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return
        self.frame.run_task(art.set_album_art, tld, on_success=self.frame._show_generated_files_dialog)

    def on_list_audio(self, event):
        tld = self.frame.list_audio_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return
        self.frame.run_task(directory.list_audio, tld, on_success=self.frame._show_generated_files_dialog)

    def on_list_type(self, event):
        tld = self.frame.list_type_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return
        ext = self.frame.list_type_ext.GetValue().strip()
        if not ext:
            wx.MessageBox("Please enter a file extension", "Error", wx.ICON_ERROR)
            return
        self.frame.run_task(directory.list_type, tld, ext, on_success=self.frame._show_generated_files_dialog)

    def on_remove_albums(self, event):
        tld = self.frame.remove_albums_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return
        self.frame.run_task(directory.remove_albums, tld, on_success=self.frame._show_generated_files_dialog)

    def on_remove_pattern(self, event):
        tld = self.frame.remove_pattern_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return
        pattern = self.frame.remove_pattern_pattern.GetValue().strip()
        if not pattern:
            wx.MessageBox("Please enter a pattern to remove", "Error", wx.ICON_ERROR)
            return
        self.frame.run_task(directory.remove_pattern, tld, pattern, on_success=self.frame._show_generated_files_dialog)

    def on_update_m3u(self, event):
        m3u_file = self.frame.update_m3u_file.GetValue().strip()
        if not self.frame._validate_file(m3u_file):
            return
        self.frame.run_task(playlist.update_playlist, m3u_file, on_success=self.frame._show_generated_files_dialog)

    def on_update_walk(self, event):
        tld = self.frame.update_walk_tld.GetValue().strip()
        if not self.frame._validate_dir(tld):
            return
        self.frame.run_task(playlist.update_walk, tld, on_success=self.frame._show_generated_files_dialog)
