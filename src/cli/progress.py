'''
@module progress
@file progress.py
@author Gerald Manweiler

@brief Defines command-line progress reporters.

@details Adapts tqdm and yaspin displays to the shared progress interface.

@version 1.0.0
@date 2026-11-10

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import time                                                 # for elapsed-time measurement

# Third Party Modules
from tqdm import tqdm                                       # for command-line progress bars

# Local Module Classes
from src.core.progress import ProgressReporter              # progress reporting interface


class SpinnerProgress(ProgressReporter):
    '''
    @brief Displays indeterminate progress through yaspin.

    @details Provides the command-line spinner for long-running operations.
    '''


    def __init__(self):
        '''
        @brief Initializes the spinner progress reporter.

        @details Defers creating the spinner until an operation starts.

        @param self {SpinnerProgress} The progress reporter.
        '''

        self._spinner = None


    def advance(self, step: int):
        '''
        @brief Accepts a progress advance.

        @details The spinner reporter only supports indeterminate progress.

        @param self {SpinnerProgress} The progress reporter.
        @param step {int} The number of completed steps.
        '''

        pass


    def finish(self) -> float:
        '''
        @brief Stops the spinner and returns elapsed time.

        @details Stops the active spinner when one has been started.

        @param self {SpinnerProgress} The progress reporter.

        @retval {float} Elapsed time in seconds.
        '''

        if self._spinner is None:
            return 0.0

        spinner = self._spinner
        self._spinner = None
        spinner.__exit__(None, None, None)

        return spinner.elapsed_time


    def start(self, total: int | None, description: str):
        '''
        @brief Starts the CLI spinner.

        @details Creates a yaspin spinner for indeterminate progress.

        @param self {SpinnerProgress} The progress reporter.
        @param total {int | None} The total progress steps, or None for indeterminate progress.
        @param description {str} A description of the operation.
        '''

        from yaspin import yaspin                            # for command-line spinner display
        from yaspin.spinners import Spinners                 # for the CLI spinner definition

        self._spinner = yaspin(Spinners.dots, text=description, timer=True)
        self._spinner.__enter__()


class TqdmProgress(ProgressReporter):
    '''
    @brief Displays progress through tqdm.

    @details Provides the command-line presentation for model progress updates.
    '''


    def __init__(self):
        '''
        @brief Initializes the progress reporter.

        @details Defers creating the progress bar until an operation starts.

        @param self {TqdmProgress} The progress reporter.
        '''

        self._bar: tqdm | None = None
        self._started_at: float | None = None


    def advance(self, step: int):
        '''
        @brief Advances the progress bar.

        @details Updates the active tqdm bar by the specified number of steps.

        @param self {TqdmProgress} The progress reporter.
        @param step {int} The number of completed steps.

        @exception RuntimeError No progress operation has been started.
        '''

        if self._bar is None:
            raise RuntimeError("Progress has not been started.")

        self._bar.update(step)


    def finish(self) -> float:
        '''
        @brief Finishes the progress bar.

        @details Closes the active bar and returns the elapsed time in seconds.

        @param self {TqdmProgress} The progress reporter.

        @retval elapsed {float} Elapsed time in seconds.

        @exception RuntimeError No progress operation has been started.
        '''

        if self._bar is None or self._started_at is None:
            raise RuntimeError("Progress has not been started.")

        self._bar.close()
        elapsed = time.perf_counter() - self._started_at
        self._bar = None
        self._started_at = None

        return elapsed


    def start(self, total: int | None, description: str):
        '''
        @brief Starts a tqdm progress bar.

        @details Creates a command-line progress bar for the operation.

        @param self {TqdmProgress} The progress reporter.
        @param total {int | None} The total number of progress steps, or None for indeterminate progress.
        @param description {str} A description of the operation.
        '''

        self._started_at = time.perf_counter()
        self._bar = tqdm(desc=description, total=total, unit=" items")
