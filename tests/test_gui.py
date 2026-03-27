'''
@file test_gui.py
@brief Simple GUI smoke tests for wxPython support.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import unittest

# third party modules
try:
    import wx
except ImportError:  # pragma: no cover
    wx = None

# local module classes
from src.gui.wx_app import MainFrame, run_gui


class TestGuiSmoke(unittest.TestCase):
    '''
    @briefBasic checks for GUI module.

    @details These tests are not meant to be exhaustive, but rather to catch basic issues with the GUI module and its dependencies.
    '''

    @unittest.skipIf(wx is None, "wxPython is not installed")
    def test_mainframe_can_instantiate(self):
        '''
        @brief Test that the MainFrame can be instantiated without errors.

        @details This test will fail if there are any issues with the MainFrame class or its dependencies that prevent it from being created.
        '''

        app = wx.App(False)
        frame = MainFrame(None)
        self.assertIsInstance(frame, wx.Frame)
        frame.Destroy()
        app.Destroy()

    @unittest.skipIf(wx is None, "wxPython is not installed")
    def test_run_gui_callable(self):
        '''
        @brief Test that the run_gui function is callable.

        @details This test will fail if there are any issues with the run_gui function or its dependencies that prevent it from being called.
        '''

        self.assertTrue(callable(run_gui))
