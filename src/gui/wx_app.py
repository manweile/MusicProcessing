'''
@file wx_app.py
@brief Defines the main GUI application using wxPython.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import logging                                              # for logging
import os                                                   # for operating system interfaces
import shutil                                               # for high-level file operations
import threading                                            # for multithreading support
from datetime import datetime                               # for handling date and time

# Third Party Modules
import wx                                                   # for wxPython GUI components

# Local Module Methods
from src import add_module_handler                          # for adding module-specific logging handlers

# Local Module Constants
from src import AUDIO_EXTS                                  # for audio file extensions
from src import MUSIC_TLD                                   # top level directory for music files
from src import PLAYLIST_EXTS                               # supported playlist file extensions
from src import RESULT_DIR                                  # directory for storing test results
from src import RESULT_EXT                                  # file extension for result files
from src.generated_files import GENERATED_PATH              # for generated files path

# Local Module Classes
from src.gui.handlers import EventHandlers

## @var logger
# @brief Logger instance for the module.
# @details Sets the logger name to the current module name.
logger = logging.getLogger(__name__)

## @var basename
# @brief Base name for the logger file handler.
# @details Gets the module file name from the current file path.
basename = os.path.basename(__file__)

add_module_handler(logger, basename)


## @name Helper Functions
# @{
def _timestamp() -> str:
    '''
    @brief Get the current timestamp as a string.

    @details This function is used for generating unique result file names based on the current date and time.

    @return time_stamp {str}A string representing the current timestamp in the format "YYYY-MM-DD HH:MM:SS".
    '''

    try:
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return time_stamp

    except Exception as e_error:
        logger.exception(f"Exception {type(e_error).__name__} getting timestamp", stack_info=True)
        raise e_error
## @}


class MainFrame(wx.Frame):
    '''
    @brief Main frame for the MusicProcessing GUI application.

    @details This class defines the main window of the application, including the layout, panels, and event handlers.
    '''

    def __init__(self, parent=None) -> None:
        '''
        @brief Initialize the MainFrame class.

        @details This constructor sets up the main window, including the layout, panels, and event handlers.

        @param self {MainFrame} The instance of the class.
        @param parent {any} The parent window, if any.
        '''

        # Initialize the main frame with the specified parent, title, and size
        super().__init__(parent, title="Music Processing GUI", size=(960, 760))

        # Increase font size by 2 points
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(font.GetPointSize() + 2)
        self.SetFont(font)

        # Create the main panel within the frame
        self.panel = wx.Panel(self)
        self.panel.SetFont(font)

        # Create splitter window for resizable notebook/log split
        self.splitter = wx.SplitterWindow(self.panel, style=wx.SP_LIVE_UPDATE)

        # Create the notebook for tabbed panels within the splitter window
        self.notebook = wx.Notebook(self.splitter)

        # Initialize event handlers
        self.handlers = EventHandlers(self)

        # Create the individual panels for each tab in the notebook
        self.panel_art = self._panel_art(self.notebook)
        self.panel_convert = self._panel_convert(self.notebook)
        self.panel_leveling = self._panel_leveling(self.notebook)
        self.panel_playlist = self._panel_playlist(self.notebook)
        self.panel_metadata = self._panel_metadata(self.notebook)
        self.panel_directory = self._panel_directory(self.notebook)

        # Add the created panels to the notebook as separate tabs
        self.notebook.AddPage(self.panel_art, "Art")
        self.notebook.AddPage(self.panel_convert, "Convert")
        self.notebook.AddPage(self.panel_leveling, "Normalize")
        self.notebook.AddPage(self.panel_playlist, "Playlist")
        self.notebook.AddPage(self.panel_metadata, "Metadata")
        self.notebook.AddPage(self.panel_directory, "Directory")

        # Create the log control for displaying log messages
        self.log_ctrl = wx.TextCtrl(self.splitter, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL, value="")

        # Split horizontally: notebook on top, log on bottom
        self.splitter.SplitHorizontally(self.notebook, self.log_ctrl)
        self.splitter.SetSashPosition(550)  # Initial sash position in pixels from top

        # Set up the main sizer for the panel and add the splitter window to it
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.splitter, 1, wx.EXPAND)
        self.panel.SetSizer(main_sizer)
        self.Maximize()


    def _panel_art(self, parent) -> wx.Panel:
        '''
        @brief This panel contains album art extraction and setting controls.

        @details Stacks the extraction sections at left and places the setting section to their right.

        @param self {MainFrame} The instance of the class.
        @param parent {any} The parent window for the panel.
        @return panel {wx.Panel} The created art panel.
        '''

        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        grid.Add(self._sizer_extract_walk(panel), pos=(0, 0), flag=wx.EXPAND | wx.ALL, border=4)
        grid.Add(self._sizer_extract_album_art(panel), pos=(1, 0), flag=wx.EXPAND | wx.ALL, border=4)
        grid.Add(self._sizer_set_album_art(panel), pos=(0, 1), span=(2, 1), flag=wx.EXPAND | wx.ALL, border=4)

        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 1)
        panel.SetSizer(grid)

        return panel


    def _sizer_extract_walk(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Creates the bulk directory art extraction section.

        @details Provides directory selection, file type filtering, and extraction controls.

        @param self {MainFrame} The instance of the class.
        @param parent {wx.Panel} The parent panel for the section.
        @return sizer {wx.StaticBoxSizer} The sizer containing the extraction controls.
        '''

        bulk_box = wx.StaticBox(parent, label="Directory Art Extraction")
        bulk_sizer = wx.StaticBoxSizer(bulk_box, wx.VERTICAL)
        bulk_subpanel = wx.Panel(parent)
        bulk_grid = wx.GridBagSizer(8, 8)

        # Create controls for selecting the starting directory and file type pattern for bulk extraction
        self.extract_walk_art_tld, extract_walk_art_btn = self._make_path_controls(bulk_subpanel)
        extract_walk_art_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_dir(evt, self.extract_walk_art_tld))

        file_types = ["Any file type"] + AUDIO_EXTS
        self.extract_walk_art_pattern = wx.Choice(bulk_subpanel, choices=file_types)
        self.extract_walk_art_pattern.SetSelection(0)
        self.extract_walk_art_pattern.SetToolTip("Select file type pattern or 'Any file type' to process all supported audio files")

        extract_walk_art_exec = wx.Button(bulk_subpanel, label="Extract Directory Art")
        extract_walk_art_exec.Bind(wx.EVT_BUTTON, self.handlers.on_extract_walk_art)

        bulk_grid.Add(wx.StaticText(bulk_subpanel, label="Starting path tld or fld:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulk_grid.Add(self.extract_walk_art_tld, pos=(0, 1), flag=wx.EXPAND)
        bulk_grid.Add(extract_walk_art_btn, pos=(0, 2))

        bulk_grid.Add(wx.StaticText(bulk_subpanel, label="Extract from Audio File Ext:"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulk_grid.Add(self.extract_walk_art_pattern, pos=(1, 1), span=(1, 2), flag=wx.EXPAND)
        bulk_grid.Add(extract_walk_art_exec, pos=(1, 3))

        bulk_grid.AddGrowableCol(1)
        bulk_subpanel.SetSizer(bulk_grid)
        bulk_sizer.Add(bulk_subpanel, 1, wx.EXPAND | wx.ALL, 4)

        return bulk_sizer


    def _sizer_extract_album_art(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Creates the specific file art extraction section.

        @details Provides audio file selection and art extraction controls.

        @param self {MainFrame} The instance of the class.
        @param parent {wx.Panel} The parent panel for the section.
        @return sizer {wx.StaticBoxSizer} The sizer containing the extraction controls.
        '''

        specific_box = wx.StaticBox(parent, label="File Art Extraction")
        specific_sizer = wx.StaticBoxSizer(specific_box, wx.VERTICAL)
        specific_subpanel = wx.Panel(parent)
        specific_grid = wx.GridBagSizer(8, 8)

        self.extract_file_art_path, extract_file_art_btn = self._make_path_controls(specific_subpanel)
        extract_file_art_btn.Bind(
            wx.EVT_BUTTON,
            lambda evt: self.handlers.on_browse_file(
                evt,
                self.extract_file_art_path,
                "Audio files (*.flac;*.mp3;*.m4a;*.wma)|*.flac;*.mp3;*.m4a;*.wma"
            )
        )

        extract_file_art_exec = wx.Button(specific_subpanel, label="Extract File Art")
        extract_file_art_exec.Bind(wx.EVT_BUTTON, self.handlers.on_extract_file_art)

        specific_grid.Add(wx.StaticText(specific_subpanel, label="Audio file to extract from:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        specific_grid.Add(self.extract_file_art_path, pos=(0, 1), flag=wx.EXPAND)
        specific_grid.Add(extract_file_art_btn, pos=(0, 2))
        specific_grid.Add(extract_file_art_exec, pos=(0, 3))

        specific_grid.AddGrowableCol(1)
        specific_subpanel.SetSizer(specific_grid)
        specific_sizer.Add(specific_subpanel, 1, wx.EXPAND | wx.ALL, 4)

        return specific_sizer


    def _sizer_set_album_art(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Creates the bulk directory art setting section.

        @details Provides directory selection and album art setting controls.

        @param self {MainFrame} The instance of the class.
        @param parent {wx.Panel} The parent panel for the section.
        @return sizer {wx.StaticBoxSizer} The sizer containing the setting controls.
        '''

        set_bulk_box = wx.StaticBox(parent, label="Set Album Art")
        set_bulk_sizer = wx.StaticBoxSizer(set_bulk_box, wx.VERTICAL)
        set_bulk_subpanel = wx.Panel(parent)
        set_bulk_grid = wx.GridBagSizer(8, 8)

        self.set_album_art_tld, set_album_art_btn = self._make_path_controls(set_bulk_subpanel)
        set_album_art_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_dir(evt, self.set_album_art_tld))

        set_album_art_exec = wx.Button(set_bulk_subpanel, label="Set Album Art")
        set_album_art_exec.Bind(wx.EVT_BUTTON, self.handlers.on_set_album_art)

        set_bulk_grid.Add(wx.StaticText(set_bulk_subpanel, label="Starting path tld or fld:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        set_bulk_grid.Add(self.set_album_art_tld, pos=(0, 1), flag=wx.EXPAND)
        set_bulk_grid.Add(set_album_art_btn, pos=(0, 2))
        set_bulk_grid.Add(set_album_art_exec, pos=(0, 3))

        set_bulk_grid.AddGrowableCol(1)
        set_bulk_subpanel.SetSizer(set_bulk_grid)
        set_bulk_sizer.Add(set_bulk_subpanel, 1, wx.EXPAND | wx.ALL, 4)

        return set_bulk_sizer


    def _panel_convert(self, parent) -> wx.Panel:
        '''
        @brief This panel includes controls for audio file conversion

        @details This panel is organized into nested subpanels for bulk directory processing and specific file processing.

        @param self {MainFrame} The instance of the class.
        @param parent {any}The parent window for the panel.
        @return panel {wx.Panel} The created convert panel.
        '''

        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        # Bulk directory audio conversion nested subpanel
        bulk_box = wx.StaticBox(panel, label="Bulk Directory Audio Conversion")
        bulk_sizer = wx.StaticBoxSizer(bulk_box, wx.VERTICAL)
        bulk_subpanel = wx.Panel(panel)
        bulk_grid = wx.GridBagSizer(8, 8)

        # Path controls for bulk directory audio conversion
        self.convert_walk_tld, convert_walk_tld_btn = self._make_path_controls(bulk_subpanel)
        convert_walk_tld_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_dir(evt, self.convert_walk_tld))

        # file type drop list for bulk conversion
        file_types = ["Any file type"] + AUDIO_EXTS
        self.convert_walk_audio_pattern = wx.Choice(bulk_subpanel, choices=file_types)
        self.convert_walk_audio_pattern.SetSelection(0)  # Default to "Any file type"
        self.convert_walk_audio_pattern.SetToolTip("Select file type pattern or 'Any file type' to process all supported audio files")

        # execute button for bulk directory audio conversion
        convert_walk_exec = wx.Button(bulk_subpanel, label="Convert Directory Audio")
        convert_walk_exec.Bind(wx.EVT_BUTTON, self.handlers.on_convert_walk)

        # order the top level directory controls in the bulk directory conversion subpanel grid
        bulk_grid.Add(wx.StaticText(bulk_subpanel, label="Top Level Directory to walk:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulk_grid.Add(self.convert_walk_tld, pos=(0, 1), flag=wx.EXPAND)
        bulk_grid.Add(convert_walk_tld_btn, pos=(0, 2))

        # order the file type pattern controls in the bulk directory conversion subpanel grid
        bulk_grid.Add(wx.StaticText(bulk_subpanel, label="Convert from Audio File Format:"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulk_grid.Add(self.convert_walk_audio_pattern, pos=(1, 1), span=(1, 2), flag=wx.EXPAND)
        bulk_grid.Add(convert_walk_exec, pos=(1, 3))

        # order the subpanels in the main grid
        bulk_grid.AddGrowableCol(1)
        bulk_subpanel.SetSizer(bulk_grid)
        bulk_sizer.Add(bulk_subpanel, 1, wx.EXPAND | wx.ALL, 4)

        # specific audio file conversion nested subpanel
        specific_box = wx.StaticBox(panel, label="Specific Audio File Conversion")
        specific_sizer = wx.StaticBoxSizer(specific_box, wx.VERTICAL)
        specific_subpanel = wx.Panel(panel)
        specific_grid = wx.GridBagSizer(8, 8)

        # Path controls for specific audio file conversion
        self.convert_file_path, convert_file_btn = self._make_path_controls(specific_subpanel)
        convert_file_btn.Bind(
            wx.EVT_BUTTON,
            lambda evt: self.handlers.on_browse_file(evt, self.convert_file_path, "Audio files (*.flac;*.mp3;*.m4a;*.wma)|*.flac;*.mp3;*.m4a;*.wma"))

        # execute button for specific audio file conversion
        convert_file_exec = wx.Button(specific_subpanel, label="Convert Audio File")
        convert_file_exec.Bind(wx.EVT_BUTTON, self.handlers.on_convert_file)

        # order the controls in the specific audio file conversion subpanel grid
        specific_grid.Add(wx.StaticText(specific_subpanel, label="Audio file to convert:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        specific_grid.Add(self.convert_file_path, pos=(0, 1), flag=wx.EXPAND)
        specific_grid.Add(convert_file_btn, pos=(0, 2))
        specific_grid.Add(convert_file_exec, pos=(0, 3))

        # allow specific subpanel to expand when frame is resized
        specific_grid.AddGrowableCol(1)
        specific_subpanel.SetSizer(specific_grid)
        specific_sizer.Add(specific_subpanel, 1, wx.EXPAND | wx.ALL, 4)

        # order the sub panels in the main grid
        grid.Add(bulk_sizer, pos=(0, 0), span=(1, 4), flag=wx.EXPAND | wx.ALL, border=4)
        grid.Add(specific_sizer, pos=(1, 0), span=(1, 4), flag=wx.EXPAND | wx.ALL, border=4)

        grid.AddGrowableCol(1)
        panel.SetSizer(grid)

        return panel


    def _panel_directory(self, parent) -> wx.Panel:
        '''
        @brief Create the directory panel.

        @details Provides controls for listing audio files, listing files by type, and removing empty albums or files matching a pattern.<br>
        It includes options for selecting top-level directories and specifying file extensions or patterns.

        @param self {MainFrame} The instance of the class.
        @param parent {any} The parent window for the panel.
        @return panel {wx.Panel} The created directory panel.
        '''

        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        self.list_audio_tld, list_audio_btn = self._make_path_controls(panel)
        list_audio_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_dir(evt, self.list_audio_tld))
        list_audio_exec = wx.Button(panel, label="List Audio")
        list_audio_exec.Bind(wx.EVT_BUTTON, self.handlers.on_list_audio)

        self.list_type_tld, list_type_btn = self._make_path_controls(panel)
        list_type_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_dir(evt, self.list_type_tld))
        self.list_type_ext = wx.TextCtrl(panel)
        list_type_exec = wx.Button(panel, label="List Type")
        list_type_exec.Bind(wx.EVT_BUTTON, self.handlers.on_list_type)

        self.remove_albums_tld, remove_albums_btn = self._make_path_controls(panel)
        remove_albums_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_dir(evt, self.remove_albums_tld))
        remove_albums_exec = wx.Button(panel, label="Remove Empty Albums")
        remove_albums_exec.Bind(wx.EVT_BUTTON, self.handlers.on_remove_albums)

        self.remove_pattern_tld, remove_pattern_btn = self._make_path_controls(panel)
        remove_pattern_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_dir(evt, self.remove_pattern_tld))
        self.remove_pattern_pattern = wx.TextCtrl(panel)
        remove_pattern_exec = wx.Button(panel, label="Remove Pattern")
        remove_pattern_exec.Bind(wx.EVT_BUTTON, self.handlers.on_remove_pattern)

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


    def _panel_metadata(self, parent) -> wx.Panel:
        '''
        @brief Create the metadata panel.

        @details This panel provides controls for retrieving and displaying metadata from media files.<br>
        It includes options for tags walk, media info walk, and unique media extraction.

        @param self {MainFrame} The instance of the class.
        @param parent {any} The parent window for the panel.
        @return panel {wx.Panel} The created metadata panel.
        '''

        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        self.tags_walk_tld, tags_walk_tld_btn = self._make_path_controls(panel)
        tags_walk_tld_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_dir(evt, self.tags_walk_tld))
        self.tags_walk_pattern = wx.TextCtrl(panel)
        self.tags_walk_ffprobe = wx.CheckBox(panel, label="Use ffprobe")
        tags_walk_exec = wx.Button(panel, label="Get Tags Walk")
        tags_walk_exec.Bind(wx.EVT_BUTTON, self.handlers.on_get_tags_walk)

        self.media_info_tld, media_info_btn = self._make_path_controls(panel)
        media_info_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_dir(evt, self.media_info_tld))
        self.media_info_pattern = wx.TextCtrl(panel)
        media_info_exec = wx.Button(panel, label="Get Media Info Walk")
        media_info_exec.Bind(wx.EVT_BUTTON, self.handlers.on_get_media_info_walk)

        self.unique_media_tld, unique_media_btn = self._make_path_controls(panel)
        unique_media_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_dir(evt, self.unique_media_tld))
        unique_media_exec = wx.Button(panel, label="Get Unique Media")
        unique_media_exec.Bind(wx.EVT_BUTTON, self.handlers.on_get_unique_media)

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


    def _panel_leveling(self, parent) -> wx.Panel:
        '''
        @brief This panel includes controls for audio normalization

        @details This panel is organized into nested subpanels for bulk directory processing and specific file processing.

        @param self {MainFrame} The instance of the class.
        @param parent {any} The parent window for the panel.
        @return panel {wx.Panel} The created normalize panel.
        '''

        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        # Bulk directory audio normalization nested subpanel
        bulk_box = wx.StaticBox(panel, label="Bulk Directory Normalizations")
        bulk_sizer = wx.StaticBoxSizer(bulk_box, wx.VERTICAL)
        bulk_subpanel = wx.Panel(panel)
        bulk_grid = wx.GridBagSizer(8, 8)

        # Path controls for bulk directory audio normalization
        self.norm_walk_tld, norm_walk_tld_btn = self._make_path_controls(bulk_subpanel)
        norm_walk_tld_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_dir(evt, self.norm_walk_tld))

        # normalization type drop list for bulk normalization
        self.norm_type_choice = wx.Choice(bulk_subpanel, choices=["ebu", "peak", "rms"])
        self.norm_type_choice.SetSelection(0)
        self.norm_type_choice.SetToolTip("Select normalization type: ebu (loudness), peak (peak level), or rms (RMS level)")

        # execute button for bulk directory audio normalization
        norm_walk_exec = wx.Button(bulk_subpanel, label="Normalize Directory")
        norm_walk_exec.Bind(wx.EVT_BUTTON, self.handlers.on_normalize_walk)

        # order the top level directory controls in the bulk directory normalization subpanel grid
        bulk_grid.Add(wx.StaticText(bulk_subpanel, label="Top Level Directory to walk:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulk_grid.Add(self.norm_walk_tld, pos=(0, 1), flag=wx.EXPAND)
        bulk_grid.Add(norm_walk_tld_btn, pos=(0, 2))

        # order the normalization type controls in the bulk directory normalization subpanel grid
        bulk_grid.Add(wx.StaticText(bulk_subpanel, label="Normalization Type:"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulk_grid.Add(self.norm_type_choice, pos=(1, 1), flag=wx.EXPAND)
        bulk_grid.Add(norm_walk_exec, pos=(1, 2))

        # order the subpanels in the main grid
        bulk_grid.AddGrowableCol(1)
        bulk_subpanel.SetSizer(bulk_grid)
        bulk_sizer.Add(bulk_subpanel, 1, wx.EXPAND | wx.ALL, 4)

        # Specific normalizations nested subpanel
        specific_box = wx.StaticBox(panel, label="Single File Normalizations")
        specific_sizer = wx.StaticBoxSizer(specific_box, wx.VERTICAL)
        specific_subpanel = wx.Panel(panel)
        specific_grid = wx.GridBagSizer(8, 8)

        # Path controls for specific file ebu normalizations
        mp3_wildcard = "MP3 files (*.mp3)|*.mp3"
        self.ebu_file_path, ebu_file_btn = self._make_path_controls(specific_subpanel)
        ebu_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_file(evt, self.ebu_file_path, mp3_wildcard))

        # execute button for specific file EBU normalization
        ebu_file_exec = wx.Button(specific_subpanel, label="EBU Normalize File")
        ebu_file_exec.Bind(wx.EVT_BUTTON, self.handlers.on_ebu_file)

        # Path controls for specific file peak normalizations
        self.peak_file_path, peak_file_btn = self._make_path_controls(specific_subpanel)
        peak_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_file(evt, self.peak_file_path, mp3_wildcard))

        peak_file_exec = wx.Button(specific_subpanel, label="Peak Normalize File")
        peak_file_exec.Bind(wx.EVT_BUTTON, self.handlers.on_peak_file)

        # Path controls for specific file RMS normalizations
        self.rms_file_path, rms_file_btn = self._make_path_controls(specific_subpanel)
        rms_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_file(evt, self.rms_file_path, mp3_wildcard))

        # execute button for specific file RMS normalization
        rms_file_exec = wx.Button(specific_subpanel, label="RMS Normalize File")
        rms_file_exec.Bind(wx.EVT_BUTTON, self.handlers.on_rms_file)

        # order the specific file ebu normalization controls in the grid
        specific_grid.Add(wx.StaticText(specific_subpanel, label="File to EBU Normalize:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        specific_grid.Add(self.ebu_file_path, pos=(0, 1), flag=wx.EXPAND)
        specific_grid.Add(ebu_file_btn, pos=(0, 2))
        specific_grid.Add(ebu_file_exec, pos=(0, 3))

        # order the specific file peak normalization controls in the grid
        specific_grid.Add(wx.StaticText(specific_subpanel, label="File to Peak Normalize:"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        specific_grid.Add(self.peak_file_path, pos=(1, 1), flag=wx.EXPAND)
        specific_grid.Add(peak_file_btn, pos=(1, 2))
        specific_grid.Add(peak_file_exec, pos=(1, 3))

        # order the specific file RMS normalization controls in the grid
        specific_grid.Add(wx.StaticText(specific_subpanel, label="File to RMS Normalize:"), pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        specific_grid.Add(self.rms_file_path, pos=(2, 1), flag=wx.EXPAND)
        specific_grid.Add(rms_file_btn, pos=(2, 2))
        specific_grid.Add(rms_file_exec, pos=(2, 3))

        # allow specific subpanel to expand when frame is resized
        specific_grid.AddGrowableCol(1)
        specific_subpanel.SetSizer(specific_grid)
        specific_sizer.Add(specific_subpanel, 1, wx.EXPAND | wx.ALL, 4)

        # order the sub panels in the main grid
        grid.Add(bulk_sizer, pos=(0, 0), span=(1, 4), flag=wx.EXPAND | wx.ALL, border=4)
        grid.Add(specific_sizer, pos=(1, 0), span=(1, 4), flag=wx.EXPAND | wx.ALL, border=4)

        grid.AddGrowableCol(1)
        panel.SetSizer(grid)

        return panel


    def _make_path_controls(self, parent) -> tuple:
        '''
        @brief Helper function to create a standard set of path controls (text box and browse button).

        @details This function is used to create consistent path input controls across different panels in the application.

        @param self {MainFrame} The instance of the class.
        @param parent {any} The parent window for the controls.
        @return path_controls (textbox, button) ({wx.TextCtrl}, {wx.Button}) Tuple containing the text control and the browse button.
        '''

        textbox = wx.TextCtrl(parent)
        textbox.SetToolTip("Enter path or click Browse button")
        button = wx.Button(parent, label="Browse")
        button.SetToolTip("Browse for a path")

        path_controls = (textbox, button)

        return path_controls


    def _panel_playlist(self, parent) -> wx.Panel:
        '''
        @brief Create the playlist panel.

        @details This panel provides controls for updating M3U playlists and performing directory walks.<br>
        It includes nested subpanels for updating a specific playlist file and for walking a directory tree.

        @param self {MainFrame} The instance of the class.
        @param parent {any} The parent window for the panel.
        @return panel {wx.Panel} The created playlist panel.
        '''

        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        # Update Playlist Walk nested subpanel
        bulk_box = wx.StaticBox(panel, label="Bulk Directory Playlist Update")
        bulk_sizer = wx.StaticBoxSizer(bulk_box, wx.VERTICAL)
        bulk_subpanel = wx.Panel(panel)
        bulk_grid = wx.GridBagSizer(8, 8)

        # Path controls for updating playlist walk
        self.bulk_tld, bulk_btn = self._make_path_controls(bulk_subpanel)
        bulk_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_dir(evt, self.bulk_tld))

        # execute button for updating playlist walk
        bulk_exec = wx.Button(bulk_subpanel, label="Update Directory Playlist")
        bulk_exec.Bind(wx.EVT_BUTTON, self.handlers.on_update_walk)

        # order the controls in the update playlist walk subpanel grid
        bulk_grid.Add(wx.StaticText(bulk_subpanel, label="Top Level Directory to walk:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulk_grid.Add(self.bulk_tld, pos=(0, 1), flag=wx.EXPAND)
        bulk_grid.Add(bulk_btn, pos=(0, 2))
        bulk_grid.Add(bulk_exec, pos=(0, 3))

        # allows update playlist walk subpanel to expand when frame is resized
        bulk_grid.AddGrowableCol(1)
        bulk_subpanel.SetSizer(bulk_grid)
        bulk_sizer.Add(bulk_subpanel, 1, wx.EXPAND | wx.ALL, 4)

        # Specific playlist update nested subpanel
        specific_box = wx.StaticBox(panel, label="Specific Playlist Update")
        specific_sizer = wx.StaticBoxSizer(specific_box, wx.VERTICAL)
        specific_subpanel = wx.Panel(panel)
        specific_grid = wx.GridBagSizer(8, 8)

        # Path controls for updating M3U playlist
        playlist_wildcard = f"Playlist files ({';'.join('*' + ext for ext in PLAYLIST_EXTS)})|{';'.join('*' + ext for ext in PLAYLIST_EXTS)}"
        self.update_m3u_file, update_m3u_file_btn = self._make_path_controls(specific_subpanel)
        update_m3u_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.handlers.on_browse_file(evt, self.update_m3u_file, playlist_wildcard))

        # Execute button for updating M3U playlist
        update_m3u_exec = wx.Button(specific_subpanel, label="Update Playlist File")
        update_m3u_exec.Bind(wx.EVT_BUTTON, self.handlers.on_update_m3u)

        # order the controls in the update M3U playlist subpanel grid
        specific_grid.Add(wx.StaticText(specific_subpanel, label="Playlist file to update:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        specific_grid.Add(self.update_m3u_file, pos=(0, 1), flag=wx.EXPAND)
        specific_grid.Add(update_m3u_file_btn, pos=(0, 2))
        specific_grid.Add(update_m3u_exec, pos=(0, 3))

        # allows update M3U subpanel to expand when frame is resized
        specific_grid.AddGrowableCol(1)
        specific_subpanel.SetSizer(specific_grid)
        specific_sizer.Add(specific_subpanel, 1, wx.EXPAND | wx.ALL, 4)

        # order the subpanels in the main grid
        grid.Add(bulk_sizer, pos=(0, 0), span=(1, 4), flag=wx.EXPAND | wx.ALL, border=4)
        grid.Add(specific_sizer, pos=(1, 0), span=(1, 4), flag=wx.EXPAND | wx.ALL, border=4)

        grid.AddGrowableCol(1)
        panel.SetSizer(grid)

        return panel


    def _set_busy_state(self, busy=True):
        '''
        @brief Set the busy state of the application.

        @details This method enables or disables the main window and log control based on the busy state.<br>
        It also changes the cursor to a wait cursor when busy and back to the default cursor when not busy.

        @param self {MainFrame} The instance of the class.
        @param busy {bool} True to set the application to busy state, False to set it to idle state.
        '''

        self.Enable(not busy)
        self.log_ctrl.Enable(True)
        self.SetCursor(wx.Cursor(wx.CURSOR_WAIT if busy else wx.CURSOR_ARROW))


    def _show_generated_files_dialog(self):
        '''
        @brief Display a file dialog to select generated MP3 files for moving.

        @details This method opens a file dialog starting in the directory where generated MP3 files are stored.

        @param self {MainFrame} The instance of the class.
        '''

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

    def _show_generated_playlist_dialog(self):
        '''
        @brief Display a file dialog to select generated playlist files for moving.

        @details This method opens a file dialog starting in the generated files directory.<br>
        It restricts file selection to playlist file extensions only.

        @param self {MainFrame} The instance of the class.
        '''

        generated_dir = GENERATED_PATH
        if not os.path.isdir(generated_dir):
            wx.MessageBox(
                f"Generated files directory not found: {generated_dir}",
                "Info",
                wx.ICON_INFORMATION,
            )
            return

        playlist_patterns = ';'.join('*' + ext for ext in PLAYLIST_EXTS)
        dlg = wx.FileDialog(
            self,
            "Select generated playlist files:",
            defaultDir=generated_dir,
            wildcard=f"Playlist files ({playlist_patterns})|{playlist_patterns}",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR,
        )

        if dlg.ShowModal() == wx.ID_OK:
            selected_files = dlg.GetPaths()
            if selected_files:
                self._move_files_dialog(selected_files)

        dlg.Destroy()


    def _show_result_file(self, filename):
        '''
        @brief Display the contents of a result file in the log control.

        @details This method constructs the path to the result file based on the provided filename and checks if it exists.

        @param self {MainFrame} The instance of the class.
        @param filename {str} The base name of the result file (without extension) to display.
        '''

        result_path = os.path.join(GENERATED_PATH, RESULT_DIR, filename + RESULT_EXT)

        if not os.path.isfile(result_path):
            wx.MessageBox(
                f"Result file not found: {result_path}",
                "Info",
                wx.ICON_INFORMATION,
            )
            return

        with open(result_path, "r", encoding="utf-8") as result_file:
            content = result_file.read()

        wx.CallAfter(self.log_ctrl.SetValue, f"=== {filename + RESULT_EXT} ===\n{content}")


    def _validate_dir(self, path):
        '''
        @brief Validate that the provided path is a directory.

        @details This method checks if the provided path is not empty and exists as a directory.<br>
        If the validation fails, it displays an appropriate message box to the user.

        @param self {MainFrame} The instance of the class.
        @param path {str} The directory path to validate.
        @return bool True if the path is a valid directory, False otherwise.
        '''

        if not path:
            wx.MessageBox("Please specify a directory path.", "Validation", wx.ICON_WARNING)
            return False

        if not os.path.isdir(path):
            wx.MessageBox(f"Directory not found: {path}", "Validation", wx.ICON_ERROR)
            return False

        return True


    def _validate_file(self, path):
        '''
        @brief Validate that the provided path is a file.

        @details This method checks if the provided path is not empty and exists as a file.<br>
        If the validation fails, it displays an appropriate message box to the user.

        @param self {MainFrame} The instance of the class.
        @param path {str} The file path to validate.
        @return bool True if the path is a valid file, False otherwise.
        '''

        if not path:
            wx.MessageBox("Please specify a file path.", "Validation", wx.ICON_WARNING)
            return False

        if not os.path.isfile(path):
            wx.MessageBox(f"File not found: {path}", "Validation", wx.ICON_ERROR)
            return False

        return True


    def _move_files(self, file_paths, dest_dir):
        '''
        @brief Move selected files to the specified destination directory and display a summary of the operation.

        @details This method attempts to move each file in the provided list of file paths to the specified destination directory.

        @param self {MainFrame} The instance of the class.
        @param file_paths {list} A list of file paths to move.
        @param dest_dir {str} The destination directory to move the files to.

        @exception Exception If an error occurs while moving a file, the exception is caught and recorded in the failed list, which is included in the summary message displayed to the user.
        '''

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


    def _move_files_dialog(self, file_paths):
        '''
        @brief Display a dialog to select the destination directory for moving files.

        @details Displays a directory selection dialog to the user and moves the selected files to the chosen directory if confirmed.<br>
        If the user cancels the dialog, no action is taken.

        @param self {MainFrame} The instance of the class.
        @param file_paths {list} A list of file paths to move.
        '''

        dest_dlg = wx.DirDialog(
            self,
            "Select destination directory to move files to:",
            style=wx.DD_DIR_MUST_EXIST,
        )

        if dest_dlg.ShowModal() == wx.ID_OK:
            dest_dir = dest_dlg.GetPath()
            self._move_files(file_paths, dest_dir)

        dest_dlg.Destroy()


    def log(self, message):
        '''
        @brief Log a message to the log control with a timestamp.

        @details This method uses wx.CallAfter to ensure that log updates are thread-safe and do not cause issues with the GUI responsiveness.<br>
        Each log entry is prefixed with a timestamp for better tracking of events.

        @param self {MainFrame} The instance of the class.
        @param message {str} The message to log.
        '''

        wx.CallAfter(self.log_ctrl.AppendText, f"[{_timestamp()}] {message}\n")


    def run_task(self, func, *args, on_success=None):
        '''
        @brief Run a long-running task in a separate thread to keep the GUI responsive.

        @details Runs the given function in a separate thread to keep the GUI responsive.<br>
        Logs the start and completion of the task, and handles any exceptions that occur.

        @param self {MainFrame} The instance of the class.
        @param func The function to run as the task.
        @param args {tuple} Arguments to pass to the function.
        @param on_success {callback} Optional callback to run on the main thread after successful completion of the task
        @return None
        '''

        def worker():
            '''
            @brief Worker function to run the task and handle logging and exceptions.

            @details Runs in separate thread, executes given task function, logs start and completion of task, handles any exceptions that occur.<br>
            It also ensures that the busy state of the GUI is properly managed.

            @exception Exception Any exception raised by the task function is caught and logged, and an error message box is displayed to the user.
            '''

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
                wx.CallAfter(self._set_busy_state, False)

        self._set_busy_state(True)
        threading.Thread(target=worker, daemon=True).start()


def run_gui():
    '''
    @brief Entry point to run the GUI application.

    @details This function initializes the wx.App, creates the main frame, and starts the main event loop.
    '''

    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
