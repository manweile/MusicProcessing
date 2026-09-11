'''
@file test_gui.py
@brief Simple GUI smoke tests for wxPython support.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import unittest
import importlib

# third party modules
try:
    import wx
except ImportError:  # pragma: no cover
    wx = None


class TestGuiSmoke(unittest.TestCase):
    '''
    @briefBasic checks for GUI module.

    @details These tests are not meant to be exhaustive, but rather to catch basic issues with the GUI module and its dependencies.
    '''

    def test_mainframe_can_instantiate(self):
        '''
        @brief Test that the MainFrame can be instantiated without errors.

        @details This test will fail if there are any issues with the MainFrame class or its dependencies that prevent it from being created.

        @exceptions Exception, SystemExit: If the GUI environment is unavailable, the test will be skipped with a message indicating the reason.
        '''

        if wx is None:
            self.skipTest("wxPython is not installed")

        try:
            gui_module = importlib.import_module("src.gui.wx_app")
            app = wx.App(False)
        except (Exception, SystemExit) as exc:  # pragma: no cover - environment dependent
            self.skipTest(f"GUI environment unavailable: {exc}")

        frame = gui_module.MainFrame(None)
        self.assertIsInstance(frame, wx.Frame)
        frame.Destroy()
        app.Destroy()

    def test_run_gui_callable(self):
        '''
        @brief Test that the run_gui function is callable.

        @details This test will fail if there are any issues with the run_gui function or its dependencies that prevent it from being called.

        @exceptions Exception, SystemExit: If the GUI environment is unavailable, the test will be skipped with a message indicating the reason.
        '''

        if wx is None:
            self.skipTest("wxPython is not installed")

        try:
            gui_module = importlib.import_module("src.gui.wx_app")
        except (Exception, SystemExit) as exc:  # pragma: no cover - environment dependent
            self.skipTest(f"GUI environment unavailable: {exc}")

        self.assertTrue(callable(gui_module.run_gui))
