import wx


class MainFrame (wx.Frame):

    def __init__(self, parent=None) -> None:

        border_one = 1
        border_five = 5
        expand_all = wx.EXPAND | wx.ALL
        proportion_one = 1

        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(font.GetPointSize() + 2)

        splitter_sash = 550
        splitter_style = wx.SP_LIVE_UPDATE

        text_ctrl_style = wx.HSCROLL | wx.TE_MULTILINE | wx.TE_READONLY

        main_frame_title = "Music Processing GUI"
        main_frame_size = wx.Size(960, 760)
        main_frame_style = wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL

        super().__init__(parent, title=main_frame_title, size=main_frame_size, style=main_frame_style)

        self.SetFont(font)

        SizerMainFrame = wx.BoxSizer(wx.VERTICAL)
        SizerMainPanel = wx.BoxSizer(wx.VERTICAL)
        SizerTabsPanel = wx.BoxSizer(wx.VERTICAL)
        SizerLogPanel = wx.BoxSizer(wx.VERTICAL)

        # Create the main panel for the frame
        self.MainPanel = wx.Panel(self)
        self.MainPanel.SetFont(font)

        self.MainSplitter = wx.SplitterWindow(self.MainPanel, style=splitter_style)

        self.TabsPanel = wx.Panel(self.MainSplitter)
        self.TabsPanel.SetFont(font)

        self.NotebookTabs = wx.Notebook(self.TabsPanel)

        self.PanelArtTab = wx.Panel(self.NotebookTabs)
        self.PanelArtTab.SetFont(font)

        self.PanelConvertTab = wx.Panel(self.NotebookTabs)
        self.PanelLevelTab = wx.Panel(self.NotebookTabs)
        self.PanelPlaylistTab = wx.Panel(self.NotebookTabs)
        self.PanelMetadataTab = wx.Panel(self.NotebookTabs)
        self.PanelDirTab = wx.Panel(self.NotebookTabs)

        self.NotebookTabs.AddPage(self.PanelArtTab, "Art")
        self.NotebookTabs.AddPage(self.PanelConvertTab, "Convert")
        self.NotebookTabs.AddPage(self.PanelLevelTab, "Level")
        self.NotebookTabs.AddPage(self.PanelPlaylistTab, "Playlist")
        self.NotebookTabs.AddPage(self.PanelMetadataTab, "Metadata")
        self.NotebookTabs.AddPage(self.PanelDirTab, "Directory")

        SizerTabsPanel.Add(self.NotebookTabs, proportion_one, expand_all, border_one)

        self.TabsPanel.SetSizer(SizerTabsPanel)
        self.TabsPanel.Layout()
        SizerTabsPanel.Fit(self.TabsPanel)

        self.LogPanel = wx.Panel(self.MainSplitter)

        self.LogTextCtrl = wx.TextCtrl(self.LogPanel, style=text_ctrl_style)
        SizerLogPanel.Add(self.LogTextCtrl, proportion_one, expand_all, border_one)

        self.LogPanel.SetSizer(SizerLogPanel)
        self.LogPanel.Layout()
        SizerLogPanel.Fit(self.LogPanel)

        self.MainSplitter.SplitHorizontally(self.TabsPanel, self.LogPanel, splitter_sash)
        SizerMainPanel.Add(self.MainSplitter, proportion_one, wx.EXPAND, border_five)

        self.MainPanel.SetSizer(SizerMainPanel)
        self.MainPanel.Layout()

        SizerMainPanel.Fit(self.MainPanel)
        SizerMainFrame.Add(self.MainPanel, proportion_one, expand_all, border_five)

        self.SetSizer(SizerMainFrame)
        self.Layout()

        self.Centre(wx.BOTH)
        self.Maximize()


# ----------------------------------------------------------------------
# Application Execution Block
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Create the core wx application runtime
    app = wx.App(False)

    # Instantiate your main window frame
    frame = MainFrame(None)

    # Make sure the frame window is rendered onto your desktop canvas
    frame.Show(True)

    # Start the continuous UI event listener loop
    app.MainLoop()
