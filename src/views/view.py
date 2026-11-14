'''
@class View
@file view.py
@author Gerald Manweiler

@brief Defines the application view interface.

@details Describes the user-facing operations required by application controllers.

@version 1.0.0
@date 2026-11-13

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
from typing import Protocol                                 # for defining view interfaces


class View(Protocol):
    '''
    @brief Defines the application view interface.

    @details Controllers use this protocol to present messages and communicate application state.
    '''


    def show_error(self, message: str):
        '''
        @brief Display an error message.

        @details The concrete view decides how to present the error.

        @param self {View} The view instance.
        @param message {str} The error message to display.
        '''

        # display an error message to the user in the concrete view implementation
        ...


    def show_generated_files(self):
        '''
        @brief Display generated files.

        @details The concrete view decides how generated files are presented.

        @param self {View} The view instance.
        '''

        # display generated files to the user in the concrete view implementation
        ...


    def show_message(self, message: str):
        '''
        @brief Display an informational message.

        @details The concrete view decides how to present the message.

        @param self {View} The view instance.
        @param message {str} The message to display.
        '''

        # display an informational message to the user in the concrete view implementation
        ...


    def set_busy(self, busy: bool):
        '''
        @brief Set whether the application is busy.

        @details The concrete view decides how the busy state is presented.

        @param self {View} The view instance.
        @param busy {bool} True when work is in progress, otherwise False.
        '''

        # Set the busy state of the application in the concrete view implementation
        ...
