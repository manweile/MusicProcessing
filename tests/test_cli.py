#!/usr/bin/env python3
'''
@class TestCli
@file test_cli.py
@author Gerald Manweiler

@brief Defines tests for the extracted CLI modules.

@details Verifies parser construction and command dispatch without invoking main.py.

@version 1.0.0
@date 2026-11-11

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import argparse                                             # for constructing parsed argument namespaces
import os                                                   # for operating-system path operations
import unittest                                             # for direct test-suite execution
from pathlib import Path                                    # for resolving test fixtures
from unittest import TestCase                               # for test-case assertions
from unittest.mock import Mock                              # for isolated command handlers
from unittest.mock import patch                             # for replacing command dependencies

# Local Module Methods
from src.cli import build_parser                            # for creating the CLI parser
from src.cli import run_cli_command                         # for dispatching parsed commands

from tests.support import get_method_names                  # for direct test-suite construction

#  Local Module Constants
from src.core.constants import MUSIC_TLD                    # top level directory for music files
from src.core.constants import UTF8                         # utf-8 encoding constant

# Local Modules Classes
from src.cli import commands                                # for patching command logging


class TestCli(TestCase):
    '''
    @brief Tests the extracted CLI modules.

    @details Verifies parser parity and independently callable command dispatch.
    '''


    def test_build_parser_help_matches_baseline(self):
        '''
        @brief Tests that new parser help matches the recorded baseline.

        @details Builds the extracted parser with the existing main.py program name.

        @note Test is coupled to the baseline textfile. Textfile must be kept up-to-date with any changes to the parser help output.

        @test Happy path.

        @param self {TestCli} The instance of the test class.
        '''

        baseline_path = Path(__file__).with_name("cli help baseline.txt")
        expected_help = baseline_path.read_text(encoding=UTF8).splitlines()
        parser = build_parser(prog="main.py")

        self.assertEqual(expected_help, parser.format_help().splitlines())


    def test_build_parser_sets_handler_and_validates_paths(self):
        '''
        @brief Tests parser handler wiring and path validation.

        @details Parses an existing directory and rejects a missing file path.

        @note Test is coupled to the subcommand. Subcommand changes require the test arguments updated accordingly.

        @test Happy path and validation error.

        @param self {TestCli} The instance of the test class.
        '''

        # prepare the path to the music top-level directory for testing
        music_path = Path(__file__).with_name(MUSIC_TLD)
        # build the parser for the CLI commands
        parser = build_parser(prog="main.py")
        # parse the arguments for the "get-audio-file-list" subcommand
        args = parser.parse_args(["get-audio-file-list", str(music_path)])

        self.assertEqual("get-audio-file-list", args.subcommand)
        self.assertEqual(str(music_path), args.tld)
        self.assertEqual(commands.get_audio_file_list, args.func)

        missing_path = os.path.join(str(music_path), "missing.mp3")
        with self.assertRaises(SystemExit):
            parser.parse_args(["clip-check-file", missing_path])


    def test_run_cli_command_dispatches_handler(self):
        '''
        @brief Tests command dispatch with parsed argument values.

        @details Uses a mock handler to verify dispatch without running a model operation.

        @note Test is coupled to the subcommand. Subcommand changes require the test arguments updated accordingly.

        @test Happy path.

        @param self {TestCli} The instance of the test class.
        '''

        handler = Mock()
        # prepare the parsed arguments for the CLI command
        args = argparse.Namespace(subcommand="get-audio-file-list", func=handler, tld=MUSIC_TLD)
        # run the CLI command with the prepared arguments
        exit_code = run_cli_command(args)

        self.assertEqual(0, exit_code)
        handler.assert_called_once_with(MUSIC_TLD)


    def test_run_cli_command_reports_handler_errors(self):
        '''
        @brief Tests command dispatch error reporting.

        @details Confirms handler failures are logged, printed, and return a nonzero exit code.

        @note Test is coupled to the subcommand. Subcommand changes require the test arguments updated accordingly.

        @test Error case.

        @param self {TestCli} The instance of the test class.
        '''

        # prepare a mock handler that raises an exception to simulate a failure scenario
        handler = Mock(side_effect=RuntimeError("operation failed"))
        args = argparse.Namespace(subcommand="get-audio-file-list", func=handler, tld=MUSIC_TLD)

        # logger patch object to capture exception logging during handler failure
        with patch.object(commands.logger, "exception") as log_exception:
            # patch the built-in print function to capture error messages during handler failure
            with patch("builtins.print") as print_error:
                exit_code = run_cli_command(args)

        self.assertEqual(1, exit_code)
        log_exception.assert_called_once()
        print_error.assert_called_once_with("Error in subcommand 'get-audio-file-list': RuntimeError: operation failed")


    def test_run_cli_command_without_subcommand_succeeds(self):
        '''
        @brief Tests dispatch with no selected subcommand.

        @details Returns success without invoking a command when no subcommand was selected.

        @test Edge case.

        @param self {TestCli} The instance of the test class.
        '''

        self.assertEqual(0, run_cli_command(argparse.Namespace(subcommand=None)))


if __name__ == "__main__":
    '''
    @brief Runs the CLI tests directly.

    @details Collects test methods and executes them with a text runner.
    '''

    methods = get_method_names(TestCli)
    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestCli(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
