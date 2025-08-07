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
import subprocess
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

        except CalledProcessError as e:
            logger.exception(f"CalledProcessError returncode:{e.returncode}, with stderr: {e.stderr} on command {e.cmd}", stack_info=True)
            raise
        except Exception:
            logger.exception(f"Exception processing command: {command}", stack_info=True)
            raise
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

        except CalledProcessError as e:
            logger.exception(f"CalledProcessError returncode:{e.returncode}, with stderr: {e.stderr} on command {e.cmd}", stack_info=True)
            raise
        except Exception:
            logger.exception(f"Exception processing command: {command}", stack_info=True)
            raise
        else:
            return process
