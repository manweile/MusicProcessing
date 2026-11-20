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

    # handlers and task runner instances
    eventHandlers: EventHandlers                            # Event handler instance for GUI events
    taskRunner: TaskRunner                                  # Task runner instance for executing background tasks

    # main UI components within the frame
    mainLog: wx.TextCtrl                                    # Text control for displaying main log messages
    mainNotebook: wx.Notebook                               # Notebook for tabbed panels within the main splitter window
    mainPanel: wx.Panel                                     # Main panel within the frame
    mainSplitter: wx.SplitterWindow                         # Splitter window dividing the main panel and log area

    # tabs within the main notebook
    # nameTab: wx.Panel                                       # Panel for folder & file name management
    artTab: wx.Panel                                        # Panel for audio art processing
    convertTab: wx.Panel                                    # Panel for audio conversion
    levelTab: wx.Panel                                      # Panel for audio level normalization
    playlistTab: wx.Panel                                   # Panel for audio playlist processing
    infoTab: wx.Panel                                       # Panel for audio & metadata information
    removalTab: wx.Panel                                    # Panel for file removal operations

    # folder & file name management
    # controls for directory adding missing album folders
    # addAlbumsWalkTld: wx.TextCtrl                           # Text control input for adding album folder top-level directory
    # addAlbumsWalkBrowse: wx.Button                          # Button control for browsing add album folder top-level directory
    # addAlbumsWalk: wx.Button                                # Button control for adding directory albums

    # controls for directory renaming existing album folders
    # renameAlbumsWalkTld: wx.TextCtrl                        # Text control input for renaming album folder top-level directory
    # renameAlbumsWalkBrowse: wx.Button                       # Button control for browsing rename album folder top-level directory
    # renameAlbumsWalk: wx.Button                             # Button control for renaming directory albums

    # controls for directory renaming files
    # renameFilesWalkTld: wx.TextCtrl                         # Text control input for renaming files top-level directory
    # renameFilesWalkBrowse: wx.Button                        # Button control for browsing rename files top-level directory
    # renameFilesWalk: wx.Button                              # Button control for renaming directory files

    # controls for specific file renaming
    # renameAudioFilePath: wx.TextCtrl                        # Text control input for specific file renaming
    # renameAudioFileBrowse: wx.Button                        # Button control for browsing specific file to rename
    # renameAudioFile: wx.Button                              # Button control for renaming specific file

    # controls for art file extraction & setting
    # controls for directory art files extraction
    extractArtDirTld: wx.TextCtrl                           # Text control input for directory art extraction path
    extractArtDirBrowse: wx.Button                          # Button control for browsing extract walk path
    extractArtDirChoice: wx.Choice                          # Choice control for selecting directory art extraction from audio with extension
    extractArtDir: wx.Button                                # Button control for extracting directory art

    # controls for specific file art extraction
    extractArtFilePath: wx.TextCtrl                         # Text control input for file art extraction path
    extractArtFileBrowse: wx.Button                         # Button control for browsing file art extraction path
    extractArtFile: wx.Button                               # Button control for extracting file art

    # controls for directory setting album art files
    setArtDirTld: wx.TextCtrl                               # Text control input for setting album art path
    setArtDirBrowse: wx.Button                              # Button control for browsing set album art path
    setArtDir: wx.Button                                    # Button control for setting directory album art

    # controls for audio file conversion
    # controls for directory audio files conversion
    convertAudioDirTld: wx.TextCtrl                         # Text control input for convert walk path
    convertAudioDirBrowse: wx.Button                        # Button control for browsing convert walk path
    convertAudioDirChoice: wx.Choice                        # Choice control for selecting audio file extension to use in convert walk
    convertAudioDir: wx.Button                              # Button control for converting directory audio

    # controls for specific file audio conversion
    convertAudioFilePath: wx.TextCtrl                       # Text control input for file audio conversion path
    convertAudioFileBrowse: wx.Button                       # Button control for browsing file audio conversion path
    convertAudioFile: wx.Button                             # Button control for converting file audio

    # controls for audio file leveling
    # controls for directory clip checking
    # clipCheckDirTld: wx.TextCtrl                            # Text control input for clip checking path
    # clipCheckDirBrowse: wx.Button                           # Button control for browsing clip checking walk path
    # clipCheckDir: wx.Button                                 # Button control for clip check on directory audio

    # controls for specific file clip checking
    # clipCheckFilePath: wx.TextCtrl                          # Text control input for the clip check file path
    # clipCheckFileBrowse: wx.Button                          # Button control for browsing file clip check path
    # clipCheckFile: wx.Button                                # Button control for performing the file clip check

    # controls for directory audio files leveling
    levelAudioDirTld: wx.TextCtrl                           # Text control input for level walk path input
    levelAudioDirBrowse: wx.Button                          # Button control for browsing level walk path
    levelAudioDirChoice: wx.Choice                          # Choice control for selecting level normalization type to use in leveling walk
    levelAudioDir: wx.Button                                # Button control for leveling directory audio

    # controls for specific file EBU leveling
    ebuFilePath: wx.TextCtrl                                # Text control input for file EBU leveling path input
    ebuFileBrowse: wx.Button                                # Button control for browsing file EBU leveling path
    ebuLevelFile: wx.Button                                 # Button control for leveling EBU file

    # controls for specific file peak leveling
    peakFilePath: wx.TextCtrl                               # Text control input for file peak leveling path input
    peakFileBrowse: wx.Button                               # Button control for browsing file peak leveling path
    peakLevelFile: wx.Button                                # Button control for leveling peak file

    # controls for specific file RMS leveling
    rmsFilePath: wx.TextCtrl                                # Text control input for file RMS leveling path input
    rmsFileBrowse: wx.Button                                # Button control for browsing file RMS leveling path
    rmsLevelFile: wx.Button                                 # Button control for leveling RMS file

    # controls for playlist file updating
    # controls for directory playlist files update
    playlistUpdateDirTld: wx.TextCtrl                       # Text control input for playlist update top-level directory
    playlistUpdateDirBrowse: wx.Button                      # Button control for browsing playlist update top-level directory
    playlistUpdateDir: wx.Button                            # Button control for updating directory playlist

    # controls for specific playlist file update
    updatePlaylistFilePath: wx.TextCtrl                     # Text control input for the playlist update file path
    updatePlaylistFileBrowse: wx.Button                     # Button control for browsing the playlist update file path
    updatePlaylistFile: wx.Button                           # Button control for updating the playlist file

    # controls for removal of folders & files
    # controls for removing empty album folders
    removeAlbumsDirTld: wx.TextCtrl                         # Text control input for the top-level directory for removing empty albums
    removeAlbumsDirBrowse: wx.Button                        # Button control for browsing the top-level directory for removing empty albums
    removeAlbumsDir: wx.Button                              # Button control for removing empty albums

    # controls for directory remove files by input pattern
    removePatternDirTld: wx.TextCtrl                        # Text control input for the top-level directory for pattern-based file removal
    removePatternDirBrowse: wx.Button                       # Button control for browsing the top-level directory for pattern-based file removal
    removePatternDirInput: wx.TextCtrl                      # Text control input for the pattern to remove
    removePatternDir: wx.Button                             # Button control for removing files based on the specified pattern

    # controls for directory remove files by set pattern
    removeListDirTld: wx.TextCtrl                           # Text control input for the top-level directory for list-based file removal
    removeListDirBrowse: wx.Button                          # Button control for browsing the top-level directory for list-based file removal
    removeListDir: wx.Button                                # Button control for removing files based on the specified list

    # controls for media & metadata information
    # controls for directory media inspection
    mediaInfoDirTld: wx.TextCtrl                           # Text control input media inspection walk path
    mediaInfoDirBrowse: wx.Button                          # Button control for browsing media inspection walk path
    mediaInfoDirChoice: wx.Choice                          # Choice control for selecting media file extension to use in media inspection walk
    mediaInfoDir: wx.Button                                # Button control for directory media inspection

    # controls for directory metadata inspection
    mediaTagsDirTld: wx.TextCtrl                            # Text control input for audio tag walk path
    mediaTagsDirBrowse: wx.Button                           # Button control for browsing audio tag walk path
    mediaTagDirChoice: wx.Choice                            # Choice control for selecting audio file extension to use in audio tag walk
    mediaTagsDir: wx.Button                                 # Button control for directory audio tag


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
        # self.nameTab = self._create_name_tab(self.mainNotebook)
        self.artTab = self._create_art_tab(self.mainNotebook)
        self.convertTab = self._create_convert_tab(self.mainNotebook)
        self.levelTab = self._create_level_tab(self.mainNotebook)
        self.playlistTab = self._create_playlist_tab(self.mainNotebook)
        self.removeTab = self._create_remove_tab(self.mainNotebook)
        self.infoTab = self._create_info_tab(self.mainNotebook)

        # add the created panels to the notebook as separate tabs, displayed from left to right in the order they are added
        # self.mainNotebook.AddPage(self.nameTab, "Name Management")
        self.mainNotebook.AddPage(self.artTab, "Art Processing")
        self.mainNotebook.AddPage(self.convertTab, "Audio Conversion")
        self.mainNotebook.AddPage(self.levelTab, "Audio Leveling")
        self.mainNotebook.AddPage(self.playlistTab, "Playlist Processing")
        self.mainNotebook.AddPage(self.removeTab, "Removal Processing")
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


    def _create_name_tab(self, parent) -> wx.Panel:
        '''
        @brief This panel contains album & song name management controls.

        @details This panel is organized into nested subpanels for bulk directory processing and specific file processing.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the panel.

        @retval panel (wx.Panel) The created name management panel.
        '''

        panel = wx.Panel(parent, name="nameTab")
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        grid = wx.GridBagSizer(8, 8)

        # create sizers for name tab panel as needed


        # order subpanels within the folder tab as needed


        # make columns growable so that the sizers expand properly when the panel is resized


        panel.SetSizer(grid)

        return panel


    def _create_rename_dir_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk directory rename audio files sizer.

        @details Provides directory selection and renaming controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent panel for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for bulk renaming audio files.
        '''

        # @note can be tld, or fld or sld (top-level directory, artist folder, or album folder)
        pass


    def _create_rename_file_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the specific audio file rename sizer.

        @details Provides file selection and renaming controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent panel for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for renaming specific audio files.
        '''

        pass


    def _create_add_folders_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk add missing album folders sizer.

        @details Provides directory selection and missing album folders addition controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent panel for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for adding missing album folders.
        '''

        # @note input path con ONLY be tld (top-level directory)
        pass


    def _create_rename_folders_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk rename incorrect album folders sizer.

        @details Provides directory selection and incorrect album folders renaming controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent panel for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for renaming incorrect album folders.
        '''

        # @note input path can ONLY be tld (top-level directory)
        pass


    def _create_art_tab(self, parent) -> wx.Panel:
        '''
        @brief This panel contains album art extraction and setting controls.

        @details This panel is organized into nested subpanels for bulk directory processing and specific file processing.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the panel.

        @retval panel (wx.Panel) The created art panel.
        '''

        panel = wx.Panel(parent, name="artTab")
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        grid = wx.GridBagSizer(8, 8)

        # create the sizers for the art tab panel
        artDirSizer = self._create_art_dir_sizer(panel)
        setAlbumArtSizer = self._create_art_set_sizer(panel)
        fileArtSizer = self._create_art_file_sizer(panel)

        # vertically stack the directory extraction and album art setting sections
        grid.Add(artDirSizer, pos=(0, 0), flag=wx.ALL | wx.EXPAND, border=4)
        grid.Add(setAlbumArtSizer, pos=(1, 0), flag=wx.ALL | wx.EXPAND, border=4)

        # horizontally place the file extraction section to the right of the directory extraction and album art sections
        grid.Add(fileArtSizer, pos=(0, 1), span=(2, 1), flag=wx.ALL | wx.EXPAND, border=4)

        # make columns growable so that the sizers expand properly when the panel is resized
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
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")
        fileTypeLabel = wx.StaticText(bulkPanel, label="Extract from Audio Ext:")

        # create controls for selecting the starting path for bulk extraction
        self.extractArtDirTld, self.extractArtDirBrowse = self._make_path_controls(bulkPanel)
        self.extractArtDirTld.Name = "extractArtDirTld"
        self.extractArtDirBrowse.Name = "extractArtDirBrowse"
        self.extractArtDirBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.extractArtDirTld))

        # file type drop list for bulk conversion
        file_types = ["Any file type"] + AUDIO_EXTS
        self.extractArtDirChoice = wx.Choice(bulkPanel, choices=file_types, name="extractArtDirChoice")
        self.extractArtDirChoice.SetSelection(0)
        self.extractArtDirChoice.SetToolTip("Select audio file type or 'Any file type' to process all supported audio files")

        # create the extraction button
        self.extractArtDir = wx.Button(bulkPanel, label="Extract All Art", name="extractArtDir")
        self.extractArtDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_extract_directory_art)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # add controls for the starting path to the grid layout
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.extractArtDirTld, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.extractArtDirBrowse, pos=(2, 3), flag=wx.EXPAND)

        # add controls for selecting the file type pattern and extraction button to the grid layout
        bulkGrid.Add(fileTypeLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.extractArtDirChoice, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.extractArtDir, pos=(3, 3))

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

        # create static text for describing section & audio file path label
        briefDesc = wx.StaticText(filePanel, label="Extracts album art from specific audio file")
        resultDesc = wx.StaticText(filePanel, label="The extracted album art will be saved alongside the audio file")
        audioFilePathLabel = wx.StaticText(filePanel, label="Audio file path:")

        # create path input and browse button controls for selecting the audio file
        wildcard_exts = "Audio files (*.flac;*.mp3;*.m4a;*.wma)|*.flac;*.mp3;*.m4a;*.wma"
        self.extractArtFilePath, self.extractArtFileBrowse = self._make_path_controls(filePanel)
        self.extractArtFilePath.Name = "extractArtFilePath"
        self.extractArtFileBrowse.Name = "extractArtFileBrowse"
        self.extractArtFileBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.extractArtFilePath, wildcard_exts))

        # create the extract file art button
        self.extractArtFile = wx.Button(filePanel, label="Extract File Art")
        self.extractArtFile.Bind(wx.EVT_BUTTON, self.eventHandlers.on_extract_file_art)

        # create a horizontal sizer for the file path and extract buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.extractArtFileBrowse, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.extractArtFile, 0)

        # create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.extractArtFilePath, 1, wx.EXPAND | wx.RIGHT, 8)
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


    def _create_art_set_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Creates the bulk directory album art setting section.

        @details Provides directory selection and album art setting controls.

        @param self {MainFrame} The instance of the class.
        @param parent {wx.Panel} The parent panel for the section.

        @retval bulkSizer {wx.StaticBoxSizer} The sizer containing the setting controls.
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
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")

        # create controls for selecting the starting path for setting album art
        self.setArtDirTld, self.setArtDirBrowse = self._make_path_controls(bulkPanel)
        self.setArtDirTld.Name = "setArtDirTld"
        self.setArtDirBrowse.Name = "setArtDirBrowse"
        self.setArtDirBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.setArtDirTld))

        # create the set album art button
        self.setArtDir = wx.Button(bulkPanel, label="Set Album Art", name="setArtDir")
        self.setArtDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_set_album_art)

        # create a horizontal sizer for the browse and setting buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.setArtDirBrowse, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.setArtDir, 0)

        # create a horizontal sizer for the starting path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.setArtDirTld, 1, wx.EXPAND | wx.RIGHT, 8)
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
        bulkSizer.Add(bulkPanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return bulkSizer


    def _create_convert_tab(self, parent) -> wx.Panel:
        '''
        @brief This panel contains audio file conversion controls.

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

        # make columns growable so that the sizers expand properly when the panel is resized
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

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for directory audio conversion.
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
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld or sld:")
        fileTypeLabel = wx.StaticText(bulkPanel, label="Convert from Audio Ext:")

        # create controls for selecting the starting path for bulk conversion
        self.convertAudioDirTld, self.convertAudioDirBrowse = self._make_path_controls(bulkPanel)
        self.convertAudioDirTld.Name = "convertAudioDirTld"
        self.convertAudioDirBrowse.Name = "convertAudioDirBrowse"
        self.convertAudioDirBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.convertAudioDirTld))

        # file type drop list for bulk conversion
        file_types = ["Any file type"] + AUDIO_EXTS
        self.convertAudioDirChoice = wx.Choice(bulkPanel, choices=file_types, name="convertAudioDirChoice")
        self.convertAudioDirChoice.SetSelection(0)
        self.convertAudioDirChoice.SetToolTip("Select audio file type or 'Any file type' to process all supported audio files")

        # create the conversion button
        self.convertAudioDir = wx.Button(bulkPanel, label="Convert All Audio", name="convertAudioDir")
        self.convertAudioDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_convert_directory_audio)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.convertAudioDirTld, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.convertAudioDirBrowse, pos=(2, 3), flag=wx.EXPAND)

        # order the file type pattern controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(fileTypeLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.convertAudioDirChoice, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.convertAudioDir, pos=(3, 3))

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
        self.convertAudioFilePath, self.convertAudioFileBrowse = self._make_path_controls(filePanel)
        self.convertAudioFilePath.Name = "convertAudioFilePath"
        self.convertAudioFileBrowse.Name = "convertAudioDirBrowse"
        self.convertAudioFileBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.convertAudioFilePath, wildcard_exts))

        # create the convert audio file button
        self.convertAudioFile = wx.Button(filePanel, label="Convert Audio File")
        self.convertAudioFile.Bind(wx.EVT_BUTTON, self.eventHandlers.on_convert_file_audio)

        # create a horizontal sizer for the browse and convert buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.convertAudioFileBrowse, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.convertAudioFile, 0)

        # create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.convertAudioFilePath, 1, wx.EXPAND | wx.RIGHT, 8)
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
        @brief This panel contains audio file leveling controls.

        @details This panel is organized into nested subpanels for bulk directory processing and specific file processing.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the panel.

        @retval panel {wx.Panel} The created leveling panel.
        '''

        panel = wx.Panel(parent, name="levelTab")
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        grid = wx.GridBagSizer(8, 8)

        # create the sizers for level tab panel
        levelDirSizer = self._create_level_dir_sizer(panel)
        levelFileSizer = self._create_level_file_sizer(panel)

        # order the sub panels side by side in the main grid
        grid.Add(levelDirSizer, pos=(0, 0), flag=wx.ALL | wx.EXPAND, border=4)
        grid.Add(levelFileSizer, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=4)

        # make columns growable so that the sizers expand properly when the panel is resized
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 1)

        panel.SetSizer(grid)

        return panel


    def _create_level_dir_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk directory audio leveling section.

        @details Provides directory selection, leveling type filtering, and leveling controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for directory audio leveling.
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
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")
        levelTypeLabel = wx.StaticText(bulkPanel, label="Level Audio Type:")

        # create controls for selecting the starting path for bulk leveling
        self.levelAudioDirTld, self.levelAudioDirBrowse = self._make_path_controls(bulkPanel)
        self.levelAudioDirTld.Name = "levelAudioDirTld"
        self.levelAudioDirBrowse.Name = "levelAudioDirBrowse"
        self.levelAudioDirBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.levelAudioDirTld))

        # level type drop list for bulk leveling
        level_types = ["ebu", "peak", "rms"]
        self.levelAudioDirChoice = wx.Choice(bulkPanel, choices=level_types, name="levelAudioDirChoice")
        self.levelAudioDirChoice.SetSelection(0)
        self.levelAudioDirChoice.SetToolTip("Select normalization type: ebu (loudness), peak (peak level), or rms (RMS level)")

        # create the leveling button
        self.levelAudioDir = wx.Button(bulkPanel, label="Level All Audio", name="levelAudioDir")
        self.levelAudioDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_level_directory_audio)

        #  add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.levelAudioDirTld, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.levelAudioDirBrowse, pos=(2, 3), flag=wx.EXPAND)

        # order the file type pattern controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(levelTypeLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.levelAudioDirChoice, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.levelAudioDir, pos=(3, 3))

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
        self.ebuLevelFile.Bind(wx.EVT_BUTTON, self.eventHandlers.on_ebu_file)

        self.peakLevelFile = wx.Button(filePanel, label="Level Peak File")
        self.peakLevelFile.Bind(wx.EVT_BUTTON, self.eventHandlers.on_peak_file)

        self.rmsLevelFile = wx.Button(filePanel, label="Level RMS File")
        self.rmsLevelFile.Bind(wx.EVT_BUTTON, self.eventHandlers.on_rms_file)

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
        @brief This panels contains playlist updating controls

        @details This panel is organized into nested subpanels for bulk directory processing and specific file processing.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the panel.

        @retval panel {wx.Panel} The created playlist panel.
        '''

        panel = wx.Panel(parent, name="playlistTab")
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        grid = wx.GridBagSizer(8, 8)

        # create the sizers for level tab panel
        playlistDirSizer = self._create_playlist_dir_sizer(panel)
        playlistFileSizer = self._create_playlist_file_sizer(panel)

        # order the sub panels side by side in the main grid
        grid.Add(playlistDirSizer, pos=(0, 0), flag=wx.ALL | wx.EXPAND, border=4)
        grid.Add(playlistFileSizer, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=4)

        # make columns growable so that the sizers expand properly when the panel is resized
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 1)

        panel.SetSizer(grid)

        return panel


    def _create_playlist_dir_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk directory playlist update section.

        @details Provides directory selection and playlist update controls.

        @param self {MainFrame} The instance of the class.
        @param parent {wx.Panel} The parent panel for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for directory playlist updates.
        '''

        bulkPanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box, sizers, and panel for the bulk directory playlist update section
        bulkBox = wx.StaticBox(parent, label="Directory Playlist Update")
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label
        briefDesc = wx.StaticText(bulkPanel, label="Updates all playlist files in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="The updated playlists will be saved in project default output location")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld only:")

        # create controls for selecting the starting path for bulk updating
        self.playlistUpdateDirTld, self.playlistUpdateDirBrowse = self._make_path_controls(bulkPanel)
        self.playlistUpdateDirTld.Name = "playlistUpdateDirTld"
        self.playlistUpdateDirBrowse.Name = "playlistUpdateDirBrowse"
        self.playlistUpdateDirBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.playlistUpdateDirTld))

        # create the update playlist button
        self.playlistUpdateDir = wx.Button(bulkPanel, label="Update All Playlists", name="playlistUpdateDir")
        self.playlistUpdateDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_update_walk)

        # create a horizontal sizer for the browse and convert buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.playlistUpdateDirBrowse, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.playlistUpdateDir, 0)

        # create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.playlistUpdateDirTld, 1, wx.EXPAND | wx.RIGHT, 8)
        pathRowSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory update subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(pathRowSizer, pos=(2, 1), span=(1, 3), flag=wx.EXPAND)

        # make the second column growable to allow the controls to expand properly
        bulkGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        bulkPanel.SetSizer(bulkGrid)
        bulkSizer.Add(bulkPanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return bulkSizer


    def _create_playlist_file_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the specific playlist update section.

        @details Provides playlist file selection and update controls.

        @param self {MainFrame} The instance of the class.
        @param parent {wx.Panel} The parent panel for the sizer.

        @retval fileSizer {wx.StaticBoxSizer} The created sizer for specific playlist updates.
        '''

        filePanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        fileGrid = wx.GridBagSizer(8, 8)

        fileBox = wx.StaticBox(parent, label="Update Playlist File")
        fileSizer = wx.StaticBoxSizer(fileBox, wx.VERTICAL)

        # create static text for describing section & audio path label
        briefDesc = wx.StaticText(filePanel, label="Update specific playlist file")
        resultDesc = wx.StaticText(filePanel, label="The updated file will be saved in project default output location")
        playlistPathLabel = wx.StaticText(filePanel, label="Playlist file path:")

        # create path input and browse button controls for selecting the audio file
        playlist_wildcard = f"Playlist files ({';'.join('*' + ext for ext in PLAYLIST_EXTS)})|{';'.join('*' + ext for ext in PLAYLIST_EXTS)}"
        self.updatePlaylistFilePath, self.updatePlaylistFileBrowse = self._make_path_controls(filePanel)
        self.updatePlaylistFilePath.Name = "updatePlaylistFilePath"
        self.updatePlaylistFileBrowse.Name = "updatePlaylistFileBrowse"
        self.updatePlaylistFileBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.updatePlaylistFilePath, playlist_wildcard))

        # create the update playlist fille button
        self.updatePlaylistFile = wx.Button(filePanel, label="Update Playlist File")
        self.updatePlaylistFile.Bind(wx.EVT_BUTTON, self.eventHandlers.on_update_playlist)

        # create a horizontal sizer for the browse and convert buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.updatePlaylistFileBrowse, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.updatePlaylistFile, 0)

        # create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.updatePlaylistFilePath, 1, wx.EXPAND | wx.RIGHT, 8)
        pathRowSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # add info text controls to the grid layout
        fileGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        fileGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # add the path row to the grid layout
        fileGrid.Add(playlistPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(pathRowSizer, pos=(2, 1), span=(1, 3), flag=wx.EXPAND)

        # make the second column growable to allow the controls to expand properly
        fileGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        filePanel.SetSizer(fileGrid)
        fileSizer.Add(filePanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return fileSizer


    def _create_info_tab(self, parent) -> wx.Panel:
        '''
        @brief This panel contains information retrieval controls.

        @details This panel is organized into nested subpanels for bulk directory processing.
        It includes options for tags walk and media info walk.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the panel.

        @retval panel {wx.Panel} The created information panel.
        '''

        panel = wx.Panel(parent, name="infoTab")
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        grid = wx.GridBagSizer(8, 8)

        # create the sizers for information retrieval tab panel
        infoMediaSizer = self._create_info_media_sizer(panel)
        infoTagsSizer = self._create_info_tag_sizer(panel)

        # horizontally order the directory and file conversion sections in the main grid
        grid.Add(infoMediaSizer, pos=(0, 0), flag=wx.ALL | wx.EXPAND, border=4)
        grid.Add(infoTagsSizer, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=4)

        # make columns growable so that the sizers expand properly when the panel is resized
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 1)

        panel.SetSizer(grid)

        return panel


    def _create_info_media_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk directory audio file media information walk sizer.

        @details Provides directory selection walk controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent panel for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The sizer containing the information controls.
        '''

        bulkPanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box, sizers, and panel for the bulk directory media information section
        bulkBox = wx.StaticBox(parent, label="Directory Media Information")
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label and file type selection
        briefDesc = wx.StaticText(bulkPanel, label="Gets media information in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="The media information file will be saved in project default output location")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")
        fileTypeLabel = wx.StaticText(bulkPanel, label="Information from Audio Ext:")

        # create controls for selecting the starting path for bulk media information
        self.mediaInfoDirTld, self.mediaInfoDirBrowse = self._make_path_controls(bulkPanel)
        self.mediaInfoDirTld.Name = "mediaInfoDirTld"
        self.mediaInfoDirBrowse.Name = "mediaInfoDirBrowse"
        self.mediaInfoDirBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.mediaInfoDirTld))

        # file type drop list for bulk media information
        file_types = ["Any file type"] + AUDIO_EXTS
        self.mediaInfoDirChoice = wx.Choice(bulkPanel, choices=file_types, name="mediaInfoDirChoice")
        self.mediaInfoDirChoice.SetSelection(0)
        self.mediaInfoDirChoice.SetToolTip("Select audio file type or 'Any file type' to process all supported audio files")

        # create the get media information button
        self.mediaInfoDir = wx.Button(bulkPanel, label="Get Media Info", name="mediaInfoDir")
        self.mediaInfoDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_get_media_info_walk)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory media information subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.mediaInfoDirTld, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.mediaInfoDirBrowse, pos=(2, 3), flag=wx.EXPAND)

        # order the file type pattern controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(fileTypeLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.mediaInfoDirChoice, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.mediaInfoDir, pos=(3, 3))

        # make the second column growable to allow the controls to expand properly
        bulkGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        bulkPanel.SetSizer(bulkGrid)
        bulkSizer.Add(bulkPanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return bulkSizer


    def _create_info_tag_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk directory audio file tag information walk sizer.

        @details Provides directory selection walk controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent panel for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The sizer containing the tag controls.
        '''

        bulkPanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box, sizers, and panel for the bulk directory tag information section
        bulkBox = wx.StaticBox(parent, label="Directory Tag Information")
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label and file type selection
        briefDesc = wx.StaticText(bulkPanel, label="Gets tag information in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="The tag information file will be saved in project default output location")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")
        fileTypeLabel = wx.StaticText(bulkPanel, label="Information from Audio Ext:")

        # create controls for selecting the starting path for bulk tag information
        self.mediaTagsDirTld, self.mediaTagsDirBrowse = self._make_path_controls(bulkPanel)
        self.mediaTagsDirTld.Name = "mediaTagsDirTld"
        self.mediaTagsDirBrowse.Name = "mediaTagsDirBrowse"
        self.mediaTagsDirBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.mediaTagsDirTld))

        # file type drop list for bulk tag information
        file_types = ["Any file type"] + AUDIO_EXTS
        self.mediaTagDirChoice = wx.Choice(bulkPanel, choices=file_types, name="mediaTagDirChoice")
        self.mediaTagDirChoice.SetSelection(0)
        self.mediaTagDirChoice.SetToolTip("Select audio file type or 'Any file type' to process all supported audio files")

        # create the get media tags button
        self.mediaTagsDir = wx.Button(bulkPanel, label="Get Media Tags", name="mediaTagsDir")
        self.mediaTagsDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_get_media_tags_walk)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory tag information subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.mediaTagsDirTld, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.mediaTagsDirBrowse, pos=(2, 3), flag=wx.EXPAND)

        # order the file type pattern controls in the bulk directory tag information subpanel grid
        bulkGrid.Add(fileTypeLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.mediaTagDirChoice, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.mediaTagsDir, pos=(3, 3))

        # make the second column growable to allow the controls to expand properly
        bulkGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        bulkPanel.SetSizer(bulkGrid)
        bulkSizer.Add(bulkPanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return bulkSizer


    def _create_remove_tab(self, parent) -> wx.Panel:
        '''
        @brief This panel contains folder & file removal controls.

        @details This panel is organized into nested subpanels for bulk directory processing and specific file processing.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the panel.

        @retval panel {wx.Panel} The created removal panel.
        '''

        panel = wx.Panel(parent, name="removeTab")
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        grid = wx.GridBagSizer(8, 8)

        # create the sizers for the removal tab
        removePatternSizer = self._create_remove_pattern_sizer(panel)
        removeListSizer = self._create_remove_list_sizer(panel)
        removeAlbumsSizer = self._create_remove_albums_sizer(panel)

        # vertically stack the remove pattern and remove list sizers
        grid.Add(removePatternSizer, pos=(0, 0), flag=wx.ALL | wx.EXPAND, border=4)
        grid.Add(removeListSizer, pos=(1, 0), flag=wx.ALL | wx.EXPAND, border=4)

        # horizontally place the remove album section to the right of the remove pattern and remove list sizers
        grid.Add(removeAlbumsSizer, pos=(0, 1), span=(2, 1), flag=wx.ALL | wx.EXPAND, border=4)

        # make columns growable so that the sizers expand properly when the panel is resized
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 1)

        panel.SetSizer(grid)

        return panel


    def _create_remove_pattern_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk remove files matching a pattern sizer.

        @details Provides directory selection, file type filtering, and  file removal controls.

        @param self {MainFrame} The instance of the class.
        @param parent {wx.Panel} The parent window for the sizer.

        @retval bulkSizer {wx.Sizer} The created sizer for directory audio conversion.
        '''

        bulkPanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box, sizers, and panel for the bulk directory audio conversion section
        bulkBox = wx.StaticBox(parent, label="Remove Matching Pattern")
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label and file type selection
        briefDesc = wx.StaticText(bulkPanel, label="Removes all files in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="Will not remove *.* pattern, or from file-system root/mount point")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")
        fileTypeLabel = wx.StaticText(bulkPanel, label="Remove this pattern:")

        # create controls for selecting the starting path for bulk file removal
        self.removePatternDirTld, self.removePatternDirBrowse = self._make_path_controls(bulkPanel)
        self.removePatternDirTld.Name = "removePatternDirTld"
        self.removePatternDirBrowse.Name = "removePatternDirBrowse"
        self.removePatternDirBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.removePatternDirTld))

        # create the pattern to remove input field
        self.removePatternDirInput = wx.TextCtrl(bulkPanel, name="removePatternDirInput")
        self.removePatternDirInput.SetToolTip("Enter the pattern to remove")

        # create the removal button
        self.removePatternDir = wx.Button(bulkPanel, label="Remove Pattern", name="removePatternDir")
        self.removePatternDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_remove_pattern)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.removePatternDirTld, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.removePatternDirBrowse, pos=(2, 3), flag=wx.EXPAND)

        # order the file type pattern controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(fileTypeLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.removePatternDirInput, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.removePatternDir, pos=(3, 3))

        # make the second column growable to allow the controls to expand properly
        bulkGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        bulkPanel.SetSizer(bulkGrid)
        bulkSizer.Add(bulkPanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return bulkSizer


    def _create_remove_list_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Creates the bulk directory remove files per set list sizer.

        @details Provides controls for selecting the directory and removing items from a set list.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent panel for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for removing items from a list.
        '''

        bulkPanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # Create the static box, sizer, and panel for the album art setting section
        bulkBox = wx.StaticBox(parent, label="Remove Matching List")
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label
        briefDesc = wx.StaticText(bulkPanel, label="Removes files from a set list in a bulk directory walk")
        detailDesc = wx.StaticText(bulkPanel, label="Only removes files that match the set list and are within the specified starting path")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld or sld:")

        # create controls for selecting the starting path for setting album art
        self.removeListDirTld, self.removeListDirBrowse = self._make_path_controls(bulkPanel)
        self.removeListDirTld.Name = "removeListDirTld"
        self.removeListDirBrowse.Name = "removeListDirBrowse"
        self.removeListDirBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.removeListDirTld))

        # create the remove from set list button
        self.removeListDir = wx.Button(bulkPanel, label="Remove List", name="removeListDir")
        self.removeListDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_remove_from_set_list)

        # create a horizontal sizer for the browse and setting buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.removeListDirBrowse, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.removeListDir, 0)

        # create a horizontal sizer for the starting path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.removeListDirTld, 1, wx.EXPAND | wx.RIGHT, 8)
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
        bulkSizer.Add(bulkPanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return bulkSizer


    def _create_remove_albums_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk remove empty albums sizer.

        @details Provides directory selection and empty folder removal controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent panel for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for removing empty albums.
        '''

        bulkPanel = wx.Panel(parent)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create static text box, sizers, and panel for the bulk remove empty albums section
        bulkBox = wx.StaticBox(parent, label="Remove Empty Albums")
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section and starting path label
        briefDesc = wx.StaticText(bulkPanel, label="Removes all empty album folders in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="All empty second level album folders will be removed")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")

        # create controls for selection the starting path for bulk removal
        self.removeAlbumsDirTld, self.removeAlbumsDirBrowse = self._make_path_controls(bulkPanel)
        self.removeAlbumsDirTld.Name = "removeAlbumsDirTld"
        self.removeAlbumsDirBrowse.Name = "removeAlbumsDirBrowse"
        self.removeAlbumsDirBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.removeAlbumsDirTld))

        # create the remove albums button
        self.removeAlbumsDir = wx.Button(bulkPanel, label="Remove Albums", name="removeAlbumsDir")
        self.removeAlbumsDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_remove_empty_albums)

        # create a horizontal sizer for the browse and remove buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.removeAlbumsDirBrowse, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.removeAlbumsDir, 0)

        # create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.removeAlbumsDirTld, 1, wx.EXPAND | wx.RIGHT, 8)
        pathRowSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory update subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(pathRowSizer, pos=(2, 1), span=(1, 3), flag=wx.EXPAND)

        # make the second column growable to allow the controls to expand properly
        bulkGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        bulkPanel.SetSizer(bulkGrid)
        bulkSizer.Add(bulkPanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return bulkSizer


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


    def log(self, message):
        '''
        @brief Log a message to the log control with a timestamp.

        @details This method uses wx.CallAfter to ensure that log updates are thread-safe and do not cause issues with the GUI responsiveness.<br>
        Each log entry is prefixed with a timestamp for better tracking of events.

        @param self {MainFrame} The instance of the class.
        @param message {str} The message to log.
        '''

        wx.CallAfter(self.mainLog.AppendText, f"[{_timestamp()}] {message}\n")


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


    def show_error(self, message: str):
        '''
        @brief Display an error reported by a background task.

        @details Shows the task error in a GUI message box.

        @param self {MainFrame} The instance of the class.
        @param message {str} The task error message.
        '''

        wx.MessageBox(message, "Error", wx.ICON_ERROR)


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
