'''
@class TestPathValidation
@file test_validation.py
@author Gerald Manweiler

@brief Defines the test path validation class.

@details Verifies wxPython-independent file and directory path validation.

@version 1.0.0
@date 2026-11-13

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import os                                                   # for constructing file-system paths
import tempfile                                             # for temporary test paths
import unittest                                             # for direct test-suite execution
from unittest import TestCase                               # for test-case assertions

# Local Module Methods
from src.controllers.validation import validate_dir         # for checking directory paths
from src.controllers.validation import validate_file        # for checking file paths
from tests.support import get_method_names                  # for direct test-suite construction


class TestPathValidation(TestCase):
    '''
    @brief Tests shared path validation functions.

    @details Verifies that each validator accepts only existing paths of its requested type.
    '''

    def test_validate_dir_accepts_only_existing_directories(self):
        '''
        @brief Test directory path validation.

        @details Accepts an existing directory and rejects empty, missing, and file paths.

        @param self {TestPathValidation} The instance of the test class.
        '''

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "audio.mp3")
            with open(file_path, "w", encoding="utf-8"):
                pass

            self.assertTrue(validate_dir(temp_dir))
            self.assertFalse(validate_dir(""))
            self.assertFalse(validate_dir(os.path.join(temp_dir, "missing")))
            self.assertFalse(validate_dir(file_path))


    def test_validate_file_accepts_only_existing_files(self):
        '''
        @brief Test file path validation.

        @details Accepts an existing file and rejects empty, missing, and directory paths.

        @param self {TestPathValidation} The instance of the test class.
        '''

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "audio.mp3")
            with open(file_path, "w", encoding="utf-8"):
                pass

            self.assertTrue(validate_file(file_path))
            self.assertFalse(validate_file(""))
            self.assertFalse(validate_file(os.path.join(temp_dir, "missing")))
            self.assertFalse(validate_file(temp_dir))


if __name__ == "__main__":
    '''
    @brief Entry point for running the test suite.

    @details Collects all test methods from the TestPathValidation class and executes them using a unittest test runner.

    @note This test module can be run directly with `python tests/test_validation.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestPathValidation)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestPathValidation(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
