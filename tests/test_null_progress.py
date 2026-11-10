'''
@class TestNullProgress
@file test_null_progress.py
@author Gerald Manweiler

@brief Defines the no-op progress reporter tests.

@details Tests no-op progress reporter behavior.

@version 1.0.0
@date 2026-11-09

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import unittest                                             # for test-case assertions
from unittest import TestCase                               # for test-case assertions and lifecycle hooks

# Local Module Methods
from tests.support import get_method_names                  # for direct test-suite construction

# Local Module Classes
from src.core.null_progress import NullProgress             # no-op progress reporter


class TestNullProgress(TestCase):
    '''
    @brief Tests no-op progress reporter semantics.

    @details Verifies progress calls are accepted and finish returns zero elapsed seconds.
    '''


    def test_null_progress_is_a_no_op(self):
        '''
        @brief Tests NullProgress no-op behavior.

        @details Verifies progress calls are accepted and finish returns zero elapsed seconds.

        @param self {TestNullProgress} The instance of the test class.
        '''

        progress = NullProgress()

        progress.start(None, "Processing files")
        progress.advance(1)

        self.assertEqual(0.0, progress.finish())


if __name__ == "__main__":
    '''
    @brief Run the NullProgress test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.

    @note This test module can be run directly with `python tests/test_null_progress.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestNullProgress)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestNullProgress(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
