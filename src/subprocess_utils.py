'''
@class SubprocessUtilities
@file src/subprocess_utils.py
@author Gerald Manweiler

@brief Defines the subprocess utilities class.

@details Defines utility methods for running and monitoring subprocess commands in the MusicProcessing project.

@version 1.0.0
@date 2024-06-06

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import gc                                                   # for garbage collection management
import logging                                              # for module logging
import os                                                   # for operating-system interfaces
import shlex                                                # for command formatting
import subprocess                                           # for process execution
from pathlib import Path                                    # for object-oriented filesystem paths
from subprocess import CalledProcessError                   # for subprocess execution errors
from subprocess import CompletedProcess                     # for completed process results
from subprocess import PIPE                                 # for subprocess stream pipes

# Third Party Modules
from yaspin import yaspin                                   # for command progress indicators
from yaspin.spinners import Spinners                        # for spinner definitions

# Local Module Methods
from src import add_module_handler                          # for module-specific logging handlers

# Local Module Constants
from src import UTF8                                        # for UTF-8 text encoding

# Local Module Errors
from src import FfmpegProcessError                          # for FFmpeg process failures

gc.enable()

## @var logger
# @brief Logger instance for the module.
# @details Sets the logger name to the current module name.
logger = logging.getLogger(__name__)

## @var basename
# @brief Base name for the logger file handler.
# @details Gets the module file name from the current file path.
basename = os.path.basename(__file__)

add_module_handler(logger, basename)


class SubprocessUtilities():
    '''
    @brief Defines the base subprocess utilities processing used by project.

    @details This class provides utility methods for running subprocess commands, including handling output and errors.
    '''

    def __init__(self) -> None:
        '''
        @brief Initializes the SubprocessUtilities class.

        @details Initializes a SubprocessUtilities instance without instance-specific state.
        '''

        pass


    def popen_pipe(self, command: list[str]) -> str:
        '''
        @brief Runs command in new process.

        @details Runs an ffprobe command asynchronously and redirects output to standard output.

        @param command {list[str]} FFprobe command for Popen to run.
        @return stdout {str} The decoded subprocess output.

        @exception RuntimeError A runtime error from subprocess popen.
        @exception UnicodeDecodeError A unicode decode error on subprocess stdout bytes.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            res = subprocess.Popen(
                command,
                stdout=PIPE,
                stderr=PIPE
            )

            # ffprobe returns via stdout (unlike ffmpeg, which uses stderr)
            stdout_bytes, stderr_bytes = res.communicate()
            stdout = stdout_bytes.decode(UTF8)
            std_err = stderr_bytes.decode(UTF8)

            if res.returncode != 0:
                logger.error(f"RuntimeError running command {shlex.join(command)} with stderr: {std_err}", exc_info=True)
                raise RuntimeError(f"RuntimeError running command {shlex.join(command)} with stderr: {std_err}")

        except RuntimeError as r_error:
            raise r_error
        except UnicodeDecodeError as ud_error:
            logger.exception(
                f"UnicodeDecodeError decoding {shlex.join(command)}: stdout_bytes: {stdout_bytes} stderr_bytes: {stderr_bytes}",
                stack_info=True,
            )
            raise ud_error
        except Exception as e_error:
            logger.exception(f"Exception running command {shlex.join(command)}", stack_info=True)
            raise e_error
        else:
            return stdout


    def spinner_popen_pipe(self, export_path: str, command: list[str], show_spinner: bool = True) -> str:
        '''
        @brief Runs command in new process with option to display a spinner.

        @details Runs an FFmpeg command asynchronously and redirects output to standard error.

        @param export_path {str} Path to destination audio file.
        @param command {list[str]} FFmpeg command for Popen to run.
        @param show_spinner {bool} Flag to use spinner or not. Default True.
        @return success_msg {str} Success message on completion.

        @exception FfmpegProcessError Exception occurred processing a ffmpeg command.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            input_path = Path(export_path)
            input_file_name = input_path.stem
            text = f"Converting {input_file_name}"

            if show_spinner:
                with yaspin(Spinners.dots, text=text, timer=True) as sp:
                    with open(os.devnull, 'rb') as devnull:
                        p = subprocess.Popen(
                            command,
                            stdin=devnull,
                            stdout=PIPE,
                            stderr=PIPE,
                            universal_newlines=True
                        )

                    while True:
                        line = p.stderr.readline()
                        if not line:
                            break

                    p_out, p_err = p.communicate()
            else:
                with open(os.devnull, 'rb') as devnull:
                    p = subprocess.Popen(
                        command,
                        stdin=devnull,
                        stdout=PIPE,
                        stderr=PIPE,
                    )

                # ffmpeg returns via stderr (unlike ffprobe, which uses stdout)
                p_out, p_err = p.communicate()
                # using 'ignore' because I don't want a UnicodeDecodeError to happen
                std_err = p_err.decode(errors='ignore')

            if p.returncode != 0:
                fp_error_msg = f"Ffmpeg returned error code: {p.returncode}\n, with output: {std_err}\n for command:{command}\n"
                logger.exception(fp_error_msg, stack_info=True)
                raise FfmpegProcessError(fp_error_msg)

        except FfmpegProcessError as fp_error:
            raise fp_error
        except Exception as e_error:
            logger.exception(f"Exception running command {shlex.join(command)}", stack_info=True)
            raise e_error
        else:
            success_msg = None
            if show_spinner:
                success_msg = f"Successful conversion on {input_path.stem} from {input_path.suffix.removeprefix(".")} in {sp.elapsed_time:.2f} secs"
            else:
                success_msg = f"Successful conversion on {input_path.stem} from {input_path.suffix.removeprefix(".")}"

            return success_msg


    def spinner_subprocess_run(self, command: list[str], text: str) -> tuple:
        '''
        @brief Runs command in subprocess with a spinner.

        @details Runs a subprocess command and returns the completed process with its spinner.

        @param command {list[str]} Command for subprocess to run.
        @param text {str} Text for spinner to display.
        @return results (process, spinner) ({CompletedProcess}, {Yaspin}) Tuple containing completed process and spinner objects.

        @exception CalledProcessError A subprocess error from ffmpeg command execution.
        @exception UnicodeDecodeError A unicode decode error on subprocess stdout bytes.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            # Check raises CalledProcessError; capture_output and text collect decoded standard streams
            with yaspin(Spinners.dots, text=text, timer=True) as spinner:
                process = subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    encoding=UTF8,
                    text=True
                )


        except CalledProcessError as cp_error:
            logger.exception(
                f"CalledProcessError returncode:{cp_error.returncode}, with stderr: {cp_error.stderr} on command {cp_error.cmd}",
                stack_info=True,
            )
            raise cp_error
        except UnicodeDecodeError as ud_error:
            logger.exception(
                f"UnicodeDecodeError reason: {ud_error.reason} on object {ud_error.object} from command {shlex.join(command)}",
                stack_info=True,
            )
            raise ud_error
        except Exception as e_error:
            logger.exception(f"Exception processing command: {command}", stack_info=True)
            raise e_error
        else:
            results = (process, spinner)
            return results


    def subprocess_run(self, command: list[str]) -> CompletedProcess:
        '''
        @brief Runs command in subprocess.

        @details Runs a subprocess command and returns its completed process.

        @param command {list[str]} Command for subprocess to run.
        @return process {CompletedProcess} Completed process object.

        @exception CalledProcessError A subprocess error from ffmpeg command execution.
        @exception UnicodeDecodeError A unicode decode error on subprocess stdout bytes.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            # Check raises CalledProcessError; capture_output and text collect decoded standard streams

            process = subprocess.run(
                command,
                check=True,
                capture_output=True,
                encoding=UTF8,
                text=True
            )

        except CalledProcessError as cp_error:
            logger.exception(f"CalledProcessError returncode: {cp_error.returncode} on command {cp_error.cmd}", stack_info=True)
            raise cp_error
        except UnicodeDecodeError as ud_error:
            logger.exception(
                f"UnicodeDecodeError reason: {ud_error.reason} on object {ud_error.object} from command {shlex.join(command)}",
                stack_info=True,
            )
            raise ud_error
        except Exception as e_error:
            logger.exception(f"Exception processing command: {command}", stack_info=True)
            raise e_error
        else:
            return process
