"""
@file test_gui.py
@brief Simple GUI smoke tests for wxPython support.
"""

import unittest

try:
    import wx
except ImportError:  # pragma: no cover
    wx = None

from src.gui.wx_app import MainFrame, run_gui


class TestGuiSmoke(unittest.TestCase):
    '''Basic checks for GUI module.'''

    @unittest.skipIf(wx is None, "wxPython is not installed")
    def test_mainframe_can_instantiate(self):
        app = wx.App(False)
        frame = MainFrame(None)
        self.assertIsInstance(frame, wx.Frame)
        frame.Destroy()
        app.Destroy()

    @unittest.skipIf(wx is None, "wxPython is not installed")
    def test_run_gui_callable(self):
        self.assertTrue(callable(run_gui))
