'''
@module parser
@file parser.py
@author Gerald Manweiler

@brief Defines the command-line parser module.

@details Builds the command-line parser and validates its file-system arguments.

@version 1.0.0
@date 2026-11-11

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import argparse                                             # for parsing command-line arguments
import os                                                   # for checking file-system paths
import re                                                   # for formatting argument help
import shutil                                               # for determining terminal width
import sys                                                  # for identifying standard error

# Local Module Methods
import src.cli.commands as commands                        # for subcommand handlers
import src.cli.constants as constants                      # for argument names and help text


class CustomArgumentParser(argparse.ArgumentParser):
    '''
    @brief Defines an argument parser that logs errors.

    @details Applies the custom help formatter and logs messages sent to standard error.
    '''


    def __init__(self, *args, **kwargs):
        '''
        @brief Initializes the argument parser.

        @details Uses the custom help formatter unless a formatter is explicitly provided.

        @param self {CustomArgumentParser} The argument parser.
        @param args {*args} Positional arguments for the argument parser.
        @param kwargs {**kwargs} Keyword arguments for the argument parser.
        '''

        kwargs.setdefault("formatter_class", CustomHelpFormatter)
        super().__init__(*args, **kwargs)


    def _print_message(self, message, file=None):
        '''
        @brief Logs parser messages written to standard error.

        @details Preserves the default output behavior while logging error messages.

        @param self {CustomArgumentParser} The argument parser.
        @param message {str} The message being printed.
        @param file {TextIOWrapper} The destination stream.
        '''

        if message:
            if file is sys.stderr:
                import logging                                  # for recording parser errors

                logging.getLogger(__name__).error(f"Argparse Error: {message.strip()}")

            super()._print_message(message, file)


class CustomHelpFormatter(argparse.HelpFormatter):
    '''
    @brief Defines the command-line help formatter.

    @details Aligns root help and subcommand descriptions at a consistent column.
    '''


    def __init__(self, prog):
        '''
        @brief Initializes the help formatter.

        @details Sets the description column far enough right for long command names.

        @param self {CustomHelpFormatter} The help formatter.
        @param prog {str} The program name displayed in usage.
        '''

        max_help_position = 60
        width = max(shutil.get_terminal_size().columns - 2, 220)
        super().__init__(prog, max_help_position=max_help_position, width=width)


    def _format_action(self, action) -> str:
        '''
        @brief Formats help descriptions at a fixed column.

        @details Aligns root options and subcommand descriptions with the baseline CLI.

        @param self {CustomHelpFormatter} The help formatter.
        @param action {argparse.Action} The action being formatted.

        @retval {str} The formatted help string.
        '''

        root_help_action = (action.dest == "help" and action.option_strings and os.path.basename(self._prog) == "main.py")
        subcommand_action = isinstance(action, argparse._SubParsersAction._ChoicesPseudoAction)

        if root_help_action or subcommand_action:
            action_max_length = self._action_max_length
            self._action_max_length = self._max_help_position - 2

            try:
                formatted = super()._format_action(action)
            finally:
                self._action_max_length = action_max_length

            return formatted

        return super()._format_action(action)


## @name Helper Functions
## @{
def build_parser(prog: str | None = None) -> CustomArgumentParser:
    '''
    @brief Builds the command-line argument parser.

    @details Creates all subcommands, preserves their validation, and appends argument help to the command list.

    @param prog {str | None} Optional program name displayed in usage.

    @retval {CustomArgumentParser} The configured command-line parser.
    '''

    command_specs = (
        ("gui", "Run in GUI mode", commands.gui, ()),
        (
            "clip-check-file",
            "Check peak/RMS/EBU R128 leveling for single audio file",
            commands.clip_check_file,
            ((constants.ARG_CLI_FILE, existing_file, constants.ARG_HELP_AUDIO, False),)
        ),
        (
            "clip-check-walk",
            "Check peak/RMS/EBU R128 leveling for multiple audio files",
            commands.clip_check_walk,
            ((constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD_FLD, False),)
        ),
        (
            "convert-file",
            "Convert audio file to mp3",
            commands.convert_file,
            (
                (constants.ARG_CLI_FILE, existing_file, constants.ARG_HELP_AUDIO, False),
                (constants.ARG_CLI_TARGET, existing_path, constants.ARG_HELP_OPT_TARGET, True)
            )
        ),
        (
            "convert-walk",
            "Convert audio files to mp3",
            commands.convert_walk,
            (
                (constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD_FLD_SLD, False),
                (constants.ARG_CLI_PATTERN, str, constants.ARG_HELP_OPT_PATTERN, True),
                (constants.ARG_CLI_TARGET, existing_path, constants.ARG_HELP_OPT_TARGET, True)
            )
        ),
        (
            "create-albums",
            "Create album sub-directories",
            commands.create_albums,
            ((constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD, False),)
        ),
        (
            "ebu-file",
            "EBU R128 level audio file",
            commands.ebu_file,
            (
                (constants.ARG_CLI_FILE, existing_file, constants.ARG_HELP_AUDIO, False),
                (constants.ARG_CLI_TARGET, existing_path, constants.ARG_HELP_OPT_TARGET, True)
            )
        ),
        (
            "extract-album-art",
            "Extract audio file embedded art",
            commands.extract_album_art,
            ((constants.ARG_CLI_FILE, existing_file, constants.ARG_HELP_AUDIO, False),)
        ),
        (
            "extract-walk",
            "Extract audio files embedded art",
            commands.extract_walk,
            (
                (constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD_FLD, False),
                (constants.ARG_CLI_PATTERN, str, constants.ARG_HELP_OPT_PATTERN, True)
            )
        ),
        (
            "get-audio-file-list",
            "Get list of audio file paths",
            commands.get_audio_file_list,
            ((constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD_FLD, False),)
        ),
        (
            "get-ext-file-list",
            "Get list of audio file extensions",
            commands.get_ext_file_list,
            (
                (constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD_FLD, False),
                (constants.ARG_CLI_PATTERN, str, constants.ARG_HELP_OPT_PATTERN, True)
            )
        ),
        (
            "get-media-info-walk",
            "Get list of audio files media info",
            commands.get_media_info_walk,
            (
                (constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD_FLD, False),
                (constants.ARG_CLI_PATTERN, str, constants.ARG_HELP_OPT_PATTERN, True)
            )
        ),
        (
            "get-tags-walk",
            "Get list of audio files metadata tags",
            commands.get_tags_walk,
            (
                (constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD_FLD, False),
                (constants.ARG_CLI_PATTERN, str, constants.ARG_HELP_OPT_PATTERN, True),
                (constants.ARG_CLI_FFPROBE, bool, constants.ARG_HELP_OPT_FFPROBE, True)
            )
        ),
        (
            "level-normalize-walk",
            "Level normalize audio files",
            commands.level_normalize_walk,
            (
                (constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD_FLD, False),
                (constants.ARG_CLI_TYPE, str, constants.ARG_HELP_LEVEL, False),
                (constants.ARG_CLI_TARGET, existing_path, constants.ARG_HELP_OPT_TARGET, True)
            )
        ),
        (
            "normalize-filename",
            "Rename audio file from metadata",
            commands.normalize_filename,
            ((constants.ARG_CLI_FILE, existing_file, constants.ARG_HELP_AUDIO, False),)
        ),
        (
            "normalize-filename-walk",
            "Rename audio files from metadata",
            commands.normalize_filename_walk,
            ((constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD_FLD_SLD, False),)
        ),
        (
            "peak-file",
            "Peak level audio file",
            commands.peak_file,
            (
                (constants.ARG_CLI_FILE, existing_file, constants.ARG_HELP_AUDIO, False),
                (constants.ARG_CLI_TARGET, str, constants.ARG_HELP_OPT_TARGET, True)
            )
        ),
        (
            "remove-empty-albums",
            "Remove empty album sub-directories",
            commands.remove_empty_albums,
            ((constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD_FLD, False),)
        ),
        (
            "remove-pattern",
            "Remove files with specified pattern",
            commands.remove_pattern,
            (
                (constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD_FLD_SLD, False),
                (constants.ARG_CLI_PATTERN, str, constants.ARG_HELP_PATTERN, False)
            )
        ),
        (
            "remove-set-list",
            "Remove files matching hard-coded pattern set",
            commands.remove_set_list,
            ((constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD_FLD_SLD, False),)
        ),
        (
            "rename-album-directories",
            "Rename album paths from metadata",
            commands.rename_album_directories,
            ((constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD, False),)
        ),
        (
            "rms-file",
            "RMS level audio file",
            commands.rms_file,
            (
                (constants.ARG_CLI_FILE, existing_file, constants.ARG_HELP_AUDIO, False),
                (constants.ARG_CLI_TARGET, str, constants.ARG_HELP_OPT_TARGET, True)
            )
        ),
        (
            "set-album-art",
            "Set albums art file",
            commands.set_album_art,
            ((constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD_FLD, False),)
        ),
        (
            "update-genres",
            "Update songs genre from CSV",
            commands.update_genres,
            (
                (constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD, False),
                (constants.ARG_CLI_CSV, existing_file, constants.ARG_HELP_GENRE, False)
            )
        ),
        (
            "update-playlist",
            "Update playlist file songs path",
            commands.update_playlist,
            (
                (constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD, False),
                (constants.ARG_CLI_PLAYLIST, existing_file, constants.ARG_HELP_PLAYLIST, False)
            )
        ),
        (
            "update-walk",
            "Update playlist files songs path",
            commands.update_walk,
            ((constants.ARG_CLI_TLD, existing_path, constants.ARG_HELP_TLD, False),)
        )
    )

    parser = CustomArgumentParser(prog=prog, description="Music Processing")
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", metavar="command")

    for command, help_text, handler, arguments in command_specs:
        command_parser = subparsers.add_parser(command, help=help_text)

        for name, argument_type, argument_help, optional in arguments:
            argument_name = "--" + name if optional else name
            command_parser.add_argument(argument_name, type=argument_type, help=argument_help)

        command_parser.set_defaults(func=handler)

    for choice_action in subparsers._choices_actions:
        sub_actions = [
            action
            for action in subparsers.choices[choice_action.dest]._actions
            if not isinstance(action, argparse._HelpAction)
        ]
        sub_actions.sort(key=lambda action: bool(action.option_strings))
        argument_help = [
            re.sub(r"^(mandatory|optional)\s+", r"\1: ", action.help)
            for action in sub_actions
            if action.help
        ]

        if argument_help:
            choice_action.help += "; " + "; ".join(argument_help)

        argument_usage = [
            f"{action.option_strings[0]} {action.dest}"
            if action.option_strings and action.nargs != 0
            else (action.option_strings[0] if action.option_strings else action.dest)
            for action in sub_actions
        ]
        choice_action.metavar = " ".join([choice_action.dest] + argument_usage)

    return parser


def existing_file(file: str) -> str:
    '''
    @brief Checks whether a file exists.

    @details Raises an argument error when the specified file does not exist.

    @param file {str} The file path.

    @retval {str} The validated file path.

    @exception {ArgumentTypeError} Indicates the file was not found.
    '''

    if not os.path.isfile(file):
        raise argparse.ArgumentTypeError(f"File not found: {file}")

    return file


def existing_path(path: str) -> str:
    '''
    @brief Checks whether a directory exists.

    @details Raises an argument error when the specified directory does not exist.

    @param path {str} The directory path.

    @retval {str} The validated directory path.

    @exception {ArgumentTypeError} Indicates the directory was not found.
    '''

    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"Directory not found: {path}")

    return path
## @}
