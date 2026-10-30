# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

import gettext
_ = gettext.gettext

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Music Processing GUI"), pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizerMain = wx.BoxSizer( wx.VERTICAL )

        self.m_panelMain = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizerMainPanel = wx.BoxSizer( wx.VERTICAL )

        self.m_splitterMain = wx.SplitterWindow( self.m_panelMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
        self.m_splitterMain.Bind( wx.EVT_IDLE, self.m_splitterMainOnIdle )

        self.m_panelTabs = wx.Panel( self.m_splitterMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizerTabs = wx.BoxSizer( wx.VERTICAL )

        self.m_notebookTabs = wx.Notebook( self.m_panelTabs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_panelArtTab = wx.Panel( self.m_notebookTabs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_notebookTabs.AddPage( self.m_panelArtTab, _(u"Art"), False )
        self.m_panelConvertTab = wx.Panel( self.m_notebookTabs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_notebookTabs.AddPage( self.m_panelConvertTab, _(u"Convert"), False )
        self.m_panelLevelTab = wx.Panel( self.m_notebookTabs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_notebookTabs.AddPage( self.m_panelLevelTab, _(u"Level"), False )
        self.m_panelPlaylistTab = wx.Panel( self.m_notebookTabs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_notebookTabs.AddPage( self.m_panelPlaylistTab, _(u"Playlist"), False )
        self.m_panelMetadataTab = wx.Panel( self.m_notebookTabs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_notebookTabs.AddPage( self.m_panelMetadataTab, _(u"Metadata"), False )
        self.m_panelDirTab = wx.Panel( self.m_notebookTabs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_notebookTabs.AddPage( self.m_panelDirTab, _(u"Directory"), False )

        bSizerTabs.Add( self.m_notebookTabs, 1, wx.EXPAND |wx.ALL, 5 )


        self.m_panelTabs.SetSizer( bSizerTabs )
        self.m_panelTabs.Layout()
        bSizerTabs.Fit( self.m_panelTabs )
        self.m_panelLog = wx.Panel( self.m_splitterMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizerLog = wx.BoxSizer( wx.VERTICAL )

        self.m_textCtrlLog = wx.TextCtrl( self.m_panelLog, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.TE_MULTILINE|wx.TE_READONLY )
        bSizerLog.Add( self.m_textCtrlLog, 1, wx.ALL|wx.EXPAND, 5 )


        self.m_panelLog.SetSizer( bSizerLog )
        self.m_panelLog.Layout()
        bSizerLog.Fit( self.m_panelLog )
        self.m_splitterMain.SplitHorizontally( self.m_panelTabs, self.m_panelLog, 550 )
        bSizerMainPanel.Add( self.m_splitterMain, 1, wx.EXPAND, 5 )


        self.m_panelMain.SetSizer( bSizerMainPanel )
        self.m_panelMain.Layout()
        bSizerMainPanel.Fit( self.m_panelMain )
        bSizerMain.Add( self.m_panelMain, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizerMain )
        self.Layout()

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass

    def m_splitterMainOnIdle( self, event ):
        self.m_splitterMain.SetSashPosition( 550 )
        self.m_splitterMain.Unbind( wx.EVT_IDLE )


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
