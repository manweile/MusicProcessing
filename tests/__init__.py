'''
@brief Gets directory name for importing by other modules.
'''

import os

## @var TESTS
# @brief Path to where test files and inputs used by the tests are stored.
# @details Getting the directory name for importing means will not need a hard coded "magic spell" else where in codebase.
TEST_PATH = ""
TEST_PATH = os.path.dirname(os.path.abspath(__file__))

## @var __all__
# @brief Exposes variable for importing by other modules.
# @details In modules needing the directory, add `from src.tests.TEST_PATH`
__all__ = ["TEST_PATH"]
