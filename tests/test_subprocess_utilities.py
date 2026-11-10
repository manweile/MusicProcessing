'''
@class TestSubprocessUtilities
@file test_subprocess_utilities.py
@author Gerald Manweiler

@brief Defines the test subprocess utilities class.

@details Tests subprocess command execution, error propagation, and decoding behavior.

@version 1.0.0
@date 2026-09-22

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import os                                                   # for test fixture path construction
import shlex                                                # for expected command formatting
import unittest                                             # for direct test-suite execution
from subprocess import CalledProcessError                   # for expected command execution errors
from unittest import TestCase                               # for test-case assertions and lifecycle hooks
from unittest.mock import Mock                              # for subprocess process doubles
from unittest.mock import patch                             # for patched subprocess functions

# Local Module Methods
from tests.support import get_method_names                  # for direct test-suite construction

# Local Module Constants
from src.core.constants import UTF8                         # for UTF-8 text encoding
from tests import TEST_M3U                                  # for invalid file-type tests
from tests import TEST_MP3_CRUSH                            # for valid media command tests
from tests import TEST_WAV_NONE                             # for non-existent file tests
from tests import TESTS_PATH                                # for invalid media fixture paths

# Local Module Errors
from src.core.errors import FfmpegProcessError              # for expected ffmpeg command failures

# Local Module Classes
from src.core.subprocess_utils import SubprocessUtilities   # for subprocess functionality under test
from tests.support import FakeProgress                      # recording progress reporter

## @var subprocess_utils
# @brief SubprocessUtilities instance under test.
# @details Provides access to subprocess execution functionality.
subprocess_utils = SubprocessUtilities()


def mock_communicate_with_error() -> tuple:
    '''
    @brief Simulate a communicate call that fails during decoding.

    @details Returns undecodable bytes that trigger a Unicode decode error.

    @retval undecoded_bytes {tuple{bytes, bytes}} Simulated communicate output with undecodable bytes.
    '''

    # A byte string that is invalid UTF-8
    invalid_utf8_bytes = b'hello \x99\xae world'

    # communicate() returns (stdout, stderr) tuple, to cause a decode error later, return undecoded bytes
    undecoded_bytes = (invalid_utf8_bytes, b'')

    return undecoded_bytes


class TestSubprocessUtilities(TestCase):
    '''
    @brief Tests SubprocessUtilities class functions.

    @details Verifies command execution, subprocess errors, and decoding behavior.
    '''


    @classmethod
    def setUpClass(cls):
        '''
        @brief Initialize data for test suite.

        @details Creates shared ffprobe and ffmpeg command fixtures for the test suite.

        @code{.text}
        get all media info command
        ffprobe -v error -show_format -show_streams file_path

        -v quiet; reduce output clutter
        -show_format; get high level details of media file
        -show_streams; gets all information about each media stream in the input
        file_path; the path to the audio file to be analyzed by ffprobe

        convert audio files to mp3 command
        ffmpeg -hide_banner -i file_path -vn -map_metadata -1 -codec:a libmp3lame -id3v2_version 3 -b:a 128198

        -hide_banner; reduce output clutter
        -i file_path; the path to the audio file
        -vn -map_metadata -1; -vn drops video stream and -map_metadata -1 drops all text metadata
        -codec:a libmp3lame; sets audio codec for mp3
        -id3v2_version 3; known bug, MUST specify id3v2 version, else will get ID3v2.4
        -b:a 128198; ffmpeg will downgrade bitrate if you don't set it
        file_path: the path to the audio file

        get volume information command
        ffmpeg -hide_banner -i file_path -filter:a volumedetect -f null -

        -hide_banner; to reduce output clutter
        -i file_path; specifies the input audio file
        -filter:a volumedetect; applies the volumedetect filter to the audio stream
        -f null -; sends the output to null to avoid creating an actual output file
        @endcode

        @param cls {TestSubprocessUtilities} Test class receiving shared command fixtures.
        '''

        cls.file_path = TEST_M3U

        # ffprobe command for getting all media file info, append a valid file_path when using
        cls.ffprobe_command = [
            "ffprobe",
            "-v", "error",
            "-show_format",
            "-show_streams"
        ]

        # ffmpeg command for an audio file conversion to mp3
        cls.ffmpeg_command = [
            "ffmpeg",
            "-hide_banner",
            "-i", cls.file_path,
            "-vn", "-map_metadata", "-1",
            "-codec:a", "libmp3lame",
            "-id3v2_version", "3",
            "-b:a", str(128198),
            TEST_WAV_NONE, '-y'
        ]

        # ffmpeg command for audio file getting volume info
        # to use, create an empty list, extend with ffmpeg_hide_banner, append with file_path, extend with ffmpeg_filter
        cls.ffmpeg_hide_banner = ['ffmpeg', '-hide_banner', '-i']
        cls.ffmpeg_filter = ['-filter:a', 'volumedetect', '-f', 'null', '-']


    def test_popen_pipe_ffmpeg_invalid_file(self):
        '''
        @brief Test ffmpeg pipe execution with an invalid file type.

        @details Verifies an invalid input file raises a runtime error.

        @test Error case.

        @param self {TestSubprocessUtilities} The instance of the test class.
        '''

        mpeg_process = None

        with self.assertRaises(RuntimeError) as cm:
            mpeg_process = subprocess_utils.popen_pipe(self.ffmpeg_command)

        self.assertIsNone(mpeg_process)
        self.assertEqual("RuntimeError", cm.exception.__class__.__name__)
        err_msg = f"RuntimeError running command {shlex.join(self.ffmpeg_command)}"
        self.assertTrue(cm.exception.args[0], err_msg)


    def test_popen_pipe_ffmpegprocess_error(self):
        '''
        @brief Test spinner pipe execution with an ffmpeg process error.

        @details Verifies failed asynchronous ffmpeg execution raises an ffmpeg process error.

        @test Error case.

        @param self {TestSubprocessUtilities} The instance of the test class.
        '''

        mpeg_process = None

        with self.assertRaises(FfmpegProcessError) as cm:
            mpeg_process = subprocess_utils.spinner_popen_pipe(self.file_path, self.ffmpeg_command)

        self.assertIsNone(mpeg_process)
        self.assertEqual("FfmpegProcessError", cm.exception.__class__.__name__)
        err_msg = f"FfmpegProcessError running command {shlex.join(self.ffmpeg_command)}"
        self.assertTrue(cm.exception.args[0], err_msg)


    def test_spinner_subprocess_run_reports_elapsed_time(self):
        '''
        @brief Tests subprocess progress reporting and elapsed time.

        @details Verifies the progress lifecycle and elapsed value are returned with the process.

        @param self {TestSubprocessUtilities} The instance of the test class.
        '''

        process = Mock()
        progress = FakeProgress(1.25)

        # Patch subprocess.run to return a mocked process and test spinner_subprocess_run with FakeProgress.
        with patch("src.core.subprocess_utils.subprocess.run", return_value=process):
            actual_process, elapsed = subprocess_utils.spinner_subprocess_run(
                self.ffmpeg_command,
                "Running test command",
                progress,
            )

        self.assertIs(process, actual_process)
        self.assertEqual(1.25, elapsed)
        self.assertEqual([(None, "Running test command")], progress.starts)
        self.assertEqual(1, progress.finish_calls)


    def test_popen_pipe_ffprobe_invalid_data(self):
        '''
        @brief Test ffprobe pipe execution with invalid MP3 data.

        @details Verifies malformed audio data raises a runtime error.

        @test Error case.

        @param self {TestSubprocessUtilities} The instance of the test class.
        '''

        file_path = os.path.join(TESTS_PATH, "No_audio_Crush-Live.mp3")

        command = self.ffprobe_command
        command.append(file_path)

        std_out = None

        with self.assertRaises(RuntimeError) as cm:
            std_out = subprocess_utils.popen_pipe(command)

        self.assertIsNone(std_out)
        self.assertTrue(cm.exception.args[0], f"{file_path}: Invalid data found when processing input")


    def test_popen_pipe_ffprobe_invalid_file(self):
        '''
        @brief Test ffprobe pipe execution with an invalid file type.

        @details Verifies a playlist input raises a runtime error.

        @test Error case.

        @param self {TestSubprocessUtilities} The instance of the test class.
        '''

        file_path = TEST_M3U

        command = self.ffprobe_command
        command.append(file_path)

        std_out = None
        with self.assertRaises(RuntimeError) as cm:
            std_out = subprocess_utils.popen_pipe(command)

        self.assertIsNone(std_out)
        err_msg = f"RuntimeError running command {shlex.join(command)}"
        self.assertTrue(cm.exception.args[0], err_msg)


    @patch('src.core.subprocess_utils.subprocess.Popen')
    def test_popen_pipe_communicate_decode_error(self, mock_popen):
        '''
        @brief Test pipe execution with undecodable communicate output.

        @details Verifies undecodable mocked output raises a Unicode decode error.<br>
        Patching the subprocess_utils.subprocess.Popen constructor to simulate undecodable output.

        @test Error case.

        @param self {TestSubprocessUtilities} The instance of the test class.
        @param mock_popen {Mock} Patched Popen constructor returning undecodable output.
        '''

        file_path = TEST_MP3_CRUSH

        command = self.ffprobe_command
        command.append(file_path)

        mock_process_instance = Mock()
        mock_process_instance.communicate.side_effect = lambda: mock_communicate_with_error()

        mock_popen.return_value = mock_process_instance

        std_out = None
        with self.assertRaises(UnicodeDecodeError) as cm:
            std_out = subprocess_utils.popen_pipe(command)

        self.assertIsNone(std_out)
        self.assertEqual("UnicodeDecodeError", cm.exception.__class__.__name__)
        self.assertEqual("invalid start byte", cm.exception.reason)

        mock_popen.reset_mock(return_value=True, side_effect=True)
        mock_process_instance.reset_mock(return_value=True, side_effect=True)


    def test_subprocess_run_ffmpeg_invalid_file(self):
        '''
        @brief Test ffmpeg volume analysis with an invalid file type.

        @details Verifies ffmpeg raises a called process error for a playlist input.

        @test Error case.

        @param self {TestSubprocessUtilities} The instance of the test class.
        '''

        file_path = TEST_M3U

        mpeg_command = []
        mpeg_command.extend(self.ffmpeg_hide_banner)
        mpeg_command.append(file_path)
        mpeg_command.extend(self.ffmpeg_filter)

        mpeg_process = None

        with self.assertRaises(CalledProcessError) as cm:
            mpeg_process = subprocess_utils.subprocess_run(mpeg_command)

        self.assertIsNone(mpeg_process)
        self.assertEqual("CalledProcessError", cm.exception.__class__.__name__)
        err_msg = f"Error opening input file {file_path}"
        self.assertTrue(err_msg in cm.exception.stderr.strip())


    def test_subprocess_run_ffprobe_non_extant(self):
        '''
        @brief Test ffprobe video-stream inspection with a missing file.

        @details Verifies ffprobe raises a called process error for a non-existent input file.

        @code{.text}
        check for stream command
        ffprobe -hide_banner -select_streams v:0 -show_streams -of json file_path

        -hide_banner: reduce output clutter
        -select_streams v:0: only want video stream
        -show_streams: gets all information about each media stream in the input
        -of json: output information in json format
        file_path: the path to the media file to be analyzed by ffprobe
        @endcode

        @test Error case.

        @param self {TestSubprocessUtilities} The instance of the test class.
        '''

        file_path = TEST_WAV_NONE

        # ffprobe command to check if audio file has embedded art
        probe_command = [
            'ffprobe',
            '-hide_banner',
            '-select_streams', 'v:0',
            '-show_streams',
            '-of', 'json',
            file_path
        ]
        probe_process = None

        with self.assertRaises(CalledProcessError) as cm:
            probe_process = subprocess_utils.subprocess_run(probe_command)

        self.assertIsNone(probe_process)
        stderr = cm.exception.stderr.strip()
        expected_err = f"{file_path}: No such file or directory"
        self.assertEqual(stderr, expected_err)


    @patch('src.core.subprocess_utils.subprocess.run')
    def test_subprocess_run_unicode_decode_error(self, mock_subprocess_run):
        '''
        @brief Test subprocess execution with undecodable output.

        @details Verifies an undecodable mocked subprocess result raises a Unicode decode error.<br>
        Patching the subprocess_utils.subprocess.run constructor to simulate undecodable output.

        @test Error case.

        @param self {TestSubprocessUtilities} The instance of the test class.
        @param mock_subprocess_run {Mock} Patched subprocess runner raising a decoding error.
        '''

        file_path = TEST_MP3_CRUSH

        mpeg_command = []
        mpeg_command.extend(self.ffmpeg_hide_banner)
        mpeg_command.append(file_path)
        mpeg_command.extend(self.ffmpeg_filter)

        mock_subprocess_run.side_effect = UnicodeDecodeError(UTF8, b'\xff', 0, 1, 'invalid start byte')

        process = None

        with self.assertRaises(UnicodeDecodeError) as cm:
            process = subprocess_utils.subprocess_run(mpeg_command)

        self.assertIsNone(process)
        self.assertEqual("UnicodeDecodeError", cm.exception.__class__.__name__)
        self.assertEqual("invalid start byte", cm.exception.reason)

        mock_subprocess_run.reset_mock(return_value=True, side_effect=True)


if __name__ == "__main__":
    '''
    @brief Run the SubprocessUtilities test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.

    @note This test module can be run directly with `python tests/test_subprocess_utilities.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestSubprocessUtilities)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestSubprocessUtilities(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
