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
from src.core.constants import MP3_EXT                      # file extension for MP3 files
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
from src.models.audio_info.audio_utilities import AudioUtilities  # noqa: E402, for GUI audio utility operations
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
    nameTab: wx.Panel                                       # Panel for folder & file name management
    artTab: wx.Panel                                        # Panel for audio art processing
    convertTab: wx.Panel                                    # Panel for audio conversion
    levelTab: wx.Panel                                      # Panel for audio level normalization
    playlistTab: wx.Panel                                   # Panel for audio playlist processing
    infoTab: wx.Panel                                       # Panel for audio & metadata information
    removalTab: wx.Panel                                    # Panel for file removal operations

    # folder & file name management
    # controls for directory adding missing album folders
    addAlbumsPath: wx.TextCtrl                              # Text control input for adding album folder source path
    addAlbumsSource: wx.Button                              # Button control for browsing add album folder source path
    addAlbums: wx.Button                                    # Button control for adding directory albums

    # controls for directory renaming existing album folders
    renameAlbumsPath: wx.TextCtrl                           # Text control input for renaming album folder source path
    renameAlbumsSource: wx.Button                           # Button control for browsing rename album folder source path
    renameAlbums: wx.Button                                 # Button control for renaming directory albums

    # controls for directory renaming files
    renameFilesPath: wx.TextCtrl                            # Text control input for renaming files source path
    renameFilesSource: wx.Button                            # Button control for browsing rename files source path
    renameFiles: wx.Button                                  # Button control for renaming directory files

    # controls for specific file renaming
    renameAudioFilePath: wx.TextCtrl                        # Text control input for specific file renaming
    renameAudioFileSource: wx.Button                        # Button control for browsing specific file to rename
    renameAudioFile: wx.Button                              # Button control for renaming specific file

    # controls for art file extraction & setting
    # controls for directory art files extraction
    extractArtPath: wx.TextCtrl                             # Text control input for directory art extraction source path
    extractArtSource: wx.Button                             # Button control for browsing extract walk source path
    extractArtChoice: wx.Choice                             # Choice control for selecting directory art extraction from audio with extension
    extractArtDir: wx.Button                                # Button control for extracting directory art

    # controls for specific file art extraction
    extractArtFilePath: wx.TextCtrl                         # Text control input for file art extraction source path
    extractArtFileBrowse: wx.Button                         # Button control for browsing file art extraction source path
    extractArtFile: wx.Button                               # Button control for extracting file art

    # controls for directory setting album art files
    setArtPath: wx.TextCtrl                                 # Text control input for setting album art path
    setArtSource: wx.Button                                 # Button control for browsing set album art path
    setArtDir: wx.Button                                    # Button control for setting directory album art

    # controls for audio file conversion
    # controls for directory audio files conversion
    convertAudioSrcPath: wx.TextCtrl                        # Text control input for convert walk source path
    convertAudioSource: wx.Button                           # Button control for browsing convert walk path
    convertAudioDestPath: wx.TextCtrl                       # Text control input for convert walk target path
    convertAudioTarget: wx.Button                           # Button control for browsing convert walk target path
    convertAudioChoice: wx.Choice                           # Choice control for selecting audio file extension to use in convert walk
    convertAudioDir: wx.Button                              # Button control for converting directory audio

    # controls for specific file audio conversion
    convertAudioFileSrcPath: wx.TextCtrl                    # Text control input for file audio conversion path
    convertAudioFileSource: wx.Button                       # Button control for browsing file audio conversion path
    convertAudioFileDestPath: wx.TextCtrl                   # Text control input for file audio conversion target path
    convertAudioFileTarget: wx.Button                       # Button control for browsing file audio conversion target path
    convertAudioFile: wx.Button                             # Button control for converting file audio

    # controls for audio file leveling
    # controls for directory clip checking
    clipCheckPath: wx.TextCtrl                              # Text control input for clip checking path
    clipCheckSource: wx.Button                              # Button control for browsing clip checking walk path
    clipCheckDir: wx.Button                                 # Button control for clip check on directory audio

    # controls for specific file clip checking
    clipCheckFilePath: wx.TextCtrl                          # Text control input for the clip check file path
    clipCheckFileSource: wx.Button                          # Button control for browsing file clip check path
    clipCheckFile: wx.Button                                # Button control for performing the file clip check

    # controls for directory audio files leveling
    levelAudioSrcPath: wx.TextCtrl                          # Text control input for level walk path input
    levelAudioSource: wx.Button                             # Button control for browsing level walk path
    levelAudioDestPath: wx.TextCtrl                         # Text control input for level walk destination path
    levelAudioTarget: wx.TextCtrl                           # Text control input for level walk target path
    levelAudioChoice: wx.Choice                             # Choice control for selecting level normalization type to use in leveling walk
    levelAudioDir: wx.Button                                # Button control for leveling directory audio

    # controls for specific file leveling
    levelAudioFileSrcPath: wx.TextCtrl                       # Text control input for the level audio file path
    levelAudioFileSource: wx.Button                          # Button control for browsing the level audio file path
    levelAudioFileDestPath: wx.TextCtrl                      # Text control input for the level audio file destination path
    levelAudioFileTarget: wx.TextCtrl                        # Text control input for the level audio file target path
    levelAudioFileChoice: wx.Choice                          # Choice control for selecting level normalization type for the single audio file
    levelAudioFile: wx.Button                                # Button control for performing the level audio file operation

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
    playlistUpdatePath: wx.TextCtrl                         # Text control input for playlist update top-level directory
    playlistUpdateSource: wx.Button                         # Button control for browsing playlist update top-level directory
    playlistUpdateDir: wx.Button                            # Button control for updating directory playlist

    # controls for specific playlist file update
    updatePlaylistFilePath: wx.TextCtrl                     # Text control input for the playlist update file path
    updatePlaylistFileBrowse: wx.Button                     # Button control for browsing the playlist update file path
    updatePlaylistFile: wx.Button                           # Button control for updating the playlist file

    # controls for removal of folders & files
    # controls for removing empty album folders
    removeAlbumsPath: wx.TextCtrl                           # Text control input for the top-level directory for removing empty albums
    removeAlbumsSource: wx.Button                           # Button control for browsing the top-level directory for removing empty albums
    removeAlbumsDir: wx.Button                              # Button control for removing empty albums

    # controls for directory remove files by input pattern
    removePatternPath: wx.TextCtrl                          # Text control input for the top-level directory for pattern-based file removal
    removePatternSource: wx.Button                          # Button control for browsing the top-level directory for pattern-based file removal
    removePatternInput: wx.TextCtrl                         # Text control input for the pattern to remove
    removePatternDir: wx.Button                             # Button control for removing files based on the specified pattern

    # controls for directory remove files by set pattern
    removeListPath: wx.TextCtrl                             # Text control input for the top-level directory for list-based file removal
    removeListSource: wx.Button                             # Button control for browsing the top-level directory for list-based file removal
    removeListDir: wx.Button                                # Button control for removing files based on the specified list

    # controls for media & metadata information
    # controls for directory media inspection
    mediaInfoPath: wx.TextCtrl                              # Text control input media inspection walk path
    mediaInfoSource: wx.Button                              # Button control for browsing media inspection walk path
    mediaInfoChoice: wx.Choice                              # Choice control for selecting media file extension to use in media inspection walk
    mediaInfoDir: wx.Button                                 # Button control for directory media inspection

    # controls for directory metadata inspection
    mediaTagsPath: wx.TextCtrl                              # Text control input for audio tag walk path
    mediaTagsSource: wx.Button                              # Button control for browsing audio tag walk path
    mediaTagChoice: wx.Choice                               # Choice control for selecting audio file extension to use in audio tag walk
    mediaTagsDir: wx.Button                                 # Button control for directory audio tag


    def __init__(
        self,
        parent=None,
        *,
        art: AudioArt,
        directory: DirectoryProcessing,
        metadata: AudioMetadata,
        normalization: AudioNormalization,
        utilities: AudioUtilities,
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
        @param utilities {AudioUtilities} The audio-utilities model instance.
        @param playlist {AudioPlaylist} The audio-playlist model instance.
        '''

        # initialize the main frame with the specified parent, title, and size
        super().__init__(parent, title="Music Processing", size=(960, 760), name="mainFrame")

        # Initialize event handlers
        self.eventHandlers = EventHandlers(self, art, directory, metadata, normalization, utilities, playlist)

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
        self.nameTab = self._create_name_tab(self.mainNotebook)
        self.artTab = self._create_art_tab(self.mainNotebook)
        self.convertTab = self._create_convert_tab(self.mainNotebook)
        self.levelTab = self._create_level_tab(self.mainNotebook)
        self.playlistTab = self._create_playlist_tab(self.mainNotebook)
        self.removeTab = self._create_remove_tab(self.mainNotebook)
        self.infoTab = self._create_info_tab(self.mainNotebook)

        # add the created panels to the notebook as separate tabs, displayed from left to right in the order they are added
        self.mainNotebook.AddPage(self.nameTab, "Name Management")
        self.mainNotebook.AddPage(self.artTab, "Art Processing")
        self.mainNotebook.AddPage(self.convertTab, "Audio Conversion")
        self.mainNotebook.AddPage(self.levelTab, "Audio Leveling")
        self.mainNotebook.AddPage(self.playlistTab, "Playlist Processing")
        self.mainNotebook.AddPage(self.removeTab, "Removal Processing")
        self.mainNotebook.AddPage(self.infoTab, "Information")

        # set Name Management tab as the default tab
        self.mainNotebook.SetSelection(0)

        # create the log control for displaying log messages
        self.mainLog = wx.TextCtrl(self.mainSplitter, style=wx.HSCROLL | wx.TE_MULTILINE | wx.TE_READONLY, value="", name="mainLog")

        # split horizontally: notebook on top, log on bottom
        self.mainSplitter.SplitHorizontally(self.mainNotebook, self.mainLog)

        # bind notebook page changed event to dynamically adjust sash position
        self.mainNotebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_notebook_page_changed)

        # set up the main sizer for the panel and add the splitter window to it
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.mainSplitter, 1, wx.EXPAND)
        self.mainPanel.SetSizer(mainSizer)

        # call Layout to ensure proper sizing before adjusting sash
        self.mainPanel.Layout()

        # adjust initial sash position based on the Name Management tab content
        wx.CallAfter(self._adjust_sash_position)

        # position the GUI window based on the environment variable for display placement
        # the environment key/value pair is only set when using the specific GUI launch configuration
        # therefore code not applicable from such as terminal command line, CI/CD pipelines, non-GUI launch configurations etc
        if os.environ.get("MUSICPROCESSING_GUI_DISPLAY") == "lower-left":
            # gather the geometry of all available displays
            displays = []
            for index in range(wx.Display.GetCount()):
                displays.append(wx.Display(index).GetGeometry())

            if not displays:
                raise RuntimeError("No displays are available for GUI placement")

            main_display_geometry = wx.Display().GetGeometry()

            # OS assigned display numbers relative to initialization sequence; therefore unreliable for determining physical layout
            # this code is predicated on two invariants:
            # 1. inverted T four monitor configuration
            # 2. main display is upper center
            lower_displays = []
            for geometry in displays:
                if geometry.y > main_display_geometry.y:
                    lower_displays.append(geometry)

            # if there are no lower displays (like running on single monitor hardware), fall back to any available display
            candidate_displays = lower_displays or displays
            lower_left_display = candidate_displays[0]

            # find the leftmost display among the candidate displays
            for geometry in candidate_displays[1:]:
                if geometry.x < lower_left_display.x:
                    lower_left_display = geometry

            self.SetPosition(lower_left_display.GetTopLeft())

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
        addAlbumsSizer = self._create_add_albums_sizer(panel)
        renameAlbumsSizer = self._create_rename_albums_sizer(panel)
        renameDirSizer = self._create_rename_dir_sizer(panel)
        renameFileSizer = self._create_rename_file_sizer(panel)

        # stack the add album and rename file walk sizers on the left
        grid.Add(addAlbumsSizer, pos=(0, 0), flag=wx.EXPAND)
        grid.Add(renameDirSizer, pos=(1, 0), flag=wx.EXPAND)

        # stack the rename albums and rename specific file sizers on the right
        grid.Add(renameAlbumsSizer, pos=(0, 1), flag=wx.EXPAND)
        grid.Add(renameFileSizer, pos=(1, 1), flag=wx.EXPAND)

        # make columns growable so that the sizers expand properly when the panel is resized
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 1)

        panel.SetSizer(grid)

        return panel


    def _create_add_albums_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk add missing album folders sizer.

        @details Provides directory selection and missing album folders addition controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent panel for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for adding missing album folders.
        '''

        # what the function is about
        function_text = "Add Album Folders"

        # info text for the section
        brief_text = "Adds missing album folders to artist folders in a directory walk"
        detail_text = "Must start from tld, checks for artist (fld) folders that only contain songs"
        result_text = "Album folders are created for each unique and valid album tag, the songs move to correct folders"
        path_text = "Starting path, tld only:"

        bulkBox = wx.StaticBox(parent, label=function_text)
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, orient=wx.VERTICAL)

        # create static text for describing section & starting path label
        briefDesc = wx.StaticText(bulkPanel, label=brief_text)
        detailDesc = wx.StaticText(bulkPanel, label=detail_text)
        resultDesc = wx.StaticText(bulkPanel, label=result_text)
        startPathLabel = wx.StaticText(bulkPanel, label=path_text)

        # create controls for selecting the starting path for bulk updating
        self.addAlbumsPath, self.addAlbumsSource = self._make_source_controls(bulkPanel, "addAlbumsPath", "addAlbumsSource")
        self.addAlbumsSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.addAlbumsPath))

        # create the update playlist button
        self.addAlbums = wx.Button(bulkPanel, label=function_text, name="addAlbums")
        self.addAlbums.Bind(wx.EVT_BUTTON, self.eventHandlers.on_add_albums)

        # create a horizontal sizer for the browse and function buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.addAlbumsSource, proportion=0, flag=wx.RIGHT, border=8)
        buttonSizer.Add(self.addAlbums, proportion=0)

        # create a horizontal sizer for all of the path input widgets
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(startPathLabel, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)
        pathRowSizer.Add(self.addAlbumsPath, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=8)
        pathRowSizer.Add(buttonSizer, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)

        # order the widgets in the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(detailDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(2, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(pathRowSizer, pos=(3, 0), span=(1, 4), flag=wx.EXPAND)

        # make the second column growable to allow the controls to expand properly
        bulkGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        bulkPanel.SetSizer(bulkGrid)
        bulkSizer.Add(bulkPanel, proportion=1, flag=wx.ALL | wx.EXPAND, border=4)

        return bulkSizer


    def _create_rename_albums_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk rename incorrect album folders sizer.

        @details Provides directory selection and incorrect album folders renaming controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent panel for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for renaming incorrect album folders.
        '''

        bulkBox = wx.StaticBox(parent, label="Rename Album Folders")
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label
        briefDesc = wx.StaticText(bulkPanel, label="Renames incorrect album folders per metadata in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="The required album name must be present, the folders are renamed in place")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld only:")

        # create controls for selecting the starting path for bulk updating
        self.renameAlbumsPath, self.renameAlbumsSource = self._make_source_controls(bulkPanel, "renameAlbumsPath", "renameAlbumsSource")
        self.renameAlbumsSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.renameAlbumsPath))

        # create the rename albums button
        self.renameAlbums = wx.Button(bulkPanel, label="Rename Albums", name="renameAlbums")
        self.renameAlbums.Bind(wx.EVT_BUTTON, self.eventHandlers.on_rename_albums)

        # create a horizontal sizer for the browse and convert buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.renameAlbumsSource, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.renameAlbums, 0)

        # create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.renameAlbumsPath, 1, wx.EXPAND | wx.RIGHT, 8)
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


    def _create_rename_dir_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk directory rename audio files sizer.

        @details Provides directory selection and renaming controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent panel for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for bulk renaming audio files.
        '''

        bulkBox = wx.StaticBox(parent, label="Directory File Renaming")
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label
        briefDesc = wx.StaticText(bulkPanel, label="Renames all audio in a directory walk per album artist and song title")
        detailDesc = wx.StaticText(bulkPanel, label="The required metadata must be present, the songs are renamed in place")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld or sld:")

        # create controls for selecting the starting path for setting album art
        self.renameFilesPath, self.renameFilesSource = self._make_source_controls(bulkPanel, "renameFilesPath", "renameFilesSource")
        self.renameFilesSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.renameFilesPath))

        # create the remove from set list button
        self.renameFiles = wx.Button(bulkPanel, label="Rename Files Walk", name="renameFiles")
        self.renameFiles.Bind(wx.EVT_BUTTON, self.eventHandlers.on_rename_files_walk)

        # create a horizontal sizer for the browse and setting buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.renameFilesSource, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.renameFiles, 0)

        # create a horizontal sizer for the starting path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.renameFilesPath, 1, wx.EXPAND | wx.RIGHT, 8)
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


    def _create_rename_file_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the specific audio file rename sizer.

        @details Provides file selection and renaming controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent panel for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for renaming specific audio files.
        '''

        fileBox = wx.StaticBox(parent, label="Rename Audio File")
        filePanel = wx.Panel(fileBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        fileGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        fileSizer = wx.StaticBoxSizer(fileBox, wx.VERTICAL)

        # create static text for describing section & audio path label
        briefDesc = wx.StaticText(filePanel, label="Renames a specific audio file per album artist and song title")
        resultDesc = wx.StaticText(filePanel, label="The required metadata must be present, the song is renamed in place")
        renamePathLabel = wx.StaticText(filePanel, label="Audio file path:")

        # create path input and browse button controls for selecting the audio file
        # @todo needs to be all audio file types
        # @todo use audio_exts constant to build wildcard string for audio files
        wildcard_exts = "Audio files (*.flac;*.mp3;*.m4a;*.wma)|*.flac;*.mp3;*.m4a;*.wma"
        self.renameAudioFilePath, self.renameAudioFileSource = self._make_source_controls(filePanel, "renameAudioFilePath", "renameAudioFileSource")
        self.renameAudioFileSource.Bind(
            wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.renameAudioFilePath, wildcard_exts)
        )

        # create the rename audio file button
        self.renameAudioFile = wx.Button(filePanel, label="Rename Audio File", name="renameAudioFile")
        self.renameAudioFile.Bind(wx.EVT_BUTTON, self.eventHandlers.on_rename_file)

        # create a horizontal sizer for the browse and convert buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.renameAudioFileSource, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.renameAudioFile, 0)

        # create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.renameAudioFilePath, 1, wx.EXPAND | wx.RIGHT, 8)
        pathRowSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # add info text controls to the grid layout
        fileGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        fileGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # add the path row to the grid layout
        fileGrid.Add(renamePathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(pathRowSizer, pos=(2, 1), span=(1, 3), flag=wx.EXPAND)

        # make the second column growable to allow the controls to expand properly
        fileGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        filePanel.SetSizer(fileGrid)
        fileSizer.Add(filePanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return fileSizer


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

        bulkBox = wx.StaticBox(parent, label="Directory Art Extraction")
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label and file type selection
        briefDesc = wx.StaticText(bulkPanel, label="Extracts album art from all audio files in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="The extracted album art will be saved alongside the audio files")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")
        fileTypeLabel = wx.StaticText(bulkPanel, label="Extract from Audio Ext:")

        # create controls for selecting the starting path for bulk extraction
        self.extractArtPath, self.extractArtSource = self._make_source_controls(bulkPanel, "extractArtPath", "extractArtSource")
        self.extractArtSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.extractArtPath))

        # file type drop list for bulk conversion
        file_types = ["Any file type"] + AUDIO_EXTS
        self.extractArtChoice = wx.Choice(bulkPanel, choices=file_types, name="extractArtChoice")
        self.extractArtChoice.SetSelection(0)
        self.extractArtChoice.SetToolTip("Select audio file type or 'Any file type' to process all supported audio files")

        # create the extraction button
        self.extractArtDir = wx.Button(bulkPanel, label="Extract All Art", name="extractArtDir")
        self.extractArtDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_extract_art_walk)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # add controls for the starting path to the grid layout
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.extractArtPath, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.extractArtSource, pos=(2, 3), flag=wx.EXPAND)

        # add controls for selecting the file type pattern and extraction button to the grid layout
        bulkGrid.Add(fileTypeLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.extractArtChoice, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
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

        fileBox = wx.StaticBox(parent, label="File Art Extraction")
        filePanel = wx.Panel(fileBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        fileGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        fileSizer = wx.StaticBoxSizer(fileBox, wx.VERTICAL)

        # create static text for describing section & audio file path label
        briefDesc = wx.StaticText(filePanel, label="Extracts album art from specific audio file")
        resultDesc = wx.StaticText(filePanel, label="The extracted album art will be saved alongside the audio file")
        audioFilePathLabel = wx.StaticText(filePanel, label="Audio file path:")

        # create path input and browse button controls for selecting the audio file
        # @todo use audio_exts constant to build
        wildcard_exts = "Audio files (*.flac;*.mp3;*.m4a;*.wma)|*.flac;*.mp3;*.m4a;*.wma"
        self.extractArtFilePath, self.extractArtFileBrowse = self._make_source_controls(filePanel, "extractArtFilePath", "extractArtFileBrowse")
        self.extractArtFileBrowse.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.extractArtFilePath, wildcard_exts))

        # create the extract file art button
        self.extractArtFile = wx.Button(filePanel, label="Extract File Art", name="extractArtFile")
        self.extractArtFile.Bind(wx.EVT_BUTTON, self.eventHandlers.on_extract_art_file)

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

        bulkBox = wx.StaticBox(parent, label="Set Album Art")
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label
        briefDesc = wx.StaticText(bulkPanel, label="Sets album art file for an album directory from project source folder")
        detailDesc = wx.StaticText(bulkPanel, label="Copies a matching AlbumArt JPEG into the album directory when it is available")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")

        # create controls for selecting the starting path for setting album art
        self.setArtPath, self.setArtSource = self._make_source_controls(bulkPanel, "setArtPath", "setArtSource")
        self.setArtSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.setArtPath))

        # create the set album art button
        self.setArtDir = wx.Button(bulkPanel, label="Set Album Art", name="setArtDir")
        self.setArtDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_set_album_art)

        # create a horizontal sizer for the browse and setting buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.setArtSource, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.setArtDir, 0)

        # create a horizontal sizer for the starting path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.setArtPath, 1, wx.EXPAND | wx.RIGHT, 8)
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

        bulkBox = wx.StaticBox(parent, label="Directory Audio Conversion")
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label and file type selection
        briefDesc = wx.StaticText(bulkPanel, label="Converts all audio files in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="Processed files saved in default output folder or specified target folder")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld or sld:")
        destPathLabel = wx.StaticText(bulkPanel, label="Destination path:")
        fileTypeLabel = wx.StaticText(bulkPanel, label="Convert from Audio Ext:")

        # create controls for selecting the starting path for bulk conversion
        self.convertAudioSrcPath, self.convertAudioSource = self._make_source_controls(bulkPanel, "convertAudioSrcPath", "convertAudioSource")
        self.convertAudioSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.convertAudioSrcPath))

        # create controls for selecting the optional target path for bulk conversion
        self.convertAudioDestPath, self.convertAudioTarget = self._make_target_controls(bulkPanel, "convertAudioDestPath", "convertAudioTarget")
        self.convertAudioTarget.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.convertAudioDestPath))

        # file type drop list for bulk conversion
        file_types = ["Any file type"] + AUDIO_EXTS
        self.convertAudioChoice = wx.Choice(bulkPanel, choices=file_types, name="convertAudioChoice")
        self.convertAudioChoice.SetSelection(0)
        self.convertAudioChoice.SetToolTip("Select audio file type or 'Any file type' to process all supported audio files")

        # create the conversion button
        self.convertAudioDir = wx.Button(bulkPanel, label="Convert All Audio", name="convertAudioDir")
        self.convertAudioDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_convert_walk)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.convertAudioSrcPath, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.convertAudioSource, pos=(2, 3), flag=wx.EXPAND)

        # order the optional target path controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(destPathLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.convertAudioDestPath, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.convertAudioTarget, pos=(3, 3), flag=wx.EXPAND)

        # order the file type pattern controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(fileTypeLabel, pos=(4, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.convertAudioChoice, pos=(4, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.convertAudioDir, pos=(4, 3))

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

        fileBox = wx.StaticBox(parent, label="Convert Audio File")
        filePanel = wx.Panel(fileBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        fileGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        fileSizer = wx.StaticBoxSizer(fileBox, wx.VERTICAL)

        # create static text for describing section & audio path label
        briefDesc = wx.StaticText(filePanel, label="Convert specific audio file")
        resultDesc = wx.StaticText(filePanel, label="Processed file saved in default output folder or specified target folder")
        audioPathLabel = wx.StaticText(filePanel, label="Audio file path:")
        destPathLabel = wx.StaticText(filePanel, label="Destination path:")

        # create path input and browse button controls for selecting the audio file
        # @todo use audio_exts constant to build wildcard string for audio files
        wildcard_exts = "Audio files (*.flac;*.mp3;*.m4a;*.wma)|*.flac;*.mp3;*.m4a;*.wma"
        self.convertAudioFileSrcPath, self.convertAudioFileSource = self._make_source_controls(
            filePanel, "convertAudioFileSrcPath", "convertAudioSource")
        self.convertAudioFileSource.Bind(
            wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.convertAudioFileSrcPath, wildcard_exts))

        # create optional target path controls
        self.convertAudioFileDestPath, self.convertAudioFileTarget = self._make_target_controls(
            filePanel, "convertAudioFileDestPath", "convertAudioFileTarget")
        self.convertAudioFileTarget.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.convertAudioFileDestPath))

        # create the convert audio file button
        self.convertAudioFile = wx.Button(filePanel, label="Convert Audio File")
        self.convertAudioFile.Bind(wx.EVT_BUTTON, self.eventHandlers.on_convert_file)

        # add info text controls to the grid layout
        fileGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        fileGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # add the source path controls to the grid layout
        fileGrid.Add(audioPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.convertAudioFileSrcPath, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        fileGrid.Add(self.convertAudioFileSource, pos=(2, 3), flag=wx.EXPAND)

        # add the destination path controls to the grid layout
        fileGrid.Add(destPathLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.convertAudioFileDestPath, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        fileGrid.Add(self.convertAudioFileTarget, pos=(3, 3), flag=wx.EXPAND)

        # add the conversion button to the grid layout on the right side so it lines up under the other 2 buttons
        fileGrid.Add(self.convertAudioFile, pos=(4, 3), flag=wx.ALIGN_RIGHT)

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
        clipCheckDirSizer = self._create_clipcheck_dir_sizer(panel)
        clipCheckFileSizer = self._create_clipcheck_file_sizer(panel)
        levelDirSizer = self._create_level_dir_sizer(panel)
        levelFileSizer = self._create_level_file_sizer(panel)

        # stack the directory sizers on the left
        grid.Add(clipCheckDirSizer, pos=(0, 0), flag=wx.ALL | wx.EXPAND, border=4)
        grid.Add(levelDirSizer, pos=(1, 0), flag=wx.ALL | wx.EXPAND, border=4)

        # stack the file sizers on the right
        grid.Add(clipCheckFileSizer, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=4)
        grid.Add(levelFileSizer, pos=(1, 1), flag=wx.ALL | wx.EXPAND, border=4)

        # make columns growable so that the sizers expand properly when the panel is resized
        grid.AddGrowableCol(0, 1)
        grid.AddGrowableCol(1, 1)

        panel.SetSizer(grid)

        return panel


    def _create_clipcheck_dir_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk directory audio clip checking section.

        @details Provides directory selection and clip checking controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for directory audio clip checking.
        '''

        bulkBox = wx.StaticBox(parent, label="Directory Clip Checking")
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label
        briefDesc = wx.StaticText(bulkPanel, label="Checks all mp3 files in a directory walk for clipping")
        resultDesc = wx.StaticText(bulkPanel, label="The results will be saved in project default output location")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")

        # create controls for selecting the starting path for bulk clip checking
        self.clipCheckPath, self.clipCheckSource = self._make_source_controls(bulkPanel, "clipCheckPath", "clipCheckSource")
        self.clipCheckSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.clipCheckPath))

        # create the clip checking button
        self.clipCheckDir = wx.Button(bulkPanel, label="Check All Audio", name="clipCheckDir")
        self.clipCheckDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_clip_check_walk)

        # create a horizontal sizer for the browse and convert buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.clipCheckSource, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.clipCheckDir, 0)

        # create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.clipCheckPath, 1, wx.EXPAND | wx.RIGHT, 8)
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


    def _create_clipcheck_file_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the specific file audio clip checking section.

        @details Provides file selection and clip checking controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the sizer.

        @retval fileSizer {wx.StaticBoxSizer} The created sizer for specific file audio clip checking.
        '''

        fileBox = wx.StaticBox(parent, label="File Clip Checking")
        filePanel = wx.Panel(fileBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        fileGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        fileSizer = wx.StaticBoxSizer(fileBox, wx.VERTICAL)

        # create static text for describing section & starting path label
        briefDesc = wx.StaticText(filePanel, label="Checks specific mp3 for clipping")
        resultDesc = wx.StaticText(filePanel, label="The results will be saved in project default output location")
        startPathLabel = wx.StaticText(filePanel, label="Mp3 file path:")

        # create controls for selecting the files for bulk clip checking
        mp3_wildcard = f"MP3 files (*{MP3_EXT})|*{MP3_EXT}"

        self.clipCheckFilePath, self.clipCheckFileSource = self._make_source_controls(filePanel, "clipCheckFilePath", "clipCheckFileSource")
        self.clipCheckFileSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.clipCheckFilePath, mp3_wildcard))

        # create the clip checking button
        self.clipCheckFile = wx.Button(filePanel, label="Check Audio File", name="clipCheckFile")
        self.clipCheckFile.Bind(wx.EVT_BUTTON, self.eventHandlers.on_clip_check_file)

        # create a horizontal sizer for the browse and convert buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.clipCheckFileSource, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.clipCheckFile, 0)

        # create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.clipCheckFilePath, 1, wx.EXPAND | wx.RIGHT, 8)
        pathRowSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # add info text controls to the grid layout
        fileGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        fileGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # add the path row to the grid layout
        fileGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(pathRowSizer, pos=(2, 1), span=(1, 3), flag=wx.EXPAND)

        # make the second column growable to allow the controls to expand properly
        fileGrid.AddGrowableCol(1)

        # set the sizer for the panel and add it to the static box sizer
        filePanel.SetSizer(fileGrid)
        fileSizer.Add(filePanel, 1, flag=wx.ALL | wx.EXPAND, border=4)

        return fileSizer


    def _create_level_dir_sizer(self, parent) -> wx.StaticBoxSizer:
        '''
        @brief Create the bulk directory audio leveling section.

        @details Provides directory selection, leveling type filtering, and leveling controls.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the sizer.

        @retval bulkSizer {wx.StaticBoxSizer} The created sizer for directory audio leveling.
        '''

        bulkBox = wx.StaticBox(parent, label="Directory Audio Leveling")
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label and leveling type selection
        briefDesc = wx.StaticText(bulkPanel, label="Levels all audio files in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="Processed files saved in default output folder or specified target folder")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")
        destPathLabel = wx.StaticText(bulkPanel, label="Destination path:")
        levelTypeLabel = wx.StaticText(bulkPanel, label="Level Audio Type:")

        # create controls for selecting the starting path for bulk leveling
        self.levelAudioSrcPath, self.levelAudioSource = self._make_source_controls(bulkPanel, "levelAudioSrcPath", "levelAudioSource")
        self.levelAudioSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.levelAudioSrcPath))

        # create controls for selecting the optional target path for bulk leveling
        self.levelAudioDestPath, self.levelAudioTarget = self._make_source_controls(bulkPanel, "levelAudioDestPath", "levelAudioTarget")
        self.levelAudioTarget.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.levelAudioDestPath))

        # level type drop list for bulk leveling
        # @todo add a level types constant LEVEL_TYPES = ["ebu", "peak", "rms"]
        # @todo add singular type constants (LEVEL_EBU = "ebu", LEVEL_PEAK = "peak", LEVEL_RMS = "rms")
        # @todo use the LEVEL_TYPES constant to populate the level_types list
        level_types = ["ebu", "peak", "rms"]
        self.levelAudioChoice = wx.Choice(bulkPanel, choices=level_types, name="levelAudioChoice")
        self.levelAudioChoice.SetSelection(0)
        self.levelAudioChoice.SetToolTip("Select normalization type: ebu (loudness), peak (peak level), or rms (RMS level)")

        # create the leveling button
        self.levelAudioDir = wx.Button(bulkPanel, label="Level All Audio", name="levelAudioDir")
        self.levelAudioDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_level_walk)

        #  add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.levelAudioSrcPath, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.levelAudioSource, pos=(2, 3), flag=wx.EXPAND)

        # order the optional target path controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(destPathLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.levelAudioDestPath, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.levelAudioTarget, pos=(3, 3), flag=wx.EXPAND)

        # order the level type controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(levelTypeLabel, pos=(4, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.levelAudioChoice, pos=(4, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.levelAudioDir, pos=(4, 3))

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

        filesBox = wx.StaticBox(parent, label="Level Audio Files")
        filePanel = wx.Panel(filesBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        fileGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        fileSizer = wx.StaticBoxSizer(filesBox, wx.VERTICAL)

        # create static text for describing section & audio path labels
        briefDesc = wx.StaticText(filePanel, label="Level specific audio file by normalization type")
        resultDesc = wx.StaticText(filePanel, label="Processed file saved in default output folder or specified target folder")
        audioPathLabel = wx.StaticText(filePanel, label="Audio file path:")
        destPathLabel = wx.StaticText(filePanel, label="Destination path:")
        levelTypeLabel = wx.StaticText(filePanel, label="Level Audio Type:")

        # create path input and browse button controls for selecting the audio files
        wildcard_mp3 = f"MP3 Audio files (*{MP3_EXT})|*{MP3_EXT}"
        self.levelAudioFileSrcPath, self.levelAudioFileSource = self._make_source_controls(
            filePanel, "levelAudioFileSrcPath", "levelAudioFileSource")
        self.levelAudioFileSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.levelAudioFileSrcPath, wildcard_mp3))

        # create optional target path controls
        self.levelAudioFileDestPath, self.levelAudioFileTarget = self._make_target_controls(
            filePanel, "levelAudioFileDestPath", "levelAudioFileTarget")
        self.levelAudioFileTarget.Bind(
            wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.levelAudioFileDestPath))

        # level type drop list for single file leveling
        # @todo add a level types constant LEVEL_TYPES = ["ebu", "peak", "rms"]
        # @todo add singular type constants (LEVEL_EBU = "ebu", LEVEL_PEAK = "peak", LEVEL_RMS = "rms")
        # @todo use the LEVEL_TYPES constant to populate the level_types list
        level_types = ["ebu", "peak", "rms"]
        self.levelAudioFileChoice = wx.Choice(filePanel, choices=level_types, name="levelAudioChoice")
        self.levelAudioFileChoice.SetSelection(0)
        self.levelAudioFileChoice.SetToolTip("Select normalization type: ebu (loudness), peak (peak level), or rms (RMS level)")

        # create the single file leveling button for the level audio file
        self.levelAudioFile = wx.Button(filePanel, label="Level Audio File")
        self.levelAudioFile.Bind(wx.EVT_BUTTON, self.eventHandlers.on_level_file)

        # add info text controls to the grid layout
        fileGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        fileGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # add the source path controls to the grid layout
        fileGrid.Add(audioPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.levelAudioFileSrcPath, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        fileGrid.Add(self.levelAudioFileSource, pos=(2, 3), flag=wx.EXPAND)

        # add the destination path controls to the grid layout
        fileGrid.Add(destPathLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.levelAudioFileDestPath, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
        fileGrid.Add(self.levelAudioFileTarget, pos=(3, 3), flag=wx.EXPAND)

        # order the level type controls in the single file leveling subpanel grid
        fileGrid.Add(levelTypeLabel, pos=(4, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        fileGrid.Add(self.levelAudioFileChoice, pos=(4, 1), span=(1, 2), flag=wx.EXPAND)
        fileGrid.Add(self.levelAudioFile, pos=(4, 3))

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

        bulkBox = wx.StaticBox(parent, label="Directory Playlist Update")
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label
        briefDesc = wx.StaticText(bulkPanel, label="Updates all playlist files in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="The updated playlists will be saved in project default output location")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld only:")

        # create controls for selecting the starting path for bulk updating
        self.playlistUpdatePath, self.playlistUpdateSource = self._make_source_controls(bulkPanel, "playlistUpdatePath", "playlistUpdateSource")
        self.playlistUpdateSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.playlistUpdatePath))

        # create the update playlist button
        self.playlistUpdateDir = wx.Button(bulkPanel, label="Update All Playlists", name="playlistUpdateDir")
        self.playlistUpdateDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_update_playlist_walk)

        # create a horizontal sizer for the browse and convert buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.playlistUpdateSource, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.playlistUpdateDir, 0)

        # create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.playlistUpdatePath, 1, wx.EXPAND | wx.RIGHT, 8)
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

        fileBox = wx.StaticBox(parent, label="Update Playlist File")
        filePanel = wx.Panel(fileBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        fileGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        fileSizer = wx.StaticBoxSizer(fileBox, wx.VERTICAL)

        # create static text for describing section & audio path label
        briefDesc = wx.StaticText(filePanel, label="Update specific playlist file")
        resultDesc = wx.StaticText(filePanel, label="The updated file will be saved in project default output location")
        playlistPathLabel = wx.StaticText(filePanel, label="Playlist file path:")

        # create path input and browse button controls for selecting the audio file
        playlist_patterns = ';'.join('*' + ext for ext in PLAYLIST_EXTS)
        playlist_wildcard = f"Playlist files ({playlist_patterns})|{playlist_patterns}"

        self.updatePlaylistFilePath, self.updatePlaylistFileBrowse = self._make_source_controls(
            filePanel, "updatePlaylistFilePath", "updatePlaylistFileBrowse")
        self.updatePlaylistFileBrowse.Bind(
            wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_file(evt, self.updatePlaylistFilePath, playlist_wildcard)
        )

        # create the update playlist fille button
        self.updatePlaylistFile = wx.Button(filePanel, label="Update Playlist File")
        self.updatePlaylistFile.Bind(wx.EVT_BUTTON, self.eventHandlers.on_update_playlist_file)

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

        bulkBox = wx.StaticBox(parent, label="Directory Media Information")
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label and file type selection
        briefDesc = wx.StaticText(bulkPanel, label="Gets media information in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="The media information file will be saved in project default output location")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")
        fileTypeLabel = wx.StaticText(bulkPanel, label="Information from Audio Ext:")

        # create controls for selecting the starting path for bulk media information
        self.mediaInfoPath, self.mediaInfoSource = self._make_source_controls(bulkPanel, "mediaInfoPath", "mediaInfoSource")
        self.mediaInfoSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.mediaInfoPath))

        # file type drop list for bulk media information
        file_types = ["Any file type"] + AUDIO_EXTS
        self.mediaInfoChoice = wx.Choice(bulkPanel, choices=file_types, name="mediaInfoChoice")
        self.mediaInfoChoice.SetSelection(0)
        self.mediaInfoChoice.SetToolTip("Select audio file type or 'Any file type' to process all supported audio files")

        # create the get media information button
        self.mediaInfoDir = wx.Button(bulkPanel, label="Get Media Info", name="mediaInfoDir")
        self.mediaInfoDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_get_media_info_walk)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory media information subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.mediaInfoPath, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.mediaInfoSource, pos=(2, 3), flag=wx.EXPAND)

        # order the file type pattern controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(fileTypeLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.mediaInfoChoice, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
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

        bulkBox = wx.StaticBox(parent, label="Directory Tag Information")
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label and file type selection
        briefDesc = wx.StaticText(bulkPanel, label="Gets tag information in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="The tag information file will be saved in project default output location")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")
        fileTypeLabel = wx.StaticText(bulkPanel, label="Information from Audio Ext:")

        # create controls for selecting the starting path for bulk tag information
        self.mediaTagsPath, self.mediaTagsSource = self._make_source_controls(bulkPanel, "mediaTagsPath", "mediaTagsSource")
        self.mediaTagsSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.mediaTagsPath))

        # file type drop list for bulk tag information
        file_types = ["Any file type"] + AUDIO_EXTS
        self.mediaTagChoice = wx.Choice(bulkPanel, choices=file_types, name="mediaTagChoice")
        self.mediaTagChoice.SetSelection(0)
        self.mediaTagChoice.SetToolTip("Select audio file type or 'Any file type' to process all supported audio files")

        # create the get media tags button
        self.mediaTagsDir = wx.Button(bulkPanel, label="Get Media Tags", name="mediaTagsDir")
        self.mediaTagsDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_get_media_tags_walk)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory tag information subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.mediaTagsPath, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.mediaTagsSource, pos=(2, 3), flag=wx.EXPAND)

        # order the file type pattern controls in the bulk directory tag information subpanel grid
        bulkGrid.Add(fileTypeLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.mediaTagChoice, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
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

        bulkBox = wx.StaticBox(parent, label="Remove Matching Pattern")
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label and file type selection
        briefDesc = wx.StaticText(bulkPanel, label="Removes all files in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="Will not remove *.* pattern, or from file-system root/mount point")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")
        fileTypeLabel = wx.StaticText(bulkPanel, label="Remove this pattern:")

        # create controls for selecting the starting path for bulk file removal
        self.removePatternPath, self.removePatternSource = self._make_source_controls(bulkPanel, "removePatternPath", "removePatternSource")
        self.removePatternSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.removePatternPath))

        # create the pattern to remove input field
        self.removePatternInput = wx.TextCtrl(bulkPanel, name="removePatternInput")
        self.removePatternInput.SetToolTip("Enter the pattern to remove")

        # create the removal button
        self.removePatternDir = wx.Button(bulkPanel, label="Remove Pattern", name="removePatternDir")
        self.removePatternDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_remove_pattern)

        # add info text controls to the grid layout
        bulkGrid.Add(briefDesc, pos=(0, 0), span=(1, 3), flag=wx.EXPAND)
        bulkGrid.Add(resultDesc, pos=(1, 0), span=(1, 3), flag=wx.EXPAND)

        # order the top level directory controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(startPathLabel, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.removePatternPath, pos=(2, 1), span=(1, 2), flag=wx.EXPAND)
        bulkGrid.Add(self.removePatternSource, pos=(2, 3), flag=wx.EXPAND)

        # order the file type pattern controls in the bulk directory conversion subpanel grid
        bulkGrid.Add(fileTypeLabel, pos=(3, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        bulkGrid.Add(self.removePatternInput, pos=(3, 1), span=(1, 2), flag=wx.EXPAND)
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

        bulkBox = wx.StaticBox(parent, label="Remove Matching List")
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section & starting path label
        briefDesc = wx.StaticText(bulkPanel, label="Removes files from a set list in a bulk directory walk")
        detailDesc = wx.StaticText(bulkPanel, label="Only removes files that match the set list and are within the specified starting path")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld or sld:")

        # create controls for selecting the starting path for setting album art
        self.removeListPath, self.removeListSource = self._make_source_controls(bulkPanel, "removeListPath", "removeListSource")
        self.removeListSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.removeListPath))

        # create the remove from set list button
        self.removeListDir = wx.Button(bulkPanel, label="Remove List", name="removeListDir")
        self.removeListDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_remove_list)

        # create a horizontal sizer for the browse and setting buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.removeListSource, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.removeListDir, 0)

        # create a horizontal sizer for the starting path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.removeListPath, 1, wx.EXPAND | wx.RIGHT, 8)
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

        bulkBox = wx.StaticBox(parent, label="Remove Empty Albums")
        bulkPanel = wx.Panel(bulkBox)
        # set gaps between elements in the grid bag sizer; elements added to grid may have border spacing of their own which is additive to this
        bulkGrid = wx.GridBagSizer(8, 8)

        # create the static box sizer
        bulkSizer = wx.StaticBoxSizer(bulkBox, wx.VERTICAL)

        # create static text for describing section and starting path label
        briefDesc = wx.StaticText(bulkPanel, label="Removes all empty album folders in a directory walk")
        resultDesc = wx.StaticText(bulkPanel, label="The album folder must be completely empty to be eligible for removal")
        startPathLabel = wx.StaticText(bulkPanel, label="Starting path, tld or fld:")

        # create controls for selection the starting path for bulk removal
        self.removeAlbumsPath, self.removeAlbumsSource = self._make_source_controls(bulkPanel, "removeAlbumsPath", "removeAlbumsSource")
        self.removeAlbumsSource.Bind(wx.EVT_BUTTON, lambda evt: self.eventHandlers.on_browse_dir(evt, self.removeAlbumsPath))

        # create the remove albums button
        self.removeAlbumsDir = wx.Button(bulkPanel, label="Remove Albums", name="removeAlbumsDir")
        self.removeAlbumsDir.Bind(wx.EVT_BUTTON, self.eventHandlers.on_remove_empty_albums)

        # create a horizontal sizer for the browse and remove buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.removeAlbumsSource, 0, wx.RIGHT, 8)
        buttonSizer.Add(self.removeAlbumsDir, 0)

        # create a horizontal sizer for the file path row
        pathRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathRowSizer.Add(self.removeAlbumsPath, 1, wx.EXPAND | wx.RIGHT, 8)
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


    def _make_source_controls(self, parent, txt_name, button_name) -> (tuple[wx.TextCtrl, wx.Button]):
        '''
        @brief Helper function to create a standard set of source path controls (text box and browse button).

        @details This function is used to create consistent path input controls across different panels in the application.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the controls.

        @retval path_controls {[wx.TextCtrl, wx.Button]} Tuple containing the text control and the browse button.
        '''

        #  create the text control for path input
        pathLabel = wx.TextCtrl(parent, name=txt_name)
        pathLabel.SetToolTip("Enter a source path or click Source button")

        # create the browse button for selecting the path
        browseButton = wx.Button(parent, label="Source", name=button_name)
        browseButton.SetToolTip("Browse for source path")

        path_controls = (pathLabel, browseButton)

        return path_controls


    def _make_target_controls(self, parent, txt_name, button_name) -> (tuple[wx.TextCtrl, wx.Button]):
        '''
        @brief Helper function to create a standard set of target path controls (text box and browse button).

        @details This function is used to create consistent path input controls across different panels in the application.

        @param self {MainFrame} The instance of the class.
        @param parent {Any} The parent window for the controls.

        @retval path_controls {[wx.TextCtrl, wx.Button]} Tuple containing the text control and the browse button.
        '''

        #  create the text control for path input
        pathLabel = wx.TextCtrl(parent, name=txt_name)
        pathLabel.SetToolTip("Enter a target path or click Target button")

        # create the browse button for selecting the path
        browseButton = wx.Button(parent, label="Target", name=button_name)
        browseButton.SetToolTip("Browse for target path")

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


    def _adjust_sash_position(self):
        '''
        @brief Adjust the sash position based on the current tab's content height.

        @details Calculates the vertical extent of all visible controls in the active tab.<br>
        Positions the sash approximately 20 pixels below the lowest visible element.

        @param self {MainFrame} The instance of the class.
        '''

        active_tab = self.mainNotebook.GetCurrentPage()
        if active_tab is None:
            return

        # find the bottom-most control in the current tab
        max_bottom = 0
        for child in active_tab.GetChildren():
            if child.IsShown():
                rect = child.GetRect()
                control_bottom = rect.y + rect.height
                if control_bottom > max_bottom:
                    max_bottom = control_bottom

        # if no visible controls found, use best size as fallback
        if max_bottom == 0:
            best_size = active_tab.GetBestSize()
            tab_height = best_size.height if best_size.height > 0 else 200
        else:
            # add buffer pixels below the lowest visible element
            tab_height = max_bottom + 20

        # calculate sash position with constraints
        splitter_height = self.mainSplitter.GetSize().height
        min_log_height = 100
        max_tab_height = splitter_height - min_log_height

        # account for the notebook tab bar height
        notebook_tab_height = 30

        # set sash position
        sash_position = min(tab_height + notebook_tab_height, max_tab_height)
        self.mainSplitter.SetSashPosition(sash_position)


    def _on_notebook_page_changed(self, event):
        '''
        @brief Event handler for notebook page changes to adjust sash position dynamically.

        @details When a notebook tab is changed, this method recalculates and adjusts the sash position
        based on the content of the newly visible tab.

        @param self {MainFrame} The instance of the class.
        @param event {wx.NotebookEvent} The event object from the notebook page change.
        '''

        wx.CallAfter(self._adjust_sash_position)


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
        utilities=AudioUtilities(),
        playlist=AudioPlaylist()
    )
    frame.Show()
    app.MainLoop()
## @}
