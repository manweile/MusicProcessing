'''
@module src.controllers.task_runner
@file task_runner.py
@author Gerald Manweiler

@brief Defines the shared task runner.

@details Runs long tasks on daemon threads and dispatches their outcomes through injected callbacks.

@version 1.0.0
@date 2026-11-13

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import logging                                              # for recording task failures
import threading                                            # for running tasks in background threads
from typing import Any                                      # for task values and callback arguments
from typing import Callable                                 # for callback type hints
from typing import Optional                                 # for optional success callbacks
from typing import Tuple                                    # for worker argument tuples


class TaskRunner:
    '''
    @brief Runs tasks in background threads.

    @details Uses injected callbacks to keep GUI-specific behavior outside the task runner.
    '''

    def __init__(
        self,
        log: Callable[[str], None],
        call_after: Callable[..., Any],
        set_busy_state: Callable[[bool], None],
        show_error: Callable[[str], None]
    ):
        '''
        @brief Initialize the task runner.

        @details Stores callbacks for logging and dispatching task results.

        @param self {TaskRunner} The instance of the class.
        @param log {Callable} Callback for logging task progress.
        @param call_after {Callable} Callback for dispatching work on the owning thread.
        @param set_busy_state {Callable} Callback for updating the busy state.
        @param show_error {Callable} Callback for displaying task errors.
        '''

        self._log = log
        self._call_after = call_after
        self._set_busy_state = set_busy_state
        self._show_error = show_error


    def run_task(self, func: Callable[..., Any], *args: Any, on_success: Optional[Callable[[], Any]] = None):
        '''
        @brief Start a task in a daemon thread.

        @details Sets the application to busy and starts a worker thread for the given function.

        @param self {TaskRunner} The instance of the class.
        @param func {Callable} The function to run.
        @param args {Any} Arguments to pass to the function.
        @param on_success {Optional[Callable]} Callback to dispatch after successful completion.
        '''

        # set the application to busy and start the worker thread for the task
        self._set_busy_state(True)
        threading.Thread(target=self.worker, args=(func, args, on_success), daemon=True).start()


    def worker(self, func: Callable[..., Any], args: Tuple[Any, ...], on_success: Optional[Callable[[], Any]] = None):
        '''
        @brief Run a task and dispatch its outcome.

        @details Logs task progress, dispatches success or error callbacks, and restores the idle state.

        @param self {TaskRunner} The instance of the class.
        @param func {Callable} The function to run.
        @param args {Tuple} Arguments to pass to the function.
        @param on_success {Optional[Callable]} Callback to dispatch after successful completion.
        '''

        # log the start of the task execution
        self._log(f"Running {func.__name__}...")

        try:
            # execute the task function with the provided arguments and log its completion
            func(*args)
            self._log(f"{func.__name__} completed.")

            # dispatch the success callback if provided
            if on_success:
                self._call_after(on_success)

        except Exception as error:
            # log the exception and prepare to dispatch the error callback
            logging.getLogger(__name__).exception("Task %s failed", func.__name__)
            self._log(f"{func.__name__} failed: {error}")

            # dispatch the error callback with the error message
            self._call_after(self._show_error, str(error))
        finally:
            # ensure the busy state is reset to idle regardless of task outcome
            self._call_after(self._set_busy_state, False)
