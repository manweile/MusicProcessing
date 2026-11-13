'''
@class TestTaskRunner
@file test_task_runner.py
@author Gerald Manweiler

@brief Defines the test task runner class.

@details Verifies background task execution and outcome dispatch.

@version 1.0.0
@date 2026-11-13

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import unittest                                             # for direct test-suite execution
from unittest import TestCase                               # for test-case assertions
from unittest.mock import Mock                              # for task runner callback tests
from unittest.mock import patch                             # for replacing worker threads

# Local Module Methods
from tests.support import get_method_names                  # for direct test-suite construction

# Local Module Classes
from src.controllers.task_runner import TaskRunner          # for task runner instantiation and worker execution tests


class TestTaskRunner(TestCase):
    '''
    @brief Tests task runner behavior.

    @details Verifies thread startup, successful completion, and task failure handling.
    '''

    def setUp(self):
        '''
        @brief Initialize callback test doubles.

        @details Records callbacks dispatched by a task runner.

        @param self {TestTaskRunner} The instance of the test class.
        '''

        self.logs = []
        self.scheduled = []
        self.busy_states = []
        self.show_error = Mock()
        self.runner = TaskRunner(
            log=self.logs.append,
            call_after=lambda callback, *args: self.scheduled.append((callback, args)),
            set_busy_state=self.busy_states.append,
            show_error=self.show_error
        )


    def test_run_task_starts_daemon_worker(self):
        '''
        @brief Test that run_task starts a daemon worker thread.

        @details Verifies busy-state activation and worker arguments.

        @param self {TestTaskRunner} The instance of the test class.
        '''


        def task(value):
            '''
            @brief Task function for testing.

            @details Returns the provided value.

            @param value {str} The value to return.
            '''

            return value


        on_success = Mock()

        # patch the threading.Thread class to intercept thread creation
        with patch("src.controllers.task_runner.threading.Thread") as thread_class:
            self.runner.run_task(task, "value", on_success=on_success)

        # verify that the thread was started with the correct target and arguments
        thread_class.assert_called_once_with(target=self.runner.worker, args=(task, ("value",), on_success), daemon=True)

        # verify that the thread was started as a daemon
        thread_class.return_value.start.assert_called_once_with()

        self.assertEqual(self.busy_states, [True])


    def test_worker_dispatches_success_and_restores_idle_state(self):
        '''
        @brief Test successful worker execution.

        @details Runs the task and verifies that success and idle callbacks are scheduled.

        @param self {TestTaskRunner} The instance of the test class.
        '''

        values = []


        def task(value):
            '''
            @brief Task function for testing.

            @details Appends the provided value to the values list.

            @param value {str} The value to append.
            '''

            values.append(value)


        # define the success callback for the task
        on_success = Mock()

        # run the worker with the task and the success callback
        self.runner.worker(task, ("value",), on_success=on_success)

        running_task = ["Running task...", "task completed."]
        scheduled_task = [(on_success, ()), (self.runner._set_busy_state, (False,))]

        self.assertEqual(values, ["value"])
        self.assertEqual(self.logs, running_task)
        self.assertEqual(self.scheduled, scheduled_task)


    def test_worker_dispatches_error_and_restores_idle_state(self):
        '''
        @brief Test worker handling of task failures.

        @details Verifies errors are logged, reported, and followed by idle-state dispatch.

        @param self {TestTaskRunner} The instance of the test class.
        '''


        def task():
            '''
            @brief Task function that raises an error.

            @details Simulates a task failure by raising a RuntimeError.
            '''

            raise RuntimeError("task failed")


        with self.assertLogs("src.controllers.task_runner", level="ERROR"):
            self.runner.worker(task, ())

        running_task = ["Running task...", "task failed: task failed"]
        scheduled_task = [(self.show_error, ("task failed",)), (self.runner._set_busy_state, (False,))]

        self.assertEqual(self.logs, running_task)
        self.assertEqual(self.scheduled, scheduled_task)


if __name__ == "__main__":
    '''
    @brief Entry point for running the test suite.

    @details Collects all test methods from the TestTaskRunner class and executes them using a unittest test runner.

    @note This test module can be run directly with `python tests/test_task_runner.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestTaskRunner)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestTaskRunner(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
