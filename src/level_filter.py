'''
@class LevelFilter
@file level_filter.py
@author Gerald Manweiler

@brief Defines the level filter class.

@details from https://stackoverflow.com/questions/36337244/logging-how-to-set-a-maximum-log-level-for-a-handler/36338212#36338212

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import gc                                                   # for garbage collection
from logging import Filter                                  # Standard logging filter class used as base for LevelFilter

gc.enable()


class LevelFilter(Filter):
    '''
    @brief Defines base level filtering used by project.

    @details This class provides a logging filter that allows only log records within a specified level range to pass through.
    '''

    def __init__(self, low, high):
        '''
        @brief Initializes the LevelFilter class.

        @details Initializes the LevelFilter with the specified low and high log levels.

        @param low {int} The lowest log level.
        @param high {int} The highest log level.
        '''

        self._low = low
        self._high = high
        Filter.__init__(self)


    def filter(self, record):
        '''
        @brief Checks if log record log level is within the specified level range.

        @details Checks if the log record's level is within the instance's specified low and high level range.

        @param record {LogRecord} The log record instance emitted when an event is logged.
        @returns {bool} True if record level is in specified level range, False otherwise.
        '''

        if self._low <= record.levelno <= self._high:
            return True

        return False
