'''
@class TestMain
@file test_main.py
@author Gerald Manweiler

@brief Defines the test main logging class.

@details Verifies that running the application creates its main log file.

@version 1.0.0
@date 2026-11-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import os                                                   # for constructing file-system paths
import subprocess                                           # for launching the application process
import sys                                                  # for the current Python executable
import unittest                                             # for direct test-suite execution
from pathlib import Path                                    # for object-oriented file-system paths
from unittest import TestCase                               # for test-case assertions

# Local Module Methods
from tests.support import get_method_names                  # for direct test-suite construction

# Local Module Constants
from src.core.constants import LOG_DIR                      # directory containing log files
from src.core.paths import GENERATED_PATH                   # directory containing generated files


class TestMain(TestCase):
    '''
    @brief Tests application logging initialization.

    @details Verifies main.py behaviors.
    '''

    @classmethod
    def setUpClass(cls):
        '''
        @brief Load the expected CLI help output.

        @details Loads the expected help output from the test fixture file.

        @note The baseline file must exist, co-located with test suite, and contain the expected help output.

        @param cls: (type[TestMain]) Test class receiving the fixture.
        '''

        baseline_path = Path(__file__).with_name("cli help baseline.txt")
        baseline_lines = baseline_path.read_text(encoding="utf-8").splitlines()
        cls.expected_help = "\n".join(baseline_lines[1:])


    def test_main_without_arguments_creates_main_log(self):
        '''
        @brief Test that launching main.py creates main.log.

        @details Deletes any existing main.log, runs main.py without arguments, and checks the log after it exits.

        @param self: (type[TestMain]) Test instance.

        @exception subprocess.TimeoutExpired If main.py does not close within the timeout.
        '''

        try:
            project_root = Path(__file__).resolve().parents[1]
            main_path = project_root.joinpath("main.py")
            log_path = Path(os.path.join(GENERATED_PATH, LOG_DIR, "main.log"))

            # Remove existing main.log if it exists before running main.py
            if log_path.exists():
                log_path.unlink()

            result = subprocess.run([sys.executable, str(main_path)], cwd=project_root, capture_output=True, text=True, timeout=180)

            expected_result = f"main.py exited with {result.returncode}.\n{result.stdout}\n{result.stderr}"
            self.assertEqual(result.returncode, 0, expected_result)
            self.assertTrue(log_path.is_file())

        except subprocess.TimeoutExpired as ste:
            self.fail(f"main.py did not exit within the timeout: {ste}")


    def test_main_help_matches_baseline(self):
        '''
        @brief Test that main.py --help matches the recorded baseline.

        @details Runs main.py with --help and compares its output with the saved help baseline.

        @param self: (type[TestMain]) Test instance.

        @exception subprocess.TimeoutExpired If main.py does not close within the timeout.
        '''

        try:
            project_root = Path(__file__).resolve().parents[1]
            main_path = project_root.joinpath("main.py")

            result = subprocess.run([sys.executable, str(main_path), "--help"], cwd=project_root, capture_output=True, text=True, timeout=180)

            expected_result = f"main.py --help exited with {result.returncode}.\n{result.stdout}\n{result.stderr}"
            self.assertEqual(result.returncode, 0, expected_result)
            self.assertEqual(self.expected_help.splitlines(), result.stdout.splitlines())

        except subprocess.TimeoutExpired as ste:
            self.fail(f"main.py did not exit within the timeout: {ste}")


if __name__ == "__main__":
    '''
    @brief Run the TestMain test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.

    @note This test module can be run directly with `python tests/test_main_logging.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestMain)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestMain(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
