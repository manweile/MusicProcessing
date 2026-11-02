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

    @retval time_stamp (str) A string representing the current timestamp in the format "YYYY-MM-DD HH:MM:SS".
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

    # Blueprint hints tell VS Code these instance variables exist and what they are
    mainLog: wx.TextCtrl
    mainPanel: wx.Panel
    mainSplitter: wx.SplitterWindow
    mainNotebook: wx.Notebook
    mainHandlers: EventHandlers

    panelArt: wx.Panel
    panelConvert: wx.Panel
    panelLeveling: wx.Panel
    panelPlaylist: wx.Panel
    panelMetadata: wx.Panel
    panelDirectory: wx.Panel

    bulkPathText: wx.TextCtrl
    patternChoice: wx.Choice
    filePathText: wx.TextCtrl
    settingPathText: wx.TextCtrl


    def __init__(self, parent=None) -> None:
        '''
        @brief Initialize the MainFrame class.

        @details This constructor sets up the main window, including the layout, panels, and event handlers.

        @param self: (MainFrame) The instance of the class.
        @param parent: (Any) The parent window, if any.
        '''

        # Initialize the main frame with the specified parent, title, and size
        super().__init__(parent, title="Music Processing GUI", size=(960, 760))

        # Increase font size by 2 points
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(font.GetPointSize() + 2)
        self.SetFont(font)

        # Create the main panel within the frame
        self.mainPanel = wx.Panel(self)
        self.mainPanel.SetFont(font)

        # Create splitter window for resizable notebook/log split
        self.mainSplitter = wx.SplitterWindow(self.mainPanel, style=wx.SP_LIVE_UPDATE)

        # Create the notebook for tabbed panels within the splitter window
        self.mainNotebook = wx.Notebook(self.mainSplitter)

        # Initialize event handlers
        self.mainHandlers = EventHandlers(self)

        # Create the individual panels for each tab in the notebook
        self.panelArt = self._panel_art(self.mainNotebook)
        self.panelConvert = self._panel_convert(self.mainNotebook)
        self.panelLeveling = self._panel_leveling(self.mainNotebook)
        self.panelPlaylist = self._panel_playlist(self.mainNotebook)
        self.panelMetadata = self._panel_metadata(self.mainNotebook)
        self.panelDirectory = self._panel_directory(self.mainNotebook)

        # Add the created panels to the notebook as separate tabs
        self.mainNotebook.AddPage(self.panelArt, "Art")
        self.mainNotebook.AddPage(self.panelConvert, "Convert")
        self.mainNotebook.AddPage(self.panelLeveling, "Normalize")
        self.mainNotebook.AddPage(self.panelPlaylist, "Playlist")
        self.mainNotebook.AddPage(self.panelMetadata, "Metadata")
        self.mainNotebook.AddPage(self.panelDirectory, "Directory")

        # Create the log control for displaying log messages
        self.mainLog = wx.TextCtrl(self.mainSplitter, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL, value="")

        # Split horizontally: notebook on top, log on bottom
        self.mainSplitter.SplitHorizontally(self.mainNotebook, self.mainLog)
        self.mainSplitter.SetSashPosition(550)  # Initial sash position in pixels from top

        # Set up the main sizer for the panel and add the splitter window to it
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.mainSplitter, 1, wx.EXPAND)
        self.mainPanel.SetSizer(mainSizer)
        self.Maximize()


    def _panel_art(self, parent) -> wx.Panel:
        '''
        @brief This panel contains album art extraction and setting controls.

        @details Stacks the extraction sections at left and places the setting section to their right.

        @param self: (MainFrame) The instance of the class.
        @param parent: (Any) The parent window for the panel.

        @retval panel (wx.Panel) The created art panel.
        '''

        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        grid.Add(self._sizer_extract_walk(panel), pos=(0, 0), flag=wx.EXPAND | wx.ALL, border=4)
        grid.Add(self._sizer_set_album_art(panel), pos=(1, 0), flag=wx.EXPAND | wx.ALL, border=4)
        grid.Add(self._sizer_extract_album_art(panel), pos=(0, 1), span=(2, 1), flag=wx.EXPAND | wx.ALL, border=4)

        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 1)
        panel.SetSizer(grid)

        return panel


    def _sizer_extract_walk(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Creates the bulk directory art extraction section.

        @details Provides directory selection, file type filtering, and extraction controls.

        @param self: (MainFrame) The instance of the class.
        @param parent: (wx.Panel) The parent panel for the section.

        @retval bulk_sizer (wx.StaticBoxSizer) The sizer containing the extraction controls.
        '''

        # Create the static box, sizers, and panel for the bulk directory art extraction section
        bulkBox = wx.StaticBox(parent, label="Directory Art Extraction")
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)
        bulkPanel = wx.Panel(parent)
        bulkGrid = wx.GridBagSizer(8, 8)

        # create static text for brief description of the section
        briefDesc = wx.StaticText(bulkPanel, label="Extracts album art from all audio files in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="The extracted album art will be saved alongside the audio files")

        # Create controls for selecting the starting path for bulk extraction
        self.bulkPathText, bulkBrowseButton = self._make_path_controls(bulkPanel)
        bulkBrowseButton.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_dir(evt, self.bulkPathText))

        # Create controls for selecting the file type pattern for bulk extraction
        file_types = ["Any file type"] + AUDIO_EXTS
        self.patternChoice = wx.Choice(bulkPanel, choices=file_types)
        self.patternChoice.SetSelection(0)
        self.patternChoice.SetToolTip("Select file type pattern or 'Any file type' to process all supported audio files")

        # Create the extraction button
        extractBulkButton = wx.Button(bulkPanel, label="Extract Directory Art")
        extractBulkButton.Bind(wx.EVT_BUTTON, self.mainHandlers.on_extract_walk_art)

        # Add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # add controls for the starting path to the grid layout
        bulkGrid.Add(wx.StaticText(bulkPanel, label="Starting path tld or fld:"), pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.bulkPathText, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(bulkBrowseButton, pos=(2, 3), flag=wx.EXPAND)

        # Add controls for selecting the file type pattern and extraction button to the grid layout
        bulkGrid.Add(wx.StaticText(bulkPanel, label="Extract from Audio Ext:"), pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.patternChoice, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(extractBulkButton, pos=(3, 3))

        # Make the second column growable to allow the controls to expand properly
        bulkGrid.AddGrowableCol(1)

        # Set the sizer for the panel and add it to the static box sizer
        bulkPanel.SetSizer(bulkGrid)
        bulkSizer.Add(bulkPanel, 1, wx.EXPAND | wx.ALL, 4)

        return bulkSizer


    def _sizer_extract_album_art(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Creates the specific file art extraction section.

        @details Provides audio file selection and art extraction controls.

        @param self: (MainFrame) The instance of the class.
        @param parent: (wx.Panel) The parent panel for the section.

        @retval fileSizer (wx.StaticBoxSizer) The sizer containing the extraction controls.
        '''

        # Create the static box, sizer , and panel for the file art extraction section
        fileBox = wx.StaticBox(parent, label="File Art Extraction")
        fileSizer = wx.StaticBoxSizer(fileBox, wx.VERTICAL)
        filePanel = wx.Panel(parent)
        fileGrid = wx.GridBagSizer(8, 8)

        # create static text for brief description of the section
        briefDesc = wx.StaticText(filePanel, label="Extracts album art from specific audio file")
        resultDesc = wx.StaticText(filePanel, label="The extracted album art will be saved alongside the audio file")

        # Create file picker controls for selecting the audio file
        file_exts = "Audio files (*.flac;*.mp3;*.m4a;*.wma)|*.flac;*.mp3;*.m4a;*.wma"
        self.filePathText, fileBrowseButton = self._make_path_controls(filePanel)
        fileBrowseButton.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_file(evt, self.filePathText, file_exts))

        # Create the extract file art button
        extractFileButton = wx.Button(filePanel, label="Extract File Art")
        extractFileButton.Bind(wx.EVT_BUTTON, self.mainHandlers.on_extract_file_art)

        # Create a horizontal sizer for the file path and extract buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(fileBrowseButton, 0, wx.RIGHT, 8)
        buttonSizer.Add(extractFileButton, 0)

        # Create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.filePathText, 1, wx.EXPAND | wx.RIGHT, 8)
        pathRowSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # Add info text controls to the grid layout
        fileGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        fileGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # Add the path row to the grid layout
        fileGrid.Add(wx.StaticText(filePanel, label="Audio file path:"), pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(pathRowSizer, pos=(2, 1), span=(1, 3), flag=wx.EXPAND)

        # Make the second column growable to allow the controls to expand properly
        fileGrid.AddGrowableCol(1)

        # Set the sizer for the panel and add it to the static box sizer
        filePanel.SetSizer(fileGrid)
        fileSizer.Add(filePanel, 1, wx.EXPAND | wx.ALL, 4)

        return fileSizer


    def _sizer_set_album_art(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Creates the bulk directory art setting section.

        @details Provides directory selection and album art setting controls.

        @param self: (MainFrame) The instance of the class.
        @param parent: (wx.Panel) The parent panel for the section.

        @retval setBulkSizer (wx.StaticBoxSizer) The sizer containing the setting controls.
        '''

        # Create the static box, sizer, and panel for the album art setting section
        setBulkBox = wx.StaticBox(parent, label="Set Album Art")
        setBulkSizer = wx.StaticBoxSizer(setBulkBox, wx.VERTICAL)
        setBulkPanel = wx.Panel(parent)
        setBulkGrid = wx.GridBagSizer(8, 8)

        # Create static text for brief description of the section
        briefDesc = wx.StaticText(setBulkPanel, label="Sets album art file for an album directory from project source folder")
        detailDesc = wx.StaticText(setBulkPanel, label="Copies a matching AlbumArt JPEG into the album directory when it is available")

        # Create controls for selecting the starting path for setting album art
        self.settingPathText, settingBrowseButton = self._make_path_controls(setBulkPanel)
        settingBrowseButton.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_dir(evt, self.settingPathText))

        # Create the set art button
        setArtButton = wx.Button(setBulkPanel, label="Set Album Art")
        setArtButton.Bind(wx.EVT_BUTTON, self.mainHandlers.on_set_album_art)

        # Create a horizontal sizer for the browse and setting buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(settingBrowseButton, 0, wx.RIGHT, 8)
        buttonSizer.Add(setArtButton, 0)

        # Create a horizontal sizer for the starting path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.settingPathText, 1, wx.EXPAND | wx.RIGHT, 8)
        pathRowSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # Add the info text controls to the grid layout
        setBulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 4), flag=wx.EXPAND)
        setBulkGrid.Add(detailDesc, pos=(1, 0), span=(1, 4), flag=wx.EXPAND)

        # Add the starting path controls to the grid layout
        setBulkGrid.Add(wx.StaticText(setBulkPanel, label="Starting path tld or fld:"), pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        setBulkGrid.Add(pathRowSizer, pos=(2, 1), span=(1, 3), flag=wx.EXPAND)

        setBulkGrid.AddGrowableCol(1)
        setBulkPanel.SetSizer(setBulkGrid)
        setBulkSizer.Add(setBulkPanel, 1, wx.EXPAND | wx.ALL, 4)

        return setBulkSizer


    def _panel_convert(self, parent) -> wx.Panel:
        '''
        @brief This panel includes controls for audio file conversion

        @details This panel is organized into nested subpanels for bulk directory processing and specific file processing.

        @param self: (MainFrame) The instance of the class.
        @param parent: (Any) The parent window for the panel.

        @retval panel (wx.Panel) The created convert panel.
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
        convert_walk_tld_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_dir(evt, self.convert_walk_tld))

        # file type drop list for bulk conversion
        file_types = ["Any file type"] + AUDIO_EXTS
        self.convert_walk_audio_pattern = wx.Choice(bulk_subpanel, choices=file_types)
        self.convert_walk_audio_pattern.SetSelection(0)  # Default to "Any file type"
        self.convert_walk_audio_pattern.SetToolTip("Select file type pattern or 'Any file type' to process all supported audio files")

        # execute button for bulk directory audio conversion
        convert_walk_exec = wx.Button(bulk_subpanel, label="Convert Directory Audio")
        convert_walk_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_convert_walk)

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
            lambda evt: self.mainHandlers.on_browse_file(evt, self.convert_file_path, "Audio files (*.flac;*.mp3;*.m4a;*.wma)|*.flac;*.mp3;*.m4a;*.wma"))

        # execute button for specific audio file conversion
        convert_file_exec = wx.Button(specific_subpanel, label="Convert Audio File")
        convert_file_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_convert_file)

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

        @param self: (MainFrame) The instance of the class.
        @param parent: (Any) The parent window for the panel.

        @retval panel (wx.Panel) The created directory panel.
        '''

        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        self.list_audio_tld, list_audio_btn = self._make_path_controls(panel)
        list_audio_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_dir(evt, self.list_audio_tld))
        list_audio_exec = wx.Button(panel, label="List Audio")
        list_audio_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_list_audio)

        self.list_type_tld, list_type_btn = self._make_path_controls(panel)
        list_type_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_dir(evt, self.list_type_tld))
        self.list_type_ext = wx.TextCtrl(panel)
        list_type_exec = wx.Button(panel, label="List Type")
        list_type_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_list_type)

        self.remove_albums_tld, remove_albums_btn = self._make_path_controls(panel)
        remove_albums_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_dir(evt, self.remove_albums_tld))
        remove_albums_exec = wx.Button(panel, label="Remove Empty Albums")
        remove_albums_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_remove_albums)

        self.remove_pattern_tld, remove_pattern_btn = self._make_path_controls(panel)
        remove_pattern_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_dir(evt, self.remove_pattern_tld))
        self.remove_pattern_pattern = wx.TextCtrl(panel)
        remove_pattern_exec = wx.Button(panel, label="Remove Pattern")
        remove_pattern_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_remove_pattern)

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

        @param self: (MainFrame) The instance of the class.
        @param parent: (Any) The parent window for the panel.

        @retval panel (wx.Panel) The created metadata panel.
        '''

        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        self.tags_walk_tld, tags_walk_tld_btn = self._make_path_controls(panel)
        tags_walk_tld_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_dir(evt, self.tags_walk_tld))
        self.tags_walk_pattern = wx.TextCtrl(panel)
        self.tags_walk_ffprobe = wx.CheckBox(panel, label="Use ffprobe")
        tags_walk_exec = wx.Button(panel, label="Get Tags Walk")
        tags_walk_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_get_tags_walk)

        self.media_info_tld, media_info_btn = self._make_path_controls(panel)
        media_info_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_dir(evt, self.media_info_tld))
        self.media_info_pattern = wx.TextCtrl(panel)
        media_info_exec = wx.Button(panel, label="Get Media Info Walk")
        media_info_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_get_media_info_walk)

        self.unique_media_tld, unique_media_btn = self._make_path_controls(panel)
        unique_media_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_dir(evt, self.unique_media_tld))
        unique_media_exec = wx.Button(panel, label="Get Unique Media")
        unique_media_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_get_unique_media)

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

        @param self: (MainFrame) The instance of the class.
        @param parent: (Any) The parent window for the panel.

        @retval panel (wx.Panel) The created normalize panel.
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
        norm_walk_tld_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_dir(evt, self.norm_walk_tld))

        # normalization type drop list for bulk normalization
        self.norm_type_choice = wx.Choice(bulk_subpanel, choices=["ebu", "peak", "rms"])
        self.norm_type_choice.SetSelection(0)
        self.norm_type_choice.SetToolTip("Select normalization type: ebu (loudness), peak (peak level), or rms (RMS level)")

        # execute button for bulk directory audio normalization
        norm_walk_exec = wx.Button(bulk_subpanel, label="Normalize Directory")
        norm_walk_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_normalize_walk)

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
        ebu_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_file(evt, self.ebu_file_path, mp3_wildcard))

        # execute button for specific file EBU normalization
        ebu_file_exec = wx.Button(specific_subpanel, label="EBU Normalize File")
        ebu_file_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_ebu_file)

        # Path controls for specific file peak normalizations
        self.peak_file_path, peak_file_btn = self._make_path_controls(specific_subpanel)
        peak_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_file(evt, self.peak_file_path, mp3_wildcard))

        peak_file_exec = wx.Button(specific_subpanel, label="Peak Normalize File")
        peak_file_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_peak_file)

        # Path controls for specific file RMS normalizations
        self.rms_file_path, rms_file_btn = self._make_path_controls(specific_subpanel)
        rms_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_file(evt, self.rms_file_path, mp3_wildcard))

        # execute button for specific file RMS normalization
        rms_file_exec = wx.Button(specific_subpanel, label="RMS Normalize File")
        rms_file_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_rms_file)

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

        @param self: (MainFrame) The instance of the class.
        @param parent: (Any) The parent window for the controls.

        @retval path_controls ((wx.TextCtrl), (wx.Button)) Tuple containing the text control and the browse button.
        '''

        pathLabel = wx.TextCtrl(parent)
        pathLabel.SetToolTip("Enter a path or click Browse button")
        browseButton = wx.Button(parent, label="Browse")
        browseButton.SetToolTip("Browse for a path")

        path_controls = (pathLabel, browseButton)

        return path_controls


    def _panel_playlist(self, parent) -> wx.Panel:
        '''
        @brief Create the playlist panel.

        @details This panel provides controls for updating M3U playlists and performing directory walks.<br>
        It includes nested subpanels for updating a specific playlist file and for walking a directory tree.

        @param self: (MainFrame) The instance of the class.
        @param parent: (any) The parent window for the panel.

        @retval panel (wx.Panel) The created playlist panel.
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
        bulk_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_dir(evt, self.bulk_tld))

        # execute button for updating playlist walk
        bulk_exec = wx.Button(bulk_subpanel, label="Update Directory Playlist")
        bulk_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_update_walk)

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
        update_m3u_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.mainHandlers.on_browse_file(evt, self.update_m3u_file, playlist_wildcard))

        # Execute button for updating M3U playlist
        update_m3u_exec = wx.Button(specific_subpanel, label="Update Playlist File")
        update_m3u_exec.Bind(wx.EVT_BUTTON, self.mainHandlers.on_update_m3u)

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

        @param self: (MainFrame) The instance of the class.
        @param busy: (bool) True to set the application to busy state, False to set it to idle state.
        '''

        self.Enable(not busy)
        self.mainLog.Enable(True)
        self.SetCursor(wx.Cursor(wx.CURSOR_WAIT if busy else wx.CURSOR_ARROW))


    def _show_generated_files_dialog(self):
        '''
        @brief Display a file dialog to select generated MP3 files for moving.

        @details This method opens a file dialog starting in the directory where generated MP3 files are stored.

        @param self: (MainFrame) The instance of the class.
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

        @param self: (MainFrame) The instance of the class.
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

        @param self: (MainFrame) The instance of the class.
        @param filename: (str) The base name of the result file (without extension) to display.
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

        wx.CallAfter(self.mainLog.SetValue, f"=== {filename + RESULT_EXT} ===\n{content}")


    def _validate_dir(self, path):
        '''
        @brief Validate that the provided path is a directory.

        @details This method checks if the provided path is not empty and exists as a directory.<br>
        If the validation fails, it displays an appropriate message box to the user.

        @param self: (MainFrame) The instance of the class.
        @param path: (str) The directory path to validate.
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

        @param self: (MainFrame) The instance of the class.
        @param path: (str) The file path to validate.
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

        @param self: (MainFrame) The instance of the class.
        @param file_paths: (list) A list of file paths to move.
        @param dest_dir: (str) The destination directory to move the files to.

        @exception Exception caught and recorded in the failed list, which is included in the summary message displayed to the user.
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

        @param self: (MainFrame) The instance of the class.
        @param file_paths: (list) A list of file paths to move.
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

        @param self: (MainFrame) The instance of the class.
        @param message: (str) The message to log.
        '''

        wx.CallAfter(self.mainLog.AppendText, f"[{_timestamp()}] {message}\n")


    def run_task(self, func, *args, on_success=None):
        '''
        @brief Run a long-running task in a separate thread to keep the GUI responsive.

        @details Runs the given function in a separate thread to keep the GUI responsive.<br>
        Logs the start and completion of the task, and handles any exceptions that occur.

        @param self: (MainFrame) The instance of the class.
        @param func: (callable) The function to run as the task.
        @param args: (tuple) Arguments to pass to the function.
        @param on_success: (callback) Optional callback to run on the main thread after successful completion of the task.
        '''

        self._set_busy_state(True)
        threading.Thread(target=self.worker, args=(func, args, on_success), daemon=True).start()


    def worker(self, func, args, on_success=None):
        '''
        @brief Run a task in a worker thread and handle its outcome.

        @details Executes the task, logs its outcome, and schedules GUI updates on the main thread.
        It also ensures that the busy state of the GUI is properly managed.

        @param self: (MainFrame) The instance of the class.
        @param func: (Any) The function to run as the task.
        @param args: (Tuple) Arguments to pass to the function.
        @param on_success: (Callable) Optional callback to run on the main thread after successful completion of the task.
        '''

        self.log(f"Running {func.__name__}...")

        try:
            func(*args)
            self.log(f"{func.__name__} completed.")
            if on_success:
                wx.CallAfter(on_success)

        except Exception as e:
            logger.exception("Task %s failed", func.__name__)
            self.log(f"{func.__name__} failed: {e}")
            wx.CallAfter(wx.MessageBox, str(e), "Error", wx.ICON_ERROR)
        finally:
            wx.CallAfter(self._set_busy_state, False)


## @name Entry Point
# @{
def run_gui():
    '''
    @brief Entry point to run the GUI application.

    @details This function initializes the wx.App, creates the main frame, and starts the main event loop.
    '''

    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()

## @}
