'''
@file level_filter.py
@brief Defines the level filter class.

@details from https://stackoverflow.com/questions/36337244/logging-how-to-set-a-maximum-log-level-for-a-handler/36338212#36338212
@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

from logging import Filter


class LevelFilter(Filter):
    '''
    @brief Defines base level filtering used by project.
    '''

    def __init__(self, low, high):
        '''
        @brief Initializes the LevelFilter class.

        @param low {int} The lowest log level.
        @param high {int} The highest log level.
        '''

        self._low = low
        self._high = high
        Filter.__init__(self)


    def filter(self, record):
        '''
        @brief Checks if log record log level is in specified level range.

        @param record {LogRecord} The log record instance emitted when an event is logged.
        @returns {bool} True if record level is in specified level range, False otherwise.
        '''

        if self._low <= record.levelno <= self._high:
            return True

        return False
