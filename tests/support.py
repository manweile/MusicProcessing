'''
@package tests.support
@file tests/support.py
@author Gerald Manweiler

@brief Defines shared test support functions.

@details Provides utilities used by multiple test modules.

@version 1.0.0
@date 2026-10-21

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import inspect                                              # for test method discovery

# Local Module Classes
from src.core.progress import ProgressReporter              # progress reporting interface


class FakeProgress(ProgressReporter):
    '''
    @brief Records progress calls for tests.

    @details Captures operation starts, advances, and finishes without displaying progress.
    '''


    def __init__(self, elapsed_time: float = 0.0):
        '''
        @brief Initializes the fake progress reporter.

        @details Initializes empty call records and the elapsed time returned by finish().

        @param self {FakeProgress} The progress reporter.
        @param elapsed_time {float} The elapsed time finish() returns.
        '''

        # Initialize call records for advances, starts, and finish calls.
        self.advances: list[int] = []
        self.elapsed_time = elapsed_time
        self.finish_calls = 0
        self.starts: list[tuple[int | None, str]] = []


    def advance(self, step: int):
        '''
        @brief Records a progress advance.

        @details Appends the completed step count to the call record.

        @param self {FakeProgress} The progress reporter.
        @param step {int} The number of completed steps.
        '''

        self.advances.append(step)


    def finish(self) -> float:
        '''
        @brief Records completion and returns the configured elapsed time.

        @details Increments the finish-call count.

        @param self {FakeProgress} The progress reporter.

        @retval {float} The configured elapsed time in seconds.
        '''

        # Record the finish call and return the configured elapsed time.
        self.finish_calls += 1
        return self.elapsed_time


    def start(self, total: int | None, description: str):
        '''
        @brief Records the start of a progress operation.

        @details Appends the total and description to the call record.

        @param self {FakeProgress} The progress reporter.
        @param total {int | None} The total number of progress steps, or None for indeterminate progress.
        @param description {str} A description of the operation.
        '''

        # Record the start call with the total and description.
        self.starts.append((total, description))


def get_method_names(cls) -> list[str]:
    '''
    @brief Get names of test methods defined by a class.

    @details Filters class methods to names that begin with the test prefix.

    @param cls {type} Class containing test methods.

    @retval method_names {list[str]} Names of test methods defined by the class.
    '''

    method_names = []

    # Iterate over all members of the class and collect test method names.
    for name, obj in inspect.getmembers(cls):
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            if name.startswith('test_'):
                method_names.append(name)

    return method_names
