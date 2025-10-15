
'''
@file test_subprocess_utilities.py
@brief Defines the test subprocess_utilities class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import os
import shlex
import unittest
from subprocess import CalledProcessError
from unittest import TestCase
from unittest.mock import Mock, patch

# local module constants
from src import UTF8
from tests import TEST_M3U, TEST_MP3_CRUSH, TEST_WAV_NONE
from tests import TESTS_PATH
# local module errors
from src import FfmpegProcessError
# local module classes
from src.subprocess_utils import SubprocessUtilities

gc.enable()

## @var subprocess_utils
# @brief instance of SubprocessUtilities class
# @details used for accessing class functionality
subprocess_utils = SubprocessUtilities()


def mock_communicate_with_error() -> tuple:
    '''
    @brief Simulates a communicate() call that fails during decoding.
    '''

    # A byte string that is invalid UTF-8
    invalid_utf8_bytes = b'hello \x99\xae world'

    # communicate() returns (stdout, stderr) tuples.
    # To cause a decode error later, return undecoded bytes.
    return (invalid_utf8_bytes, b'')


class TestSubprocessUtilities(TestCase):
    '''
    @brief Tests SubprocessUtilities class functions.
    '''


    @classmethod
    def setUpClass(cls):
        '''
        @brief Initialize data for test suite.

        @details These datums are used throughout class and only need init once.
        '''

        cls.file_path = TEST_M3U

        # from metadata.get_media_info,
        # calls popen_pipe with ffprobe command for getting all media file info
        # append a valid file_path when using
        cls.ffprobe_command = [
            "ffprobe",
            "-v", "error",
            "-show_format",
            "-show_streams"
        ]

        # from metadata.convert_file,
        # calls popen_pipe with a ffmpeg command for an audio file conversion to mp3
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

        # from normalization.get_volume_info,
        # calls popen_pipe with an ffmpeg command for audio file getting volume info
        # -hide_banner to reduce output clutter
        # -i file_path
        # -filter:a volumedetect so get volume stats on audio stream
        # -f null - send output to stdout
        # to use, create an empty list, extend with ffmpeg_hide_banner, append with file_path, extend with ffmpeg_filter
        cls.ffmpeg_hide_banner = ['ffmpeg', '-hide_banner', '-i']
        cls.ffmpeg_filter = ['-filter:a', 'volumedetect', '-f', 'null', '-']


    def test_popen_pipe_ffmpeg_invalid_file(self):
        '''
        @brief Tests trying to get ffprobe media info from invalid file type throws RuntimeError.
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
        @brief Tests asynchronous execution of command with redirection to stderr throws FfmpegProcessError.
        '''

        mpeg_process = None

        with self.assertRaises(FfmpegProcessError) as cm:
            mpeg_process = subprocess_utils.spinner_popen_pipe(self.file_path, self.ffmpeg_command, show_spinner=False)

        self.assertIsNone(mpeg_process)
        self.assertEqual("FfmpegProcessError", cm.exception.__class__.__name__)
        err_msg = f"FfmpegProcessError running command {shlex.join(self.ffmpeg_command)}"
        self.assertTrue(cm.exception.args[0], err_msg)


    def test_popen_pipe_ffprobe_invalid_data(self):
        '''
        @brief Test trying to get ffprobe media info from invalid mp3 file throws RuntimeError.
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
        @brief Tests trying to get ffprobe media info from invalid file type throws RuntimeError.
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


    @patch('src.subprocess_utils.subprocess.Popen')
    def test_popen_pipe_communicate_decode_error(self, mock_popen):
        '''
        @brief Tests asynchronous Popen execution of command throws UnicodeDecodeError.
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
        @brief Tests getting ffmpeg volume info failing due to invalid file type throws CalledProcessError.
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
        @brief Tests Tries to run ffprobe video stream check for non-extant file throws CalledProcessError.

        @details This test is a due diligence expected failure test.
        SubprocessUtilities.subprocess_run is 4th level, called by AudioArt.has_video_stream function.
        AudioArt.has_video_stream has its own tests, which are not an appropriate location for subprocess_run testing.
        '''

        file_path = TEST_WAV_NONE

        # from art.has_video_stream,
        # calls subprocess_run with an ffprobe command to check if audio file has embedded art
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


    @patch('src.subprocess_utils.subprocess.run')
    def test_subprocess_run_unicode_decode_error(self, mock_subprocess_run):
        '''
        @brief Tests running subprocess for command throws UnicodeDecodeError.
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


def get_method_names(cls):
    '''
    @brief Returns a list of names of methods defined within a given class.

    @param cls {Class} The name of the class to get methods list from.
    @return method_names [{str}] The names of the methods defined in class.
    '''

    method_names = []
    for name, obj in inspect.getmembers(cls):
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            if name.startswith('test_'):
                method_names.append(name)
    return method_names


if __name__ == "__main__":
    methods = get_method_names(TestSubprocessUtilities)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestSubprocessUtilities(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
