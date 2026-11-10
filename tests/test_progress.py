'''
@class TestProgress
@file test_progress.py
@author Gerald Manweiler

@brief Defines the progress interface tests.

@details Tests recording progress reporter behavior.

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
from tests.support import FakeProgress                      # recording progress reporter


class TestProgress(TestCase):
    '''
    @brief Tests progress reporter semantics.

    @details Verifies no-op behavior and recorded progress values.
    '''


    def test_fake_progress_records_calls_and_elapsed_time(self):
        '''
        @brief Tests FakeProgress recording and elapsed time.

        @details Verifies operation details, advances, and finish return values are recorded.

        @param self {TestProgress} The instance of the test class.
        '''

        progress = FakeProgress(2.5)

        progress.start(5, "Processing files")
        progress.advance(2)
        elapsed_time = progress.finish()

        self.assertEqual([(5, "Processing files")], progress.starts)
        self.assertEqual([2], progress.advances)
        self.assertEqual(1, progress.finish_calls)
        self.assertEqual(2.5, elapsed_time)


if __name__ == "__main__":
    '''
    @brief Run the Progress test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.

    @note This test module can be run directly with `python tests/test_progress.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestProgress)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestProgress(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
