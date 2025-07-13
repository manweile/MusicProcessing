#!/usr/bin/env python3
'''
@brief Music Processing project executable script.

@details Run this script with appropriate input arguments to process audio files.
'''

# standard modules
import argparse
import gc

# third party modules
from gooey import Gooey, GooeyParser

# local modules
from src.audio_info import AudioArt
from src.audio_info import AudioMetadata
from src.audio_normalize import AudioNormalization
from src.dir_processing import DirectoryProcessing

gc.enable()

art = AudioArt()
directory = DirectoryProcessing()
metadata = AudioMetadata()
normalization = AudioNormalization()

running = True


def convert_file(file_path):
    '''
    @brief Converts specified audio file to mp3 format.

    @param file_path {str} The full path to audio file.
    '''

    metadata.convert_file(file_path)


@Gooey(optional_cols=2, program_name="Music Processing")
def parse_args():
    '''
    @brief

    @details
    @return
    '''

    parser = GooeyParser(description='Music Processing')
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    convert_file_parser = subparsers.add_parser("convert-file", help="Converts an audio file to mp3")
    convert_file_parser.add_argument("file", type=str, help="mandatory full path to audio file", widget="FileChooser")
    convert_file_parser.set_defaults(func=convert_file)

    args = parser.parse_args()
    return args


def main(args):
    '''
    @brief Module entry point.

    @details Takes command line arguments and executes per arguments.

    @param args {Namespace} Arguments for execution.
    @exception NotImplementedError A subcommand not implemented error.
    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        if args.subcommand == "convert-file":
            file_path = getattr(args, "file")
            convert_file(file_path)

    except NotImplementedError:
        raise NotImplementedError(f"Command {args.subcommand} does not exist")
    except Exception as e:
        raise Exception(f"Exception {e} executing subcommand {args.subcommand}")


if __name__ == '__main__':
    '''
    @brief Code execution guard.

    @details Allows code to run only when script is executed.
    '''

    args = parse_args()
    main(args)
