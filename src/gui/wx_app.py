import datetime
import os
import shutil
import threading

import wx

from src.audio_info import AudioArt, AudioMetadata, AudioPlaylist
from src.audio_normalize import AudioNormalization
from src.dir_processing import DirectoryProcessing
from src.generated_files import GENERATED_PATH
from src import MUSIC_TLD, AUDIO_EXTS

metadata = AudioMetadata()
art = AudioArt()
normalization = AudioNormalization()
directory = DirectoryProcessing()
playlist = AudioPlaylist()


def _timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class MainFrame(wx.Frame):
    def __init__(self, parent=None):
        super().__init__(parent, title="MusicProcessing GUI", size=(960, 760))

        self.panel = wx.Panel(self)

        # Create splitter window for resizable notebook/log split
        self.splitter = wx.SplitterWindow(self.panel, style=wx.SP_LIVE_UPDATE)

        self.notebook = wx.Notebook(self.splitter)

        self.art_panel = self._make_art_panel(self.notebook)
        self.convert_panel = self._make_convert_panel(self.notebook)
        self.normalize_panel = self._make_normalize_panel(self.notebook)
        self.metadata_panel = self._make_metadata_panel(self.notebook)

        self.dir_panel = self._make_directory_panel(self.notebook)
        self.playlist_panel = self._make_playlist_panel(self.notebook)

        self.notebook.AddPage(self.art_panel, "Art")
        self.notebook.AddPage(self.convert_panel, "Convert")
        self.notebook.AddPage(self.normalize_panel, "Normalize")
        self.notebook.AddPage(self.playlist_panel, "Playlist")
        self.notebook.AddPage(self.metadata_panel, "Metadata")
        self.notebook.AddPage(self.dir_panel, "Directory")

        self.log_ctrl = wx.TextCtrl(
            self.splitter,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
            value="",
        )

        # Split horizontally: notebook on top, log on bottom
        self.splitter.SplitHorizontally(self.notebook, self.log_ctrl)
        self.splitter.SetSashPosition(550)  # Initial sash position in pixels from top

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.splitter, 1, wx.EXPAND)
        self.panel.SetSizer(main_sizer)
        self.Maximize()

    def _make_path_controls(self, parent):
        textbox = wx.TextCtrl(parent)
        textbox.SetToolTip("Enter path or click Browse button")
        button = wx.Button(parent, label="Browse")
        button.SetToolTip("Browse for a path")
        return textbox, button

    def _make_convert_panel(self, parent):
        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        # convert file
        self.convert_file_path, convert_file_btn = self._make_path_controls(panel)
        convert_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_file(evt, self.convert_file_path, "Audio files (*.mp3;*.m4a;*.wma)|*.mp3;*.m4a;*.wma"))
        convert_file_exec = wx.Button(panel, label="Convert File")
        convert_file_exec.Bind(wx.EVT_BUTTON, self.on_convert_file)

        # convert walk
        self.convert_walk_tld, convert_walk_tld_btn = self._make_path_controls(panel)
        convert_walk_tld_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_dir(evt, self.convert_walk_tld))
        pattern_choices = ["Any file type"] + AUDIO_EXTS
        self.convert_walk_pattern = wx.Choice(panel, choices=pattern_choices)
        self.convert_walk_pattern.SetSelection(0)  # Default to "Any file type"
        self.convert_walk_pattern.SetToolTip("Select file type pattern or 'Any file type' to process all supported audio files")
        pattern_label = wx.StaticText(panel, label="Pattern (optional):")
        convert_walk_exec = wx.Button(panel, label="Convert Walk")
        convert_walk_exec.Bind(wx.EVT_BUTTON, self.on_convert_walk)

        grid.Add(wx.StaticText(panel, label="Audio file to convert:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.convert_file_path, pos=(0, 1), flag=wx.EXPAND)
        grid.Add(convert_file_btn, pos=(0, 2))
        grid.Add(convert_file_exec, pos=(0, 3))

        grid.Add(wx.StaticText(panel, label="Top-level dir (convert walk):"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.convert_walk_tld, pos=(1, 1), flag=wx.EXPAND)
        grid.Add(convert_walk_tld_btn, pos=(1, 2))

        grid.Add(pattern_label, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.convert_walk_pattern, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        grid.Add(convert_walk_exec, pos=(2, 3))

        grid.AddGrowableCol(1)

        panel.SetSizer(grid)
        return panel

    def _make_normalize_panel(self, parent):
        panel = wx.Panel(parent)

        # Nested subpanel for normalize-walk options
        normalize_box = wx.StaticBox(panel, label="Normalize Walk Options")
        normalize_sizer = wx.StaticBoxSizer(normalize_box, wx.VERTICAL)
        normalize_subpanel = wx.Panel(panel)
        normalize_grid = wx.GridBagSizer(8, 8)

        self.norm_walk_tld, norm_walk_tld_btn = self._make_path_controls(normalize_subpanel)
        norm_walk_tld_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_dir(evt, self.norm_walk_tld))
        self.norm_type_choice = wx.Choice(normalize_subpanel, choices=["ebu", "peak", "rms"])
        self.norm_type_choice.SetSelection(0)
        self.norm_type_choice.SetToolTip("Select normalization type: ebu (loudness), peak (peak level), or rms (RMS level)")
        norm_walk_exec = wx.Button(normalize_subpanel, label="Normalize Walk")
        norm_walk_exec.Bind(wx.EVT_BUTTON, self.on_normalize_walk)

        normalize_grid.Add(wx.StaticText(normalize_subpanel, label="Top-level dir (normalize walk):"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        normalize_grid.Add(self.norm_walk_tld, pos=(0, 1), flag=wx.EXPAND)
        normalize_grid.Add(norm_walk_tld_btn, pos=(0, 2))
        normalize_grid.Add(wx.StaticText(normalize_subpanel, label="Type:"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        normalize_grid.Add(self.norm_type_choice, pos=(1, 1), flag=wx.EXPAND)
        normalize_grid.Add(norm_walk_exec, pos=(1, 2))

        normalize_grid.AddGrowableCol(1)
        normalize_subpanel.SetSizer(normalize_grid)
        normalize_sizer.Add(normalize_subpanel, 1, wx.EXPAND | wx.ALL, 4)

        grid = wx.GridBagSizer(8, 8)
        grid.Add(normalize_sizer, pos=(0, 0), span=(1, 4), flag=wx.EXPAND | wx.ALL, border=4)

        # Specific normalizations nested subpanel
        specific_box = wx.StaticBox(panel, label="Specific Normalizations")
        specific_sizer = wx.StaticBoxSizer(specific_box, wx.VERTICAL)
        specific_subpanel = wx.Panel(panel)
        specific_grid = wx.GridBagSizer(8, 8)

        self.ebu_file_path, ebu_file_btn = self._make_path_controls(specific_subpanel)
        ebu_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_file(evt, self.ebu_file_path))
        ebu_file_exec = wx.Button(specific_subpanel, label="EBU File")
        ebu_file_exec.Bind(wx.EVT_BUTTON, self.on_ebu_file)

        self.peak_file_path, peak_file_btn = self._make_path_controls(specific_subpanel)
        peak_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_file(evt, self.peak_file_path))
        peak_file_exec = wx.Button(specific_subpanel, label="Peak File")
        peak_file_exec.Bind(wx.EVT_BUTTON, self.on_peak_file)

        self.rms_file_path, rms_file_btn = self._make_path_controls(specific_subpanel)
        rms_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_file(evt, self.rms_file_path))
        rms_file_exec = wx.Button(specific_subpanel, label="RMS File")
        rms_file_exec.Bind(wx.EVT_BUTTON, self.on_rms_file)

        specific_grid.Add(wx.StaticText(specific_subpanel, label="EBU file:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        specific_grid.Add(self.ebu_file_path, pos=(0, 1), flag=wx.EXPAND)
        specific_grid.Add(ebu_file_btn, pos=(0, 2))
        specific_grid.Add(ebu_file_exec, pos=(0, 3))

        specific_grid.Add(wx.StaticText(specific_subpanel, label="Peak file:"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        specific_grid.Add(self.peak_file_path, pos=(1, 1), flag=wx.EXPAND)
        specific_grid.Add(peak_file_btn, pos=(1, 2))
        specific_grid.Add(peak_file_exec, pos=(1, 3))

        specific_grid.Add(wx.StaticText(specific_subpanel, label="RMS file:"), pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        specific_grid.Add(self.rms_file_path, pos=(2, 1), flag=wx.EXPAND)
        specific_grid.Add(rms_file_btn, pos=(2, 2))
        specific_grid.Add(rms_file_exec, pos=(2, 3))

        specific_grid.AddGrowableCol(1)
        specific_subpanel.SetSizer(specific_grid)
        specific_sizer.Add(specific_subpanel, 1, wx.EXPAND | wx.ALL, 4)

        grid.Add(specific_sizer, pos=(1, 0), span=(1, 4), flag=wx.EXPAND | wx.ALL, border=4)

        grid.AddGrowableCol(1)
        panel.SetSizer(grid)
        return panel

        grid.AddGrowableCol(1)
        panel.SetSizer(grid)
        return panel

        grid.Add(wx.StaticText(panel, label="EBU file:"), pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.ebu_file_path, pos=(2, 1), flag=wx.EXPAND)
        grid.Add(ebu_file_btn, pos=(2, 2))
        grid.Add(ebu_file_exec, pos=(2, 3))

        grid.Add(wx.StaticText(panel, label="Peak file:"), pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.peak_file_path, pos=(3, 1), flag=wx.EXPAND)
        grid.Add(peak_file_btn, pos=(3, 2))
        grid.Add(peak_file_exec, pos=(3, 3))

        grid.Add(wx.StaticText(panel, label="RMS file:"), pos=(4, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.rms_file_path, pos=(4, 1), flag=wx.EXPAND)
        grid.Add(rms_file_btn, pos=(4, 2))
        grid.Add(rms_file_exec, pos=(4, 3))

        grid.AddGrowableCol(1)
        panel.SetSizer(grid)

        return panel

    def _make_metadata_panel(self, parent):
        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        self.tags_walk_tld, tags_walk_tld_btn = self._make_path_controls(panel)
        tags_walk_tld_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_dir(evt, self.tags_walk_tld))
        self.tags_walk_pattern = wx.TextCtrl(panel)
        self.tags_walk_ffprobe = wx.CheckBox(panel, label="Use ffprobe")
        tags_walk_exec = wx.Button(panel, label="Get Tags Walk")
        tags_walk_exec.Bind(wx.EVT_BUTTON, self.on_get_tags_walk)

        self.media_info_tld, media_info_btn = self._make_path_controls(panel)
        media_info_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_dir(evt, self.media_info_tld))
        self.media_info_pattern = wx.TextCtrl(panel)
        media_info_exec = wx.Button(panel, label="Get Media Info Walk")
        media_info_exec.Bind(wx.EVT_BUTTON, self.on_get_media_info_walk)

        self.unique_media_tld, unique_media_btn = self._make_path_controls(panel)
        unique_media_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_dir(evt, self.unique_media_tld))
        unique_media_exec = wx.Button(panel, label="Get Unique Media")
        unique_media_exec.Bind(wx.EVT_BUTTON, self.on_get_unique_media)

        grid.Add(wx.StaticText(panel, label="Top-level dir (tags walk):"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.tags_walk_tld, pos=(0, 1), flag=wx.EXPAND)
        grid.Add(tags_walk_tld_btn, pos=(0, 2))
        grid.Add(wx.StaticText(panel, label="Pattern:"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.tags_walk_pattern, pos=(1, 1), span=(1, 2), flag=wx.EXPAND)
        grid.Add(self.tags_walk_ffprobe, pos=(2, 1))
        grid.Add(tags_walk_exec, pos=(2, 2))

        grid.Add(wx.StaticText(panel, label="Top-level dir (media info walk):"), pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.media_info_tld, pos=(3, 1), flag=wx.EXPAND)
        grid.Add(media_info_btn, pos=(3, 2))
        grid.Add(wx.StaticText(panel, label="Pattern:"), pos=(4, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.media_info_pattern, pos=(4, 1), span=(1, 2), flag=wx.EXPAND)
        grid.Add(media_info_exec, pos=(4, 3))

        grid.Add(wx.StaticText(panel, label="Top-level dir (unique media):"), pos=(5, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.unique_media_tld, pos=(5, 1), flag=wx.EXPAND)
        grid.Add(unique_media_btn, pos=(5, 2))
        grid.Add(unique_media_exec, pos=(5, 3))

        grid.AddGrowableCol(1)
        panel.SetSizer(grid)
        return panel

    def _make_art_panel(self, parent):
        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        self.extract_file_art_path, extract_file_art_btn = self._make_path_controls(panel)
        extract_file_art_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_file(evt, self.extract_file_art_path, "Audio files (*.mp3;*.m4a;*.wma)|*.mp3;*.m4a;*.wma"))
        extract_file_art_exec = wx.Button(panel, label="Extract File Art")
        extract_file_art_exec.Bind(wx.EVT_BUTTON, self.on_extract_file_art)

        self.extract_walk_art_tld, extract_walk_art_btn = self._make_path_controls(panel)
        extract_walk_art_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_dir(evt, self.extract_walk_art_tld))
        pattern_choices = ["Any file type"] + AUDIO_EXTS
        self.extract_walk_art_pattern = wx.Choice(panel, choices=pattern_choices)
        self.extract_walk_art_pattern.SetSelection(0)  # Default to "Any file type"
        self.extract_walk_art_pattern.SetToolTip("Select file type pattern or 'Any file type' to process all supported audio files")
        extract_walk_art_exec = wx.Button(panel, label="Extract Walk Art")
        extract_walk_art_exec.Bind(wx.EVT_BUTTON, self.on_extract_walk_art)

        self.set_album_art_tld, set_album_art_btn = self._make_path_controls(panel)
        set_album_art_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_dir(evt, self.set_album_art_tld))
        set_album_art_exec = wx.Button(panel, label="Set Album Art")
        set_album_art_exec.Bind(wx.EVT_BUTTON, self.on_set_album_art)

        grid.Add(wx.StaticText(panel, label="Audio file (extract art):"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.extract_file_art_path, pos=(0, 1), flag=wx.EXPAND)
        grid.Add(extract_file_art_btn, pos=(0, 2))
        grid.Add(extract_file_art_exec, pos=(0, 3))

        grid.Add(wx.StaticText(panel, label="Top-level dir (extract walk):"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.extract_walk_art_tld, pos=(1, 1), flag=wx.EXPAND)
        grid.Add(extract_walk_art_btn, pos=(1, 2))
        grid.Add(wx.StaticText(panel, label="Pattern (optional):"), pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.extract_walk_art_pattern, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        grid.Add(extract_walk_art_exec, pos=(2, 3))

        grid.Add(wx.StaticText(panel, label="Top-level dir (set art):"), pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.set_album_art_tld, pos=(3, 1), flag=wx.EXPAND)
        grid.Add(set_album_art_btn, pos=(3, 2))
        grid.Add(set_album_art_exec, pos=(3, 3))

        grid.AddGrowableCol(1)
        panel.SetSizer(grid)
        return panel

    def _make_directory_panel(self, parent):
        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        self.list_audio_tld, list_audio_btn = self._make_path_controls(panel)
        list_audio_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_dir(evt, self.list_audio_tld))
        list_audio_exec = wx.Button(panel, label="List Audio")
        list_audio_exec.Bind(wx.EVT_BUTTON, self.on_list_audio)

        self.list_type_tld, list_type_btn = self._make_path_controls(panel)
        list_type_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_dir(evt, self.list_type_tld))
        self.list_type_ext = wx.TextCtrl(panel)
        list_type_exec = wx.Button(panel, label="List Type")
        list_type_exec.Bind(wx.EVT_BUTTON, self.on_list_type)

        self.remove_albums_tld, remove_albums_btn = self._make_path_controls(panel)
        remove_albums_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_dir(evt, self.remove_albums_tld))
        remove_albums_exec = wx.Button(panel, label="Remove Empty Albums")
        remove_albums_exec.Bind(wx.EVT_BUTTON, self.on_remove_albums)

        self.remove_pattern_tld, remove_pattern_btn = self._make_path_controls(panel)
        remove_pattern_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_dir(evt, self.remove_pattern_tld))
        self.remove_pattern_pattern = wx.TextCtrl(panel)
        remove_pattern_exec = wx.Button(panel, label="Remove Pattern")
        remove_pattern_exec.Bind(wx.EVT_BUTTON, self.on_remove_pattern)

        grid.Add(wx.StaticText(panel, label="Top-level dir (list audio):"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.list_audio_tld, pos=(0, 1), flag=wx.EXPAND)
        grid.Add(list_audio_btn, pos=(0, 2))
        grid.Add(list_audio_exec, pos=(0, 3))

        grid.Add(wx.StaticText(panel, label="Top-level dir (list type):"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.list_type_tld, pos=(1, 1), flag=wx.EXPAND)
        grid.Add(list_type_btn, pos=(1, 2))
        grid.Add(wx.StaticText(panel, label="Ext (e.g. mp3):"), pos=(1, 4), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.list_type_ext, pos=(1, 5))
        grid.Add(list_type_exec, pos=(1, 6))

        grid.Add(self.remove_albums_tld, pos=(2, 1), flag=wx.EXPAND)
        grid.Add(remove_albums_btn, pos=(2, 2))
        grid.Add(remove_albums_exec, pos=(2, 3))

        grid.Add(self.remove_pattern_tld, pos=(3, 1), flag=wx.EXPAND)
        grid.Add(remove_pattern_btn, pos=(3, 2))
        grid.Add(wx.StaticText(panel, label="Pattern:"), pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.remove_pattern_pattern, pos=(3, 3), span=(1, 2), flag=wx.EXPAND)
        grid.Add(remove_pattern_exec, pos=(3, 5))

        grid.AddGrowableCol(1)
        panel.SetSizer(grid)
        return panel

    def _make_playlist_panel(self, parent):
        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        self.update_m3u_tld, update_m3u_btn = self._make_path_controls(panel)
        update_m3u_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_dir(evt, self.update_m3u_tld))
        self.update_m3u_file, update_m3u_file_btn = self._make_path_controls(panel)
        update_m3u_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_file(evt, self.update_m3u_file))
        update_m3u_exec = wx.Button(panel, label="Update M3U")
        update_m3u_exec.Bind(wx.EVT_BUTTON, self.on_update_m3u)

        self.update_walk_tld, update_walk_btn = self._make_path_controls(panel)
        update_walk_btn.Bind(wx.EVT_BUTTON, lambda evt: self.on_browse_dir(evt, self.update_walk_tld))
        update_walk_exec = wx.Button(panel, label="Update Walk")
        update_walk_exec.Bind(wx.EVT_BUTTON, self.on_update_walk)

        grid.Add(wx.StaticText(panel, label="Top-level dir (update m3u):"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.update_m3u_tld, pos=(0, 1), flag=wx.EXPAND)
        grid.Add(update_m3u_btn, pos=(0, 2))
        grid.Add(wx.StaticText(panel, label="Playlist file (.m3u):"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.update_m3u_file, pos=(1, 1), flag=wx.EXPAND)
        grid.Add(update_m3u_file_btn, pos=(1, 2))
        grid.Add(update_m3u_exec, pos=(1, 3))

        grid.Add(wx.StaticText(panel, label="Top-level dir (update walk):"), pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.update_walk_tld, pos=(2, 1), flag=wx.EXPAND)
        grid.Add(update_walk_btn, pos=(2, 2))
        grid.Add(update_walk_exec, pos=(2, 3))

        grid.AddGrowableCol(1)
        panel.SetSizer(grid)
        return panel

    def on_browse_file(self, event, textctrl, wildcard=None):
        dlg = wx.FileDialog(self, "Select file", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST, wildcard=wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            textctrl.SetValue(path)
        dlg.Destroy()

    def on_browse_dir(self, event, textctrl):
        dlg = wx.DirDialog(self, "Select directory", style=wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            textctrl.SetValue(path)
        dlg.Destroy()

    def log(self, message):
        wx.CallAfter(self.log_ctrl.AppendText, f"[{_timestamp()}] {message}\n")

    def run_task(self, func, *args, on_success=None):
        def worker():
            self.log(f"Running {func.__name__}...")
            try:
                func(*args)
                self.log(f"{func.__name__} completed.")
                if on_success:
                    wx.CallAfter(on_success)
            except Exception as e:
                self.log(f"{func.__name__} failed: {e}")
                wx.CallAfter(wx.MessageBox, str(e), "Error", wx.ICON_ERROR)
            finally:
                wx.CallAfter(self.Enable, True)

        self.Enable(False)
        threading.Thread(target=worker, daemon=True).start()

    def _validate_file(self, path):
        if not path:
            wx.MessageBox("Please specify a file path.", "Validation", wx.ICON_WARNING)
            return False
        if not os.path.isfile(path):
            wx.MessageBox(f"File not found: {path}", "Validation", wx.ICON_ERROR)
            return False
        return True

    def _validate_dir(self, path):
        if not path:
            wx.MessageBox("Please specify a directory path.", "Validation", wx.ICON_WARNING)
            return False
        if not os.path.isdir(path):
            wx.MessageBox(f"Directory not found: {path}", "Validation", wx.ICON_ERROR)
            return False
        return True

    def _show_generated_files_dialog(self):
        generated_dir = os.path.join(GENERATED_PATH, MUSIC_TLD)
        if not os.path.isdir(generated_dir):
            wx.MessageBox(
                f"Generated files directory not found: {generated_dir}",
                "Info",
                wx.ICON_INFORMATION,
            )
            return

        dlg = wx.FileDialog(
            self,
            "Select MP3 files to move (generated files):",
            defaultDir=generated_dir,
            wildcard="MP3 files (*.mp3)|*.mp3|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR,
        )

        if dlg.ShowModal() == wx.ID_OK:
            selected_files = dlg.GetPaths()
            if selected_files:
                self._move_files_dialog(selected_files)
        dlg.Destroy()

    def _move_files_dialog(self, file_paths):
        dest_dlg = wx.DirDialog(
            self,
            "Select destination directory to move files to:",
            style=wx.DD_DIR_MUST_EXIST,
        )

        if dest_dlg.ShowModal() == wx.ID_OK:
            dest_dir = dest_dlg.GetPath()
            self._move_files(file_paths, dest_dir)
        dest_dlg.Destroy()

    def _move_files(self, file_paths, dest_dir):
        moved = []
        failed = []

        for src_file in file_paths:
            try:
                dest_file = os.path.join(dest_dir, os.path.basename(src_file))
                shutil.move(src_file, dest_file)
                moved.append(os.path.basename(src_file))
            except Exception as e:
                failed.append(f"{os.path.basename(src_file)}: {e}")

        message = f"Moved {len(moved)} file(s)"
        if moved:
            message += f": {', '.join(moved[:3])}" + ("..." if len(moved) > 3 else "")
        if failed:
            message += f"\n\nFailed ({len(failed)}):\n" + "\n".join(failed[:5]) + (
                "\n..." if len(failed) > 5 else ""
            )
        wx.MessageBox(message, "Move Summary", wx.ICON_INFORMATION)

    def on_convert_file(self, event):
        path = self.convert_file_path.GetValue().strip()
        if not self._validate_file(path):
            return
        self.run_task(metadata.convert_file, path, on_success=self._show_generated_files_dialog)

    def on_convert_walk(self, event):
        tld = self.convert_walk_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return
        selection = self.convert_walk_pattern.GetSelection()
        pattern = None if selection == 0 else self.convert_walk_pattern.GetString(selection)
        self.run_task(metadata.convert_walk, tld, pattern, on_success=self._show_generated_files_dialog)

    def on_normalize_walk(self, event):
        tld = self.norm_walk_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return
        norm_type = self.norm_type_choice.GetStringSelection().lower()
        self.run_task(normalization.normalize_walk, tld, norm_type, on_success=self._show_generated_files_dialog)

    def on_ebu_file(self, event):
        path = self.ebu_file_path.GetValue().strip()
        if not self._validate_file(path):
            return
        self.run_task(normalization.ebu_normalize_file, path, on_success=self._show_generated_files_dialog)

    def on_peak_file(self, event):
        path = self.peak_file_path.GetValue().strip()
        if not self._validate_file(path):
            return
        self.run_task(normalization.peak_normalize_file, path, on_success=self._show_generated_files_dialog)

    def on_rms_file(self, event):
        path = self.rms_file_path.GetValue().strip()
        if not self._validate_file(path):
            return
        self.run_task(normalization.rms_normalize_file, path, on_success=self._show_generated_files_dialog)

    def on_get_tags_walk(self, event):
        tld = self.tags_walk_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return
        pattern = self.tags_walk_pattern.GetValue().strip() or None
        ffprobe = self.tags_walk_ffprobe.GetValue()
        self.run_task(metadata.get_tags_walk, tld, pattern, ffprobe)

    def on_get_media_info_walk(self, event):
        tld = self.media_info_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return
        pattern = self.media_info_pattern.GetValue().strip() or None
        self.run_task(metadata.get_media_info_walk, tld, pattern)

    def on_get_unique_media(self, event):
        tld = self.unique_media_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return
        self.run_task(metadata.get_unique_media_keys, tld)

    def on_extract_file_art(self, event):
        path = self.extract_file_art_path.GetValue().strip()
        if not self._validate_file(path):
            return
        self.run_task(art.extract_album_art, path)

    def on_extract_walk_art(self, event):
        tld = self.extract_walk_art_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return
        selection = self.extract_walk_art_pattern.GetSelection()
        pattern = None if selection == 0 else self.extract_walk_art_pattern.GetString(selection)
        self.run_task(art.extract_walk, tld, pattern)

    def on_set_album_art(self, event):
        tld = self.set_album_art_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return
        self.run_task(art.set_album_art, tld)

    def on_list_audio(self, event):
        tld = self.list_audio_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return
        self.run_task(directory.get_audio_file_list, tld)

    def on_list_type(self, event):
        tld = self.list_type_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return
        ext = self.list_type_ext.GetValue().strip() or None
        self.run_task(directory.get_ext_file_list, ext, tld)

    def on_remove_albums(self, event):
        tld = self.remove_albums_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return
        self.run_task(directory.remove_empty_album_dir, tld)

    def on_remove_pattern(self, event):
        tld = self.remove_pattern_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return
        pattern = self.remove_pattern_pattern.GetValue().strip()
        if not pattern:
            wx.MessageBox("Please specify a pattern.", "Validation", wx.ICON_WARNING)
            return
        self.run_task(directory.remove_pattern, tld, pattern)

    def on_update_m3u(self, event):
        tld = self.update_m3u_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return
        m3u = self.update_m3u_file.GetValue().strip()
        if not self._validate_file(m3u):
            return
        self.run_task(playlist.update_paths, tld, m3u)

    def on_update_walk(self, event):
        tld = self.update_walk_tld.GetValue().strip()
        if not self._validate_dir(tld):
            return
        self.run_task(playlist.update_walk, tld)


def run_gui():
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
