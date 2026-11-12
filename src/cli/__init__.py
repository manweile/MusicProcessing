'''
@package src.cli
@file src/cli/__init__.py
@author Gerald Manweiler

@brief Package for the MusicProcessing command-line interface.

@details Contains the command-line interface components for the application.

@version 1.0.0
@date 2026-11-02

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Local Module Methods
from src.cli.commands import run_cli_command                 # exposes CLI command dispatch
from src.cli.parser import build_parser                      # exposes CLI parser construction

## @var __all__
# @brief Exposes the public CLI entry points.
# @details Import `build_parser` to construct the CLI argument parser.
# @details Import `run_cli_command` to dispatch a parsed CLI command.
__all__ = [
    "build_parser",
    "run_cli_command"
]
