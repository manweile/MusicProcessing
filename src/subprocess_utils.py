'''
@file subprocess_utils.py
@brief Defines the subprocess utilities class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import logging
import os
import shlex
import subprocess
from pathlib import Path
from subprocess import PIPE
from subprocess import CalledProcessError

# third party modules
from yaspin import yaspin
from yaspin.spinners import Spinners
# local module methods
from src import add_module_handler
# local module constants
from src import UTF8
# local module errors
from src import FfmpegProcessError

gc.enable()

logger = logging.getLogger(__name__)
basename = os.path.basename(__file__)
add_module_handler(logger, basename)


class SubprocessUtilities():
    '''
    @brief Defines the base subprocess utilities processing used by project.
    '''

    def __init__(self):
        '''
        @brief Initialize the SubprocessUtilities class.

        @details A basic class implementation with no instantiation parameters.

        @return SubprocessUtilities {instance} An instance of the class.
        '''

        pass


    def popen_pipe(self, command):
        '''
        @brief Runs command in new process.

        @details Asynchronous execution of ffprobe command with redirection to stdout.

        @param command {str} Ffprobe command for Popen subprocess to run.
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
            logger.exception(f"UnicodeDecodeError decoding {shlex.join(command)}: stdout_bytes: {stdout_bytes} stderr_bytes: {stderr_bytes}", stack_info=True)
            raise ud_error
        except Exception as e_error:
            logger.exception(f"Exception running command {shlex.join(command)}", stack_info=True)
            raise e_error
        else:
            return stdout


    def spinner_popen_pipe(self, export_path, command, show_spinner=True):
        '''
        @brief Runs command in new process with option to display a spinner.

        @details Asynchronous execution of ffmpeg command with redirection to stderr.

        @param export_path {str} Path to destination audio file.
        @param command {str} Ffmpeg command for Popen subprocess to run.
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


    def spinner_subprocess_run(self, command, text):
        '''
        @brief Runs command in subprocess with a spinner.

        @details Runs subprocess for command, returns stdin & stderr.

        @param command {str} Command for subprocess  to run.
        @param text {str} Text for spinner to display.
        @return results (process, spinner) ({CompletedProcess}, {Yaspin}) Tuple containing completed process and spinner objects.

        @exception CalledProcessError A subprocess error from ffmpeg command execution.
        @exception UnicodeDecodeError A unicode decode error on subprocess stdout bytes.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            '''
            check enables CalledProcessError throwing,
            capture output to get stdout & stderr
            encoding for cross-platform compatibility & avoid decoding errors
            text decodes stdout/stderr as text
            '''
            with yaspin(Spinners.dots, text=text, timer=True) as spinner:
                process = subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    encoding=UTF8,
                    text=True
                )


        except CalledProcessError as cp_error:
            logger.exception(f"CalledProcessError returncode:{cp_error.returncode}, with stderr: {cp_error.stderr} on command {cp_error.cmd}", stack_info=True)
            raise cp_error
        except UnicodeDecodeError as ud_error:
            logger.exception(f"UnicodeDecodeError reason: {ud_error.reason} on object {ud_error.object} from command {shlex.join(command)}", stack_info=True)
            raise ud_error
        except Exception as e_error:
            logger.exception(f"Exception processing command: {command}", stack_info=True)
            raise e_error
        else:
            return process, spinner


    def subprocess_run(self, command):
        '''
        @brief Runs command in subprocess.

        @details Runs subprocess for command, returns stdin & stderr.

        @param command {str} Command for subprocess  to run.
        @return process {CompletedProcess} Completed process object.

        @exception CalledProcessError A subprocess error from ffmpeg command execution.
        @exception UnicodeDecodeError A unicode decode error on subprocess stdout bytes.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            '''
            check enables CalledProcessError throwing,
            capture output to get stdout & stderr
            encoding for cross-platform compatibility & avoid decoding errors
            text decodes stdout/stderr as text
            '''

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
            logger.exception(f"UnicodeDecodeError reason: {ud_error.reason} on object {ud_error.object} from command {shlex.join(command)}", stack_info=True)
            raise ud_error
        except Exception as e_error:
            logger.exception(f"Exception processing command: {command}", stack_info=True)
            raise e_error
        else:
            return process
