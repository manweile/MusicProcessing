'''
@class ProgressReporter
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
    @brief Defines the protocol interface for reporting operation progress.

    @details Separates operation progress from the display used by a frontend.

    @note This protocol describes the progress-reporting behavior expected by operations that performs work.<br>
    A reporter receives notifications when an operation starts, advances, and finishes,
    while the implementation decides how those notifications are presented or recorded.<br>
    <br>
    Implementations may display progress in a user interface, record calls for tests, or intentionally do nothing.<br>
    This keeps the operation logic independent of any specific display library or frontend.<br>
    <br>
    `start()` receives the total number of steps when known. A total of `None` represents indeterminate progress.<br>
    `advance()` reports completed work, and `finish()` ends the operation and returns its elapsed time in seconds.<br>
    A no-op implementation may return `0.0` when it does not track elapsed time.
    '''


    def start(self, total: int | None, description: str) -> None:
        '''
        @brief Starts reporting progress for an operation.

        @details Protocol interface; a missing total indicates indeterminate progress.<br>
        Callers should not invoke protocol stub directly; it is intended to be implemented by concrete classes.

        @param self {ProgressReporter} The progress reporter.
        @param total {int | None} The total number of progress steps, or None for indeterminate progress.
        @param description {str} A description of the operation.

        @return {None} This function does not return any value.
        '''

        # mark method as declared but not implemented
        ...


    def advance(self, step: int) -> None:
        '''
        @brief Advances progress by the specified number of steps.

        @details Protocol interface; reports completed work to the configured frontend.<br>
        Callers should not invoke protocol stub directly; it is intended to be implemented by concrete classes.

        @param self {ProgressReporter} The progress reporter.
        @param step {int} The number of completed progress steps.

        @return {None} This function does not return any value.
        '''

        # mark method as declared but not implemented
        ...


    def finish(self) -> float:
        '''
        @brief Finishes progress reporting.

        @details Protocol interface; returns the elapsed time for the operation in seconds.<br>
        Callers should not invoke protocol stub directly; it is intended to be implemented by concrete classes.

        @param self {ProgressReporter} The progress reporter.

        @retval {float} Elapsed time in seconds.
        '''

        # mark method as declared but not implemented
        ...
