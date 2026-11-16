'''
@class TestCorePaths
@file test_paths.py
@author Gerald Manweiler

@brief Defines tests for core path configuration.

@details Verifies generated-file path defaults and environment overrides.

@version 1.0.0
@date 2026-11-16

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import importlib                                            # for reloading path configuration
import os                                                   # for environment access
import unittest                                             # for direct test-suite execution
from unittest import TestCase                               # for test-case assertions
from unittest.mock import patch                             # for environment patching

# Local Module Methods
from tests.support import get_method_names                  # for direct test-suite construction

# Local Modules
from src.core import paths                                  # for core path configuration


class TestCorePaths(TestCase):
    '''
    @brief Test case for core path configuration.

    @details Verifies the generated-files directory configuration.
    '''

    def test_generated_path_environment_override_and_default(self):
        '''
        @brief Test the generated-files environment override and default.

        @details Uses the configured path when set and falls back to the source directory when empty.<br>
        This test is for when running Github Local Actions or similar CI environments.

        @test Happy path.

        @param self {TestCorePaths} The instance of the test class.
        '''

        # add cleanup to reload the paths module after each test
        self.addCleanup(importlib.reload, paths)

        # define the override path for the generated files
        override_path = os.path.join("tmp", "generated_files")

        # patch dict to set the environment variable for the override path
        with patch.dict(os.environ, {"MUSICPROCESSING_GENERATED_PATH": override_path}):
            # assert that the GENERATED_PATH matches the override path
            importlib.reload(paths)
            self.assertEqual(paths.GENERATED_PATH, override_path)

        # patch dict to unset the environment variable for the default path
        with patch.dict(os.environ, {"MUSICPROCESSING_GENERATED_PATH": ""}):
            # assert that the GENERATED_PATH falls back to the default path within the source directory
            importlib.reload(paths)
            self.assertEqual(paths.GENERATED_PATH, os.path.join(paths.SRC_PATH, "generated_files"))


if __name__ == "__main__":
    '''
    @brief Run the TestCorePaths test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.

    @note This test module can be run directly with `python tests/test_paths.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestCorePaths)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestCorePaths(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
