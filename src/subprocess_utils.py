'''
@file subprocess_utils.py.py
@brief Defines the subprocess_utilities class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import logging
import os
import shlex
import subprocess
from subprocess import Popen, PIPE
from subprocess import CalledProcessError

# third party modules
from yaspin import yaspin
from yaspin.spinners import Spinners

# local modules
from src import ERROR_LOG_FORMAT, LOG_DIR, LOG_EXT, UTF8          # logging constants
from src.generated_files import GENERATED_FILES

gc.enable()

# Configure logging
basename = os.path.basename(__file__)
stem = os.path.splitext(basename)[0]
file = stem + LOG_EXT
log_filename = os.path.join(GENERATED_FILES, LOG_DIR, file)
# override the default logging level WARN to lowest level so we can log all levels
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=ERROR_LOG_FORMAT, filemode="a", encoding=UTF8)

# create logger for module and restrict to module
# use raise in exception handling if we need send something inter-module
logger = logging.getLogger(__name__)
logger.propagate = False


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

        @details Asynchronous execution of command with redirection to stdout.

        @param command {str} Command for Popen subprocess  to run.
        @return stdout {str} The decoded subprocess output.
        @exception RuntimeError A runtime error from subprocess popen.
        @exception UnicodeDecodeError A unicode decode error on subprocess stdout bytes.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            res = Popen(
                command,
                stdout=PIPE
            )

            # ffprobe returns via stdout (unlike ffmpeg, which uses stderr)
            stdout_bytes = res.communicate()[0]
            stdout = stdout_bytes.decode("utf-8")

            if res.returncode != 0:
                logger.error(f"RuntimeError running command {shlex.join(command)}", exc_info=True)
                raise RuntimeError(f"RuntimeError running command {shlex.join(command)}", exc_info=True)

        except RuntimeError as r_error:
            raise r_error
        except UnicodeDecodeError as ud_error:
            logger.exception(f"UnicodeDecodeError decoding {shlex.join(command)}: {stdout_bytes}", stack_info=True)
            raise ud_error
        except Exception as e_error:
            logger.exception(f"Exception running command {shlex.join(command)}", stack_info=True)
            raise e_error
        else:
            return stdout


    def spinner_subprocess_run(self, text, command):
        '''
        @brief Runs command in subprocess with a spinner.

        @details Runs subprocess for command, returns stdin & stderr.

        @param text {str} Text for spinner to display.
        @param command {str} Command for subprocess  to run.
        @return results (process, spinner) ({CompletedProcess}, {Yaspin}) Tuple containing completed process and spinner objects.
        @exception CalledProcessError A subprocess error from ffmpeg command execution.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            with yaspin(Spinners.dots, text=text, timer=True) as spinner:
                # check enables CalledProcessError throwing,
                # capture output to get stdout & stderr
                # text decodes stdout/stderr as text
                process = subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    text=True
                )

        except CalledProcessError as cp_error:
            logger.exception(f"CalledProcessError returncode:{cp_error.returncode}, with stderr: {cp_error.stderr} on command {cp_error.cmd}", stack_info=True)
            raise cp_error
        except Exception as e_error:
            logger.exception(f"Exception processing command: {command}", stack_info=True)
            raise e_error
        else:
            return process, spinner


    def subprocess_run(self, command):
        '''
        @brief Runs command in subprocess.

        @details Runs subprocess for command, returns stdin & stderr.

        @param text {str} Text for spinner to display.
        @param command {str} Command for subprocess  to run.
        @return process {CompletedProcess} Completed process object.
        @exception CalledProcessError A subprocess error from ffmpeg command execution.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            # check enables CalledProcessError throwing,
            # capture output to get stdout & stderr
            # text decodes stdout/stderr as text
            process = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )

        except CalledProcessError as cp_error:
            logger.error(f"CalledProcessError returncode:{cp_error.returncode}, with stderr: {cp_error.stderr} on command {cp_error.cmd}", exc_info=True)
            raise cp_error
        except Exception as e_error:
            logger.exception(f"Exception processing command: {command}", stack_info=True)
            raise e_error
        else:
            return process
