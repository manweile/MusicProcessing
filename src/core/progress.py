'''
@module src.core.progress
@file progress.py
@author Gerald Manweiler

@brief Defines the progress reporting interface.

@details Provides a shared protocol for reporting operation progress.

@version 1.0.0
@date 2026-11-09

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
from typing import Protocol                                 # for progress reporter interfaces


class ProgressReporter(Protocol):
    '''
    @brief Defines the interface for reporting operation progress.

    @details Separates operation progress from the display used by a frontend.
    '''


    def start(self, total: int | None, description: str) -> None:
        '''
        @brief Starts reporting progress for an operation.

        @details A missing total indicates indeterminate progress.

        @param self {ProgressReporter} The progress reporter.
        @param total {int | None} The total number of progress steps, or None for indeterminate progress.
        @param description {str} A description of the operation.
        '''

        pass


    def advance(self, step: int) -> None:
        '''
        @brief Advances progress by the specified number of steps.

        @details Reports completed work to the configured frontend.

        @param self {ProgressReporter} The progress reporter.
        @param step {int} The number of completed progress steps.
        '''

        pass


    def finish(self) -> float:
        '''
        @brief Finishes progress reporting.

        @details Returns the elapsed time for the operation in seconds.

        @param self {ProgressReporter} The progress reporter.

        @retval {float} Elapsed time in seconds.
        '''

        pass
