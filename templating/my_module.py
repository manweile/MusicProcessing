
'''
@file my_module.py
@brief Defines the my class class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import logging
import os
# import ipsumlorem
# from ipsum import lorem

# third party modules
# import ipsumlorem
# from ipsum import lorem

# local module methods
from src import add_module_handler
# local module constants
# from src import IPSUM_LOREM
# from src.generated_files import GENERATED_FILES
# local module errors
# from src import IpsumLoremError
# local module classes
# from src.dolor import IpsumLorem

gc.enable()

## @var logger
# @brief the logger instance for module
# @details sets the logger name to module name
logger = logging.getLogger(__name__)

## @var basename
# @brief name for logger file handler log file
# @details gets the module file name
basename = os.path.basename(__file__)

add_module_handler(logger, basename)

# instantiate classes here
# ipsum_lorem = IpsumLorem()

# instantiate module levels vars here
# IPSUM_LOREM = "ipsum lorem"


class MyClass():
    '''
    @brief Defines the base my class processing used by project.
    '''

    def __init__(self) -> None:
        '''
        @brief Initialize the MyClass class.

        @details A basic class implementation with no instantiation parameters.

        @return MyClass {instance} An instance of the class.
        '''

        pass
