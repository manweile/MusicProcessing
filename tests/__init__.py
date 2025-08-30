'''
@package tests
@brief Gets directory name for importing by other modules.
'''

# standard modules
import os

# local module constants
from src import EXPORT_TLD

## @var TESTS_PATH
# @brief Path to where test files and inputs used by the tests are stored.
# @details Getting the directory name for importing means will not need a hard coded "magic spell" else where in codebase.
TESTS_PATH = ""
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))

## @var TESTS_TLD
# @brief Path to where music audio test files are stored.
# @details use this this when working with audio file tests.
TESTS_TLD = ""
TESTS_TLD = os.path.join(TESTS_PATH, EXPORT_TLD)

## @var __all__
# @brief Exposes variable for importing by other modules.
# @details In modules needing the directory, add `from src.tests.TESTS_PATH`
# @details In modules needing the directory, add `from src.tests.TESTS_TLD`
__all__ = ["TESTS_PATH", "TESTS_TLD"]
