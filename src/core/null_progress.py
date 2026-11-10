'''
@class NullProgress
@file null_progress.py
@author Gerald Manweiler

@brief Defines the no-op progress reporter class.

@details Supports headless operation without displaying progress.

@version 1.0.0
@date 2026-11-09

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''


class NullProgress:
    '''
    @brief Provides a no-op progress reporter.

    @details Supports headless operation without displaying progress.
    '''


    def start(self, total: int | None, description: str) -> None:
        '''
        @brief Starts a no-op progress operation.

        @details Accepts progress details without displaying them.

        @param self {NullProgress} The progress reporter.
        @param total {int | None} The total number of progress steps, or None for indeterminate progress.
        @param description {str} A description of the operation.
        '''

        pass


    def advance(self, step: int) -> None:
        '''
        @brief Advances a no-op progress operation.

        @details Accepts progress steps without displaying them.

        @param self {NullProgress} The progress reporter.
        @param step {int} The number of completed progress steps.
        '''

        pass


    def finish(self) -> float:
        '''
        @brief Finishes a no-op progress operation.

        @details Returns zero because no elapsed time is tracked.

        @param self {NullProgress} The progress reporter.

        @retval {float} Zero elapsed seconds.
        '''

        return 0.0
