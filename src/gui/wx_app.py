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
from datetime import datetime                               # for handling date and time

# Third Party Modules
import wx                                                   # for wxPython GUI components

# Local Module Methods
from src.core.logging_config import add_module_handler      # for adding module-specific logging handlers
from src.core.logging_config import bootstrap_logging       # for package logging startup

# Local Module Constants
from src.core.constants import AUDIO_EXTS                   # for audio file extensions
from src.core.constants import MUSIC_TLD                    # top level directory for music files
from src.core.constants import PLAYLIST_EXTS                # supported playlist file extensions
from src.core.constants import RESULT_DIR                   # directory for storing test results
from src.core.constants import RESULT_EXT                   # file extension for result files
from src.core.paths import GENERATED_PATH                   # for generated files path

# MUST configure logging before importing modules that register logging handlers
# applies because of EventHandlers importing modules that call add_module_handler at module scope
# also, this module must configure logging first to to protect itself from early logging issues
# imports after executable code require noqa: E402 (module import after code) to stop error warning
bootstrap_logging()

# Local Module Classes
from src.controllers.task_runner import TaskRunner          # noqa: E402, for running tasks outside the GUI thread
from src.gui.handlers import EventHandlers                  # noqa: E402, event handlers for the GUI
from src.models.audio_info.audio_art import AudioArt        # noqa: E402, for GUI audio-art operations
from src.models.audio_info.audio_metadata import AudioMetadata  # noqa: E402, for GUI audio-metadata operations
from src.models.audio_info.audio_playlist import AudioPlaylist  # noqa: E402, for GUI playlist operations
from src.models.audio_normalize.audio_normalization import AudioNormalization  # noqa: E402, for GUI normalization
from src.models.dir_processing.directory_processing import DirectoryProcessing  # noqa: E402, for GUI directory operations

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

    @retval time_stamp {str} A string representing the current timestamp in the format "YYYY-MM-DD HH:MM:SS".

    @exception e_error {Exception} A common baseclass exception to handle unforeseen errors.
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

    eventHandlers: EventHandlers                            # Event handler instance for GUI events
    taskRunner: TaskRunner                                  # Task runner instance for executing background tasks

    mainLog: wx.TextCtrl                                    # Text control for displaying main log messages
    mainNotebook: wx.Notebook                               # Notebook for tabbed panels within the main splitter window
    mainPanel: wx.Panel                                     # Main panel within the frame
    mainSplitter: wx.SplitterWindow                         # Splitter window dividing the main panel and log area

    artTab: wx.Panel                                        # Panel for audio art processing
    convertTab: wx.Panel                                    # Panel for audio conversion
    levelTab: wx.Panel                                      # Panel for audio level normalization
    playlistTab: wx.Panel                                   # Panel for audio playlist processing
    infoTab: wx.Panel                                       # Panel for audio & metadata information
    dirTab: wx.Panel                                        # Panel for directory processing

    extractArtTld: wx.TextCtrl                              # Text control input for directory art extraction path input
    extractDirBrowse: wx.Button                             # Button control for browsing extract walk path
    extractArtChoice: wx.Choice                             # Choice control for selecting directory art extraction from audio with extension
    extractDirArt: wx.Button                                # Button control for extracting directory art

    extractArtPath: wx.TextCtrl                             # Text control input for file art extraction path input
    extractFileBrowse: wx.Button                            # Button control for browsing file art extraction path
    extractFileArt: wx.Button                               # Button control for extracting file art

    setArtTld: wx.TextCtrl                                  # Text control input for setting album art path input
    setArtBrowse: wx.Button                                 # Button control for browsing set album art path

    convertWalkTld: wx.TextCtrl                             # Text control input for convert walk path input
    convertWalkBrowse: wx.Button                            # Button control for browsing convert walk path
    convertAudioChoice: wx.Choice                           # Choice control for selecting audio file extension to use in convert walk
    convertDirAudio: wx.Button                              # Button control for converting directory audio

    convertAudioPath: wx.TextCtrl                           # Text control input for file audio conversion path input
    convertFileBrowse: wx.Button                            # Button control for browsing file audio conversion path
    convertAudioFile: wx.Button                             # Button control for converting file audio

    levelWalkTld: wx.TextCtrl                               # Text control input for level walk path input
    levelWalkBrowse: wx.Button                              # Button control for browsing level walk path
    levelAudioChoice: wx.Choice                             # Choice control for selecting level normalization type to use in leveling walk
    levelDirAudio: wx.Button                                # Button control for leveling directory audio

    ebuFilePath: wx.TextCtrl                                # Text control input for file EBU leveling path input
    ebuFileBrowse: wx.Button                                # Button control for browsing file EBU leveling path
    ebuLevelFile: wx.Button                                 # Button control for leveling EBU file

    peakFilePath: wx.TextCtrl                               # Text control input for file peak leveling path input
    peakLevelFile: wx.Button                                # Button control for leveling peak file
    peakFileBrowse: wx.Button                               # Button control for browsing file peak leveling path

    rmsFilePath: wx.TextCtrl                                # Text control input for file RMS leveling path input
    rmsLevelFile: wx.Button                                 # Button control for leveling RMS file
    rmsFileBrowse: wx.Button                                # Button control for browsing file RMS leveling path


    def __init__(
        self,
        parent=None,
        *,
        art: AudioArt,
        directory: DirectoryProcessing,
        metadata: AudioMetadata,
        normalization: AudioNormalization,
        playlist: AudioPlaylist
    ):
        '''
        @brief Initialize the MainFrame class.

        @details This constructor sets up the main window, including the layout, panels, and event handlers.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window, if any.
        @param art {AudioArt} The audio-art model instance.
        @param directory {DirectoryProcessing} The directory-processing model instance.
        @param metadata {AudioMetadata} The audio-metadata model instance.
        @param normalization {AudioNormalization} The audio-normalization model instance.
        @param playlist {AudioPlaylist} The audio-playlist model instance.
        '''

        # initialize the main frame with the specified parent, title, and size
        super().__init__(parent, title="Music Processing", size=(960, 760))

        # Initialize event handlers
        self.eventHandlers = EventHandlers(self, art, directory, metadata, normalization, playlist)

        # create the background task runner with callbacks for GUI updates
        self.taskRunner = TaskRunner(log=self.log, call_after=wx.CallAfter, set_busy_state=self.set_busy, show_error=self.show_error)

        # increase font size by 2 points
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(font.GetPointSize() + 2)
        self.SetFont(font)

        # create the main panel within the frame
        self.mainPanel = wx.Panel(self, name="mainPanel")
        self.mainPanel.SetFont(font)

        # create splitter window for resizable notebook/log split
        self.mainSplitter = wx.SplitterWindow(self.mainPanel, style=wx.SP_LIVE_UPDATE, name="mainSplitter")

        # create the notebook for tabbed panels within the splitter window
        self.mainNotebook = wx.Notebook(self.mainSplitter, name="mainNotebook")

        # create the individual panels for each tab in the notebook
        self.artTab = self._create_art_tab(self.mainNotebook)
        self.convertTab = self._create_convert_tab(self.mainNotebook)
        self.levelTab = self._create_level_tab(self.mainNotebook)
        self.playlistTab = self._create_playlist_tab(self.mainNotebook)
        self.infoTab = self._create_info_tab(self.mainNotebook)
        self.dirTab = self._create_dir_tab(self.mainNotebook)

        # add the created panels to the notebook as separate tabs, displayed from left to right in the order they are added
        self.mainNotebook.AddPage(self.artTab, "Art Processing")
        self.mainNotebook.AddPage(self.convertTab, "Audio Conversion")
        self.mainNotebook.AddPage(self.levelTab, "Audio Leveling")
        self.mainNotebook.AddPage(self.playlistTab, "Playlist Processing")
        self.mainNotebook.AddPage(self.dirTab, "Directory Processing")
        self.mainNotebook.AddPage(self.infoTab, "Information")

        # create the log control for displaying log messages
        self.mainLog = wx.TextCtrl(self.mainSplitter, style=wx.HSCROLL | wx.TE_MULTILINE | wx.TE_READONLY, value="", name="mainLog")

        # split horizontally: notebook on top, log on bottom
        self.mainSplitter.SplitHorizontally(self.mainNotebook, self.mainLog)
        # Initial sash position in pixels from top
        sash_position = self.Size.height // 2
        self.mainSplitter.SetSashPosition(sash_position)

        # set up the main sizer for the panel and add the splitter window to it
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.mainSplitter, 1, wx.EXPAND)
        self.mainPanel.SetSizer(mainSizer)
        self.Maximize()


    def _create_art_tab(self, parent) -> wx.Panel:
        '''
        @brief This panel contains album art extraction and setting controls.

        @details Stacks the extraction sections at left and places the setting section to their right.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the panel.

        @retval panel (wx.Panel) The created art panel.
        '''

        panel = wx.Panel(parent, name="artTab")
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        grid = wx.GridBagSizer(8, 8)

        # create the sizers for the art tab panel
        artDirSizer = self._create_art_dir_sizer(panel)
        setAlbumArtSizer = self._create_art_set_album_sizer(panel)
        fileArtSizer = self._create_art_file_sizer(panel)

        # vertically stack the directory extraction and album art setting sections
        grid.Add(artDirSizer, pos=(0, 0), flag=wx.ALL | wx.EXPAND, border=4)
        grid.Add(setAlbumArtSizer, pos=(1, 0), flag=wx.ALL | wx.EXPAND, border=4)
        # horizontally place the file extraction section to the right of the directory extraction and album art sections
        grid.Add(fileArtSizer, pos=(0, 1), span=(2, 1), flag=wx.ALL | wx.EXPAND, border=4)

        # make both columns growable so that the sizers expand properly when the panel is resized
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 1)

        panel.SetSizer(grid)

        return panel


    def _create_art_dir_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Creates the bulk directory art extraction section.

        @details Provides directory selection, file type filtering, and extraction controls.

        @param self {MainFrame} The instance of the class.
        @param parent {wx.Panel} The parent panel for the section.

        @retval bulkSizer {wx.StaticBoxSizer} The sizer containing the extraction controls.
        '''

        bulkPanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box, sizers, and panel for the bulk directory art extraction section
        bulkBox = wx.StaticBox(parent, label="Directory Art Extraction")
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label and file type selection
        briefDesc = wx.StaticText(bulkPanel, label="Extracts album art from all audio files in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="The extracted album art will be saved alongside the audio files")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path tld or fld:")
        fileTypeLabel = wx.StaticText(bulkPanel, label="Extract from Audio Ext:")

        # create controls for selecting the starting path for bulk extraction
        self.extractArtTld, self.extractDirBrowse = self._make_path_controls(bulkPanel)
        self.extractArtTld.Name = "extractArtTld"
        self.extractDirBrowse.Name = "extractDirBrowse"
        self.extractDirBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.extractArtTld))

        # file type drop list for bulk conversion
        file_types = ["Any file type"] + AUDIO_EXTS
        self.extractArtChoice = wx.Choice(bulkPanel, choices=file_types, name="extractArtChoice")
        self.extractArtChoice.SetSelection(0)
        self.extractArtChoice.SetToolTip("Select audio file type or 'Any file type' to process all supported audio files")

        # create the extraction button
        self.extractDirArt = wx.Button(bulkPanel, label="Extract Directory Art", name="extractDirArt")
        self.extractDirArt.Bind(wx.EVT_BUTTON, self.eventHandlers.on_extract_directory_art)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # add controls for the starting path to the grid layout
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.extractArtTld, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.extractDirBrowse, pos=(2, 3), flag=wx.EXPAND)

        # add controls for selecting the file type pattern and extraction button to the grid layout
        bulkGrid.Add(fileTypeLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.extractArtChoice, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.extractDirArt, pos=(3, 3))

        # make the second column growable to allow the controls to expand properly
        bulkGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        bulkPanel.SetSizer(bulkGrid)
        bulkSizer.Add(bulkPanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return bulkSizer


    def _create_art_file_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Creates the specific file art extraction section.

        @details Provides audio file selection and art extraction controls.

        @param self {MainFrame} The instance of the class.
        @param parent {wx.Panel} The parent panel for the section.

        @retval fileSizer {wx.StaticBoxSizer} The sizer containing the extraction controls.
        '''

        filePanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        fileGrid = wx.GridBagSizer(8, 8)

        # create the static box, sizer, and panel for the file art extraction section
        fileBox = wx.StaticBox(parent, label="File Art Extraction")
        fileSizer = wx.StaticBoxSizer(fileBox, wx.VERTICAL)
        filePanel = wx.Panel(parent)
        fileGrid = wx.GridBagSizer(8, 8)

        # create static text for describing section & audio file path label
        briefDesc = wx.StaticText(filePanel, label="Extracts album art from specific audio file")
        resultDesc = wx.StaticText(filePanel, label="The extracted album art will be saved alongside the audio file")
        audioFilePathLabel = wx.StaticText(filePanel, label="Audio file path:")

        # create path input and browse button controls for selecting the audio file
        wildcard_exts = "Audio files (*.flac;*.mp3;*.m4a;*.wma)|*.flac;*.mp3;*.m4a;*.wma"
        self.extractArtPath, self.extractFileBrowse = self._make_path_controls(filePanel)
        self.extractArtPath.Name = "extractArtPath"
        self.extractFileBrowse.Name = "extractFileBrowse"
        self.extractFileBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.extractArtPath, wildcard_exts))

        # create the extract file art button
        self.extractFileArt = wx.Button(filePanel, label="Extract File Art")
        self.extractFileArt.Bind(wx.EVT_BUTTON, self.eventHandlers.on_extract_file_art)

        # create a horizontal sizer for the file path and extract buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.extractFileBrowse, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.extractFileArt, 0)

        # create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.extractArtPath, 1, wx.EXPAND | wx.RIGHT, 8)
        pathRowSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # add info text controls to the grid layout
        fileGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        fileGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # add the path row to the grid layout
        fileGrid.Add(audioFilePathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(pathRowSizer, pos=(2, 1), span=(1, 3), flag=wx.EXPAND)

        # make the second column growable to allow the controls to expand properly
        fileGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        filePanel.SetSizer(fileGrid)
        fileSizer.Add(filePanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return fileSizer


    def _create_art_set_album_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Creates the bulk directory album art setting section.

        @details Provides directory selection and album art setting controls.

        @param self {MainFrame} The instance of the class.
        @param parent {wx.Panel} The parent panel for the section.

        @retval setBulkSizer {wx.StaticBoxSizer} The sizer containing the setting controls.
        '''

        bulkPanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # Create the static box, sizer, and panel for the album art setting section
        bulkBox = wx.StaticBox(parent, label="Set Album Art")
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label
        briefDesc = wx.StaticText(bulkPanel, label="Sets album art file for an album directory from project source folder")
        detailDesc = wx.StaticText(bulkPanel, label="Copies a matching AlbumArt JPEG into the album directory when it is available")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path tld or fld:")

        # create controls for selecting the starting path for setting album art
        self.setArtTld, self.setArtBrowse = self._make_path_controls(bulkPanel)
        self.setArtTld.Name = "setArtTld"
        self.setArtBrowse.Name = "setArtBrowse"
        self.setArtBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.setArtTld))

        # create the set album art button
        setAlbumArt = wx.Button(bulkPanel, label="Set Album Art")
        setAlbumArt.Bind(wx.EVT_BUTTON, self.eventHandlers.on_set_album_art)

        # create a horizontal sizer for the browse and setting buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.setArtBrowse, 0, wx.RIGHT, 8)
        buttonSizer.Add(setAlbumArt, 0)

        # create a horizontal sizer for the starting path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.setArtTld, 1, wx.EXPAND | wx.RIGHT, 8)
        pathRowSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # add the info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 4), flag=wx.EXPAND)
        bulkGrid.Add(detailDesc, pos=(1, 0), span=(1, 4), flag=wx.EXPAND)

        # add the starting path controls to the grid layout
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(pathRowSizer, pos=(2, 1), span=(1, 3), flag=wx.EXPAND)

        # make the second column growable to allow the controls to expand properly
        bulkGrid.AddGrowableCol(1)
        bulkPanel.SetSizer(bulkGrid)
        bulkSizer.Add(bulkPanel, 1, wx.EXPAND | wx.ALL, 4)

        return bulkSizer


    def _create_convert_tab(self, parent) -> wx.Panel:
        '''
        @brief This panel includes controls for audio file conversion

        @details This panel is organized into nested subpanels for bulk directory processing and specific file processing.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the panel.

        @retval panel {wx.Panel} The created convert panel.
        '''

        panel = wx.Panel(parent, name="convertTab")
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        grid = wx.GridBagSizer(8, 8)

        # create the sizers for conversion tab panel
        convertDirSizer = self._create_convert_dir_sizer(panel)
        convertFileSizer = self._create_convert_file_sizer(panel)

        # horizontally order the directory and file conversion sections in the main grid
        grid.Add(convertDirSizer, pos=(0, 0), flag=wx.ALL | wx.EXPAND, border=4)
        grid.Add(convertFileSizer, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=4)

        # make both columns growable so that the sizers expand properly when the panel is resized
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 1)

        panel.SetSizer(grid)

        return panel


    def _create_convert_dir_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk directory audio conversion section.

        @details Provides directory selection, file type filtering, and conversion controls.

        @param self {MainFrame} The instance of the class.
        @param parent {wx.Panel} The parent window for the sizer.

        @retval bulkSizer {wx.Sizer} The created sizer for directory audio conversion.
        '''

        bulkPanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box, sizers, and panel for the bulk directory audio conversion section
        bulkBox = wx.StaticBox(parent, label="Directory Audio Conversion")
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label and file type selection
        briefDesc = wx.StaticText(bulkPanel, label="Converts all audio files in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="The converted files will be saved in project default output location")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path tld or fld:")
        fileTypeLabel = wx.StaticText(bulkPanel, label="Convert from Audio Ext:")

        # create controls for selecting the starting path for bulk conversion
        self.convertWalkTld, self.convertWalkBrowse = self._make_path_controls(bulkPanel)
        self.convertWalkTld.Name = "convertWalkTld"
        self.convertWalkBrowse.Name = "convertWalkBrowse"
        self.convertWalkBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.convertWalkTld))

        # file type drop list for bulk conversion
        file_types = ["Any file type"] + AUDIO_EXTS
        self.convertAudioChoice = wx.Choice(bulkPanel, choices=file_types, name="convertAudioChoice")
        self.convertAudioChoice.SetSelection(0)
        self.convertAudioChoice.SetToolTip("Select audio file type or 'Any file type' to process all supported audio files")

        # create the conversion button
        self.convertDirAudio = wx.Button(bulkPanel, label="Convert Directory Audio")
        self.convertDirAudio.Bind(wx.EVT_BUTTON, self.eventHandlers.on_convert_directory_audio)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.convertWalkTld, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.convertWalkBrowse, pos=(2, 3), flag=wx.EXPAND)

        # order the file type pattern controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(fileTypeLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.convertAudioChoice, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.convertDirAudio, pos=(3, 3))

        # make the second column growable to allow the controls to expand properly
        bulkGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        bulkPanel.SetSizer(bulkGrid)
        bulkSizer.Add(bulkPanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return bulkSizer


    def _create_convert_file_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the specific file audio conversion section.

        @details Provides audio file selection and audio conversion controls.

        @param self {MainFrame} The instance of the class.
        @param parent {wx.Panel} The parent panel for the sizer.

        @retval fileSizer {wx.StaticBoxSizer} The created sizer for specific audio file conversion.
        '''

        filePanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        fileGrid = wx.GridBagSizer(8, 8)

        # create the static box, sizer, and panel for the specific audio file conversion section
        fileBox = wx.StaticBox(parent, label="Convert Audio File")
        fileSizer = wx.StaticBoxSizer(fileBox, wx.VERTICAL)

        # create static text for describing section & audio path label
        briefDesc = wx.StaticText(filePanel, label="Convert specific audio file")
        resultDesc = wx.StaticText(filePanel, label="The converted file will be saved in project default output location")
        audioPathLabel = wx.StaticText(filePanel, label="Audio file path:")

        # create path input and browse button controls for selecting the audio file
        wildcard_exts = "Audio files (*.flac;*.mp3;*.m4a;*.wma)|*.flac;*.mp3;*.m4a;*.wma"
        self.convertAudioPath, self.convertFileBrowse = self._make_path_controls(filePanel)
        self.convertAudioPath.Name = "convertAudioPath"
        self.convertFileBrowse.Name = "convertAudioBrowse"
        self.convertFileBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.convertAudioPath, wildcard_exts))

        # create the convert audio file button
        self.convertAudioFile = wx.Button(filePanel, label="Convert Audio File")
        self.convertAudioFile.Bind(wx.EVT_BUTTON, self.eventHandlers.on_convert_file_audio)

        # create a horizontal sizer for the browse and convert buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.convertFileBrowse, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.convertAudioFile, 0)

        # create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.convertAudioPath, 1, wx.EXPAND | wx.RIGHT, 8)
        pathRowSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # add info text controls to the grid layout
        fileGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        fileGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # add the path row to the grid layout
        fileGrid.Add(audioPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(pathRowSizer, pos=(2, 1), span=(1, 3), flag=wx.EXPAND)

        # make the second column growable to allow the controls to expand properly
        fileGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        filePanel.SetSizer(fileGrid)
        fileSizer.Add(filePanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return fileSizer


    def _create_level_tab(self, parent) -> wx.Panel:
        '''
        @brief This panel includes controls for audio file leveling.

        @details This panel is organized into nested subpanels for bulk directory processing and specific file processing.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the panel.

        @retval panel {wx.Panel} The created leveling panel.
        '''

        panel = wx.Panel(parent, name="levelTab")
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        grid = wx.GridBagSizer(8, 8)

        #  create the sizers for level tab panel
        levelDirSizer = self._create_level_dir_sizer(panel)
        levelFileSizer = self._create_level_file_sizer(panel)

        # order the sub panels side by side in the main grid
        grid.Add(levelDirSizer, pos=(0, 0), flag=wx.ALL | wx.EXPAND, border=4)
        grid.Add(levelFileSizer, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=4)

        # make both columns growable so that the sizers expand properly when the panel is resized
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 1)

        panel.SetSizer(grid)

        return panel


    def _create_level_dir_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk directory audio leveling sizer.

        @details Provides directory selection, leveling type filtering, and leveling controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the sizer.

        @retval sizer {wx.StaticBoxSizer} The created sizer for directory audio leveling.
        '''

        bulkPanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box, sizers, and panel for the bulk directory audio conversion section
        bulkBox = wx.StaticBox(parent, label="Directory Audio Leveling")
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label and leveling type selection
        briefDesc = wx.StaticText(bulkPanel, label="Levels all audio files in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="The leveled files will be saved in project default output location")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path tld or fld:")
        levelTypeLabel = wx.StaticText(bulkPanel, label="Level Audio Type:")

        # create controls for selecting the starting path for bulk leveling
        self.levelWalkTld, self.levelWalkBrowse = self._make_path_controls(bulkPanel)
        self.levelWalkTld.Name = "levelWalkTld"
        self.levelWalkBrowse.Name = "levelWalkBrowse"
        self.levelWalkBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.levelWalkTld))

        # level type drop list for bulk leveling
        level_types = ["ebu", "peak", "rms"]
        self.levelAudioChoice = wx.Choice(bulkPanel, choices=level_types, name="levelAudioChoice")
        self.levelAudioChoice.SetSelection(0)
        self.levelAudioChoice.SetToolTip("Select normalization type: ebu (loudness), peak (peak level), or rms (RMS level)")

        # create the leveling button
        self.levelDirAudio = wx.Button(bulkPanel, label="Level Directory Audio")
        self.levelDirAudio.Bind(wx.EVT_BUTTON, self.eventHandlers.on_level_directory_audio)

        #  add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.levelWalkTld, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.levelWalkBrowse, pos=(2, 3), flag=wx.EXPAND)

        # order the file type pattern controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(levelTypeLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.levelAudioChoice, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.levelDirAudio, pos=(3, 3))

        # make the second column growable to allow the controls to expand properly
        bulkGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        bulkPanel.SetSizer(bulkGrid)
        bulkSizer.Add(bulkPanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return bulkSizer


    def _create_level_file_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the specific file audio leveling section.

        @details Provides audio file selection and audio leveling controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent panel for the sizer.

        @retval fileSizer {wx.StaticBoxSizer} The created static box sizer for leveling file audio controls.
        '''

        filePanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        fileGrid = wx.GridBagSizer(8, 8)

        # create the static box, sizer, and panel for the specific audio conversion section
        filesBox = wx.StaticBox(parent, label="Level Audio Files")
        fileSizer = wx.StaticBoxSizer(filesBox, wx.VERTICAL)

        # create static text for describing section & audio path labels
        briefDesc = wx.StaticText(filePanel, label="Level specific audio file by normalization type")
        resultDesc = wx.StaticText(filePanel, label="The leveled file will be saved in project default output location")
        ebuLabel = wx.StaticText(filePanel, label="File to EBU normalize:")
        peakLabel = wx.StaticText(filePanel, label="File to Peak normalize:")
        rmsLabel = wx.StaticText(filePanel, label="File to RMS normalize:")

        # create path input and browse button controls for selecting the audio files
        wildcard_mp3 = "MP3 Audio files (*.mp3)|*.mp3"

        self.ebuFilePath, self.ebuFileBrowse = self._make_path_controls(filePanel)
        self.ebuFilePath.Name = "ebuFilePath"
        self.ebuFileBrowse.Name = "ebuFileBrowse"
        self.ebuFileBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.ebuFilePath, wildcard_mp3))

        self.peakFilePath, self.peakFileBrowse = self._make_path_controls(filePanel)
        self.peakFilePath.Name = "peakFilePath"
        self.peakFileBrowse.Name = "peakFileBrowse"
        self.peakFileBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.peakFilePath, wildcard_mp3))

        self.rmsFilePath, self.rmsFileBrowse = self._make_path_controls(filePanel)
        self.rmsFilePath.Name = "rmsFilePath"
        self.rmsFileBrowse.Name = "rmsFileBrowse"
        self.rmsFileBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.rmsFilePath, wildcard_mp3))

        # create the single file leveling buttons
        self.ebuLevelFile = wx.Button(filePanel, label="Level EBU File")
        self.ebuLevelFile.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_ebu_file(evt, self.ebuFilePath, "ebu"))

        self.peakLevelFile = wx.Button(filePanel, label="Level Peak File")
        self.peakLevelFile.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_peak_file(evt, self.peakFilePath, "peak"))

        self.rmsLevelFile = wx.Button(filePanel, label="Level RMS File")
        self.rmsLevelFile.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_rms_file(evt, self.rmsFilePath, "rms"))

        # add info text controls to the grid layout
        fileGrid.Add(briefDesc, pos=(0, 0), span=(1, 4), flag=wx.EXPAND)
        fileGrid.Add(resultDesc, pos=(1, 0), span=(1, 4), flag=wx.EXPAND)

        # add path rows with shared columns to keep controls aligned
        fileGrid.Add(ebuLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.ebuFilePath, pos=(2, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.ebuFileBrowse, pos=(2, 2), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.ebuLevelFile, pos=(2, 3), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

        fileGrid.Add(peakLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.peakFilePath, pos=(3, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.peakFileBrowse, pos=(3, 2), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.peakLevelFile, pos=(3, 3), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

        fileGrid.Add(rmsLabel, pos=(4, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.rmsFilePath, pos=(4, 1), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.rmsFileBrowse, pos=(4, 2), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.rmsLevelFile, pos=(4, 3), flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

        # make the second column growable to allow the controls to expand properly
        fileGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        filePanel.SetSizer(fileGrid)
        fileSizer.Add(filePanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return fileSizer


    def _create_playlist_tab(self, parent) -> wx.Panel:
        '''
        @brief Create the playlist panel.

        @details This panel provides controls for updating M3U playlists and performing directory walks.<br>
        It includes nested subpanels for updating a specific playlist file and for walking a directory tree.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the panel.

        @retval panel {wx.Panel} The created playlist panel.
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
        bulk_btn.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.bulk_tld))

        # execute button for updating playlist walk
        bulk_exec = wx.Button(bulk_subpanel, label="Update Directory Playlist")
        bulk_exec.Bind(wx.EVT_BUTTON, self.eventHandlers.on_update_walk)

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
        update_m3u_file_btn.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.update_m3u_file, playlist_wildcard))

        # Execute button for updating M3U playlist
        update_m3u_exec = wx.Button(specific_subpanel, label="Update Playlist File")
        update_m3u_exec.Bind(wx.EVT_BUTTON, self.eventHandlers.on_update_m3u)

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
        grid.Add(bulk_sizer, pos=(0, 0), span=(1, 4), flag=wx.ALL | wx.EXPAND, border=4)
        grid.Add(specific_sizer, pos=(1, 0), span=(1, 4), flag=wx.ALL | wx.EXPAND, border=4)

        grid.AddGrowableCol(1)
        panel.SetSizer(grid)

        return panel


    def _create_dir_tab(self, parent) -> wx.Panel:
        '''
        @brief Create the directory panel.

        @details Provides controls for listing audio files, listing files by type, and removing empty albums or files matching a pattern.<br>
        It includes options for selecting top-level directories and specifying file extensions or patterns.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the panel.

        @retval panel {wx.Panel} The created directory panel.
        '''

        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        self.list_audio_tld, list_audio_btn = self._make_path_controls(panel)
        list_audio_btn.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.list_audio_tld))
        list_audio_exec = wx.Button(panel, label="List Audio")
        list_audio_exec.Bind(wx.EVT_BUTTON, self.eventHandlers.on_list_audio)

        self.list_type_tld, list_type_btn = self._make_path_controls(panel)
        list_type_btn.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.list_type_tld))
        self.list_type_ext = wx.TextCtrl(panel)
        list_type_exec = wx.Button(panel, label="List Type")
        list_type_exec.Bind(wx.EVT_BUTTON, self.eventHandlers.on_list_type)

        self.remove_albums_tld, remove_albums_btn = self._make_path_controls(panel)
        remove_albums_btn.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.remove_albums_tld))
        remove_albums_exec = wx.Button(panel, label="Remove Empty Albums")
        remove_albums_exec.Bind(wx.EVT_BUTTON, self.eventHandlers.on_remove_albums)

        self.remove_pattern_tld, remove_pattern_btn = self._make_path_controls(panel)
        remove_pattern_btn.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.remove_pattern_tld))
        self.remove_pattern_pattern = wx.TextCtrl(panel)
        remove_pattern_exec = wx.Button(panel, label="Remove Pattern")
        remove_pattern_exec.Bind(wx.EVT_BUTTON, self.eventHandlers.on_remove_pattern)

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


    def _create_info_tab(self, parent) -> wx.Panel:
        '''
        @brief Create the metadata panel.

        @details This panel provides controls for retrieving and displaying metadata from media files.<br>
        It includes options for tags walk, media info walk, and unique media extraction.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the panel.

        @retval panel {wx.Panel} The created metadata panel.
        '''

        panel = wx.Panel(parent)
        grid = wx.GridBagSizer(8, 8)

        self.tags_walk_tld, tags_walk_tld_btn = self._make_path_controls(panel)
        tags_walk_tld_btn.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.tags_walk_tld))
        self.tags_walk_pattern = wx.TextCtrl(panel)
        self.tags_walk_ffprobe = wx.CheckBox(panel, label="Use ffprobe")
        tags_walk_exec = wx.Button(panel, label="Get Tags Walk")
        tags_walk_exec.Bind(wx.EVT_BUTTON, self.eventHandlers.on_get_tags_walk)

        self.media_info_tld, media_info_btn = self._make_path_controls(panel)
        media_info_btn.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.media_info_tld))
        self.media_info_pattern = wx.TextCtrl(panel)
        media_info_exec = wx.Button(panel, label="Get Media Info Walk")
        media_info_exec.Bind(wx.EVT_BUTTON, self.eventHandlers.on_get_media_info_walk)

        self.unique_media_tld, unique_media_btn = self._make_path_controls(panel)
        unique_media_btn.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.unique_media_tld))
        unique_media_exec = wx.Button(panel, label="Get Unique Media")
        unique_media_exec.Bind(wx.EVT_BUTTON, self.eventHandlers.on_get_unique_media)

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


    def _make_path_controls(self, parent) -> (tuple[wx.TextCtrl, wx.Button]):
        '''
        @brief Helper function to create a standard set of path controls (text box and browse button).

        @details This function is used to create consistent path input controls across different panels in the application.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the controls.

        @retval path_controls {[wx.TextCtrl, wx.Button]} Tuple containing the text control and the browse button.
        '''

        #  create the text control for path input
        pathLabel = wx.TextCtrl(parent)
        pathLabel.SetToolTip("Enter a path or click Browse button")

        # create the browse button for selecting the path
        browseButton = wx.Button(parent, label="Browse")
        browseButton.SetToolTip("Browse for a path")

        path_controls = (pathLabel, browseButton)

        return path_controls


    def set_busy(self, busy: bool):
        '''
        @brief Set the busy state of the application.

        @details This method enables or disables the main window and log control based on the busy state.<br>
        It also changes the cursor to a wait cursor when busy and back to the default cursor when not busy.

        @param self {MainFrame} The instance of the class.
        @param busy {bool} True to set the application to busy state, False to set it to idle state.
        '''

        self.Enable(not busy)
        self.mainLog.Enable(True)
        self.SetCursor(wx.Cursor(wx.CURSOR_WAIT if busy else wx.CURSOR_ARROW))


    def show_generated_files(self):
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

        wx.CallAfter(self.mainLog.SetValue, f"=== {filename + RESULT_EXT} ===\n{content}")


    def _move_files(self, file_paths, dest_dir):
        '''
        @brief Move selected files to the specified destination directory and display a summary of the operation.

        @details This method attempts to move each file in the provided list of file paths to the specified destination directory.

        @param self {MainFrame} The instance of the class.
        @param file_paths {list} A list of file paths to move.
        @param dest_dir {str} The destination directory to move the files to.

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

        wx.CallAfter(self.mainLog.AppendText, f"[{_timestamp()}] {message}\n")


    def show_error(self, message: str):
        '''
        @brief Display an error reported by a background task.

        @details Shows the task error in a GUI message box.

        @param self {MainFrame} The instance of the class.
        @param message {str} The task error message.
        '''

        wx.MessageBox(message, "Error", wx.ICON_ERROR)


    def show_message(self, message: str):
        '''
        @brief Display an informational message.

        @details Shows the message in a GUI message box.

        @param self {MainFrame} The instance of the class.
        @param message {str} The message to display.
        '''

        wx.MessageBox(message, "Info", wx.ICON_INFORMATION)


## @name Entry Point
# @{
def run_gui():
    '''
    @brief Entry point to run the GUI application.

    @details This function initializes the wx.App, creates the main frame, and starts the main event loop.
    '''

    app = wx.App(False)
    frame = MainFrame(
        art=AudioArt(),
        directory=DirectoryProcessing(),
        metadata=AudioMetadata(),
        normalization=AudioNormalization(),
        playlist=AudioPlaylist()
    )
    frame.Show()
    app.MainLoop()
## @}
