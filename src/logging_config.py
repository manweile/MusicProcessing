'''
@module logging_config
@file src/logging_config.py
@author Gerald Manweiler

@brief Defines the logging configuration module shim.

@details Re-exports the configuration for package and module file logging shim.

@version 1.0.0
@date 2026-09-16

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Local Modules
from src.core.logging_config import add_module_handler        # Shim for old import path
from src.core.logging_config import configure_logging # Shim for old import path
