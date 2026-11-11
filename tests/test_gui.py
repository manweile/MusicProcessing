'''
@class TestGuiSmoke
@file test_gui.py
@author Gerald Manweiler

@brief Simple GUI smoke tests for wxPython support.

@details Provides basic smoke tests for the GUI module, ensuring that key components can be instantiated and functions are callable.

@version 1.0.0
@date 2026-11-08

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import importlib                                            # for dynamic module import
import unittest                                             # for direct test-suite execution
from unittest import TestCase                               # for test-case assertions

# Third Party Modules
try:                                                        # try/except block to handle optional wxPython dependency
    import wx                                               # for wxPython GUI support
except ImportError:                                         # pragma: no cover
    wx = None                                               # wxPython not available

# Local Module Methods
from tests.support import get_method_names                  # for direct test-suite construction


class TestGuiSmoke(TestCase):
    '''
    @brief Basic checks for GUI module.

    @details These tests are not meant to be exhaustive, but rather to catch basic issues with the GUI module and its dependencies.
    '''

    def test_mainframe_can_instantiate(self):
        '''
        @brief Test that the MainFrame can be instantiated without errors.

        @details This test will fail if there are any issues with the MainFrame class or its dependencies that prevent it from being created.

        @param self {TestGuiSmoke} Test instance.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        @exception SystemExit If the GUI environment is unavailable, the test will be skipped with a message indicating the reason.
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

        @param self {TestGuiSmoke} Test instance.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        @exception SystemExit A common baseclass exception to handle unforeseen errors.
        '''

        if wx is None:
            self.skipTest("wxPython is not installed")

        try:
            gui_module = importlib.import_module("src.gui.wx_app")
        except (Exception, SystemExit) as exc:  # pragma: no cover - environment dependent
            self.skipTest(f"GUI environment unavailable: {exc}")

        self.assertTrue(callable(gui_module.run_gui))


if __name__ == "__main__":
    '''
    @brief Run the TestGuiSmoke test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.

    @note This test module can be run directly with `python tests/test_gui.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestGuiSmoke)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestGuiSmoke(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
