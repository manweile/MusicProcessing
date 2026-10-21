'''
@module tests.support
@file support.py
@author Gerald Manweiler

@brief Defines shared test support functions.

@details Provides utilities used by multiple test modules.

@version 1.0.0
@date 2026-10-21

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import inspect                                              # for test method discovery


def get_method_names(cls):
    '''
    @brief Get names of test methods defined by a class.

    @details Filters class methods to names that begin with the test prefix.

    @param cls {type} Class containing test methods.
    @return method_names {list[str]} Names of test methods defined by the class.
    '''

    method_names = []
    for name, obj in inspect.getmembers(cls):
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            if name.startswith('test_'):
                method_names.append(name)
    return method_names
