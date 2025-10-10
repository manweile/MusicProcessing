
'''
@file test_subprocess_utilities.py
@brief Defines the test subprocess_utilities class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import logging
import unittest
from subprocess import CalledProcessError
from unittest import TestCase
from unittest.mock import Mock, patch

# local module constants
from tests import TEST_M3U, TEST_MP3_CRUSH, TEST_WAV_NONE
from src import UTF8
# local module errors
from src import FfmpegProcessError
# local module classes
from src.subprocess_utils import SubprocessUtilities

gc.enable()

# instantiate classes here
subprocess_utils = SubprocessUtilities()

'''
Get the effective level so we can disable logging when necessary.
In tests that use assertRaises, disable the logger at or below the log level of the tested function,
encapsulate the assertRaises in a try block, and use a finally to restore the original log level.
'''
original_log_level = logging.getLogger().getEffectiveLevel()


def mock_communicate_with_error():
    """Simulates a communicate() call that fails during decoding."""
    # A byte string that is invalid UTF-8
    invalid_utf8_bytes = b'hello \x99\xae world'

    # communicate() returns (stdout, stderr) tuples.
    # To cause a decode error later, return undecoded bytes.
    return (invalid_utf8_bytes, b'')


class TestSubprocessUtilities(TestCase):
    '''
    @brief Tests SubprocessUtilities class functions.
    '''


    def test_popen_pipe_ffmpeg_invalid_file(self):
        '''
        @brief Tests trying to get ffprobe media info from invalid file type throws RuntimeError.
        '''

        export_path = TEST_WAV_NONE
        file_path = TEST_M3U
        bitrate = 128198
        # from metadata.convert_file, command for an audio file conversion to mp3
        # ffmpeg
        # -hide_banner            # reduce output clutter
        # -i file_path            # specify input file D:\MusicProcessing\tests\Music\test.m3u
        # -vn -map_metadata -1    # -vn drops video stream and -map_metadata -1 drops all text metadata
        # -codec:a libmp3lame     # -codec:a libmp3lame sets audio codec for mp3
        # -id3v2_version 3        # known bug have to specify id3v2 version
        # -b:a 128198             # ffmpeg will downgrade bitrate if you don't set it
        mpeg_command = [
            "ffmpeg", "-hide_banner",
            "-i", file_path,
            "-vn", "-map_metadata", "-1",
            "-codec:a", "libmp3lame",
            "-id3v2_version", "3",
            "-b:a", str(bitrate),
            export_path, '-y'
        ]

        mpeg_process = None

        with self.assertRaises(RuntimeError) as cm:
            mpeg_process = subprocess_utils.popen_pipe(mpeg_command)

        self.assertIsNone(mpeg_process)
        self.assertEqual("RuntimeError", cm.exception.__class__.__name__)
        err_msg = f"RuntimeError running command ffmpeg -hide_banner -i {TEST_M3U} -vn -map_metadata -1 -codec:a libmp3lame -id3v2_version 3 -b:a 128198 {TEST_WAV_NONE} -y"
        self.assertTrue(cm.exception.args[0], err_msg)


    def test_popen_pipe_ffmpegprocess_error(self):
        '''
        @brief Tests asynchronous execution of command with redirection to stderr throws FfmpegProcessError.
        '''

        # @todo will need mocking of some type
        # metadata.convert_file calls spinner_popen_pipe with ffmpeg command
        export_path = TEST_WAV_NONE
        file_path = TEST_M3U
        bitrate = 128198
        # from metadata.convert_file, command for an audio file conversion to mp3
        # ffmpeg
        # -hide_banner            # reduce output clutter
        # -i file_path            # specify input file D:\MusicProcessing\tests\Music\test.m3u
        # -vn -map_metadata -1    # -vn drops video stream and -map_metadata -1 drops all text metadata
        # -codec:a libmp3lame     # -codec:a libmp3lame sets audio codec for mp3
        # -id3v2_version 3        # known bug have to specify id3v2 version
        # -b:a 128198             # ffmpeg will downgrade bitrate if you don't set it
        mpeg_command = [
            "ffmpeg", "-hide_banner",
            "-i", file_path,
            "-vn", "-map_metadata", "-1",
            "-codec:a", "libmp3lame",
            "-id3v2_version", "3",
            "-b:a", str(bitrate),
            export_path, '-y'
        ]

        mpeg_process = None

        with self.assertRaises(FfmpegProcessError) as cm:
            mpeg_process = subprocess_utils.spinner_popen_pipe(file_path, mpeg_command, show_spinner=False)

        self.assertIsNone(mpeg_process)
        self.assertEqual("FfmpegProcessError", cm.exception.__class__.__name__)
        err_msg = f"FfmpegProcessError running command ffmpeg -hide_banner -i {TEST_M3U} -vn -map_metadata -1 -codec:a libmp3lame -id3v2_version 3 -b:a 128198 {TEST_WAV_NONE} -y"
        self.assertTrue(cm.exception.args[0], err_msg)


    def test_popen_pipe_ffprobe_invalid_file(self):
        '''
        @brief Tests trying to get ffprobe media info from invalid file type throws RuntimeError.
        '''

        file_path = TEST_M3U

        # from metadata.get_media_info, command for getting all media file info
        # -v quiet reduce output clutter
        # -show_format get high level details of media file
        # -show_streams gets all information about each media stream in the input
        command = [
            "ffprobe",
            "-v", "quiet",
            "-show_format",
            "-show_streams",
            file_path
        ]

        std_out = None
        with self.assertRaises(RuntimeError) as cm:
            std_out = subprocess_utils.popen_pipe(command)

        self.assertIsNone(std_out)
        err_msg = f"RuntimeError running command ffprobe -v quiet -show_format -show_streams {TEST_M3U}"
        self.assertTrue(cm.exception.args[0], err_msg)


    @patch('src.subprocess_utils.subprocess.Popen')
    def test_popen_pipe_unicode_other(self, mock_popen):
        '''
        @brief Tests asynchronous execution of ffprobe command throws UnicodeDecodeError.
        '''

        # metadata.get_media_info calls popen_pipe with an ffprobe command
        # -v quiet reduce output clutter
        # -show_format get high level details of media file
        # -show_streams gets all information about each media stream in the input
        command = [
            "ffprobe",
            "-v", "quiet",
            "-show_format",
            "-show_streams",
            TEST_MP3_CRUSH
        ]

        mock_process_instance = Mock()
        mock_process_instance.communicate.side_effect = \
            lambda: mock_communicate_with_error()

        mock_popen.return_value = mock_process_instance

        std_out = subprocess_utils.popen_pipe(command)

        self.assertIsNone(std_out)
        self.assertEqual("UnicodeDecodeError", cm.exception.__class__.__name__)
        self.assertIn("Decoding error", std_out)
        self.assertIn("codec can't decode byte 0x99", std_out)

        # popen_pipe_subprocess_utils = SubprocessUtilities()

        # mock_popen_pipe = Mock(spec=popen_pipe_subprocess_utils)
        # mock_popen_pipe.side_effect = UnicodeDecodeError(UTF8, b'\xbe', 0, 1, 'invalid start byte')

        # popen_pipe_subprocess_utils.popen_pipe = mock_popen_pipe

        # std_out = None
        # with self.assertRaises(UnicodeDecodeError) as cm:
        #     std_out = popen_pipe_subprocess_utils.popen_pipe(command)

        # self.assertIsNone(std_out)
        # self.assertEqual("UnicodeDecodeError", cm.exception.__class__.__name__)

        # mock_popen_pipe.reset_mock(return_value=True, side_effect=True)


    def test_popen_pipe_unicode_error(self):
        '''
        @brief Tests asynchronous execution of ffprobe command throws UnicodeDecodeError.
        '''

        # metadata.get_media_info calls popen_pipe with an ffprobe command
        # -v quiet reduce output clutter
        # -show_format get high level details of media file
        # -show_streams gets all information about each media stream in the input
        command = [
            "ffprobe",
            "-v", "quiet",
            "-show_format",
            "-show_streams",
            TEST_MP3_CRUSH
        ]

        popen_pipe_subprocess_utils = SubprocessUtilities()

        mock_popen_pipe = Mock(spec=popen_pipe_subprocess_utils)
        mock_popen_pipe.side_effect = UnicodeDecodeError(UTF8, b'\xbe', 0, 1, 'invalid start byte')

        popen_pipe_subprocess_utils.popen_pipe = mock_popen_pipe

        std_out = None
        with self.assertRaises(UnicodeDecodeError) as cm:
            std_out = popen_pipe_subprocess_utils.popen_pipe(command)

        self.assertIsNone(std_out)
        self.assertEqual("UnicodeDecodeError", cm.exception.__class__.__name__)

        mock_popen_pipe.reset_mock(return_value=True, side_effect=True)


    def test_subprocess_run_ffmpeg_invalid_file(self):
        '''
        @brief Tests getting ffmpeg volume info failing due to invalid file type throws CalledProcessError.
        '''

        file_path = TEST_M3U
        # -hide_banner to reduce output clutter
        # -filter:a volumedetect so get volume stats on audio stream
        # -f null - send output to stdout
        mpeg_command = [
            'ffmpeg', '-hide_banner',
            '-i', file_path,
            '-filter:a', 'volumedetect',
            '-f', 'null', '-'
        ]
        mpeg_process = None

        with self.assertRaises(CalledProcessError) as cm:
            mpeg_process = subprocess_utils.subprocess_run(mpeg_command)

        self.assertIsNone(mpeg_process)
        self.assertEqual("CalledProcessError", cm.exception.__class__.__name__)
        err_msg = f"Error opening input file {TEST_M3U}"
        self.assertTrue(err_msg in cm.exception.stderr.strip())


    def test_subprocess_run_ffprobe_non_extant(self):
        '''
        @brief Tests Tries to run ffprobe video stream check for non-extant file throws CalledProcessError.

        @details This test is a due diligence expected failure test.
        SubprocessUtilities.subprocess_run is 4th level, called by AudioArt.has_video_stream function.
        AudioArt.has_video_stream has its own tests, which are not an appropriate location for subprocess_run testing.
        '''

        input_audio = TEST_WAV_NONE

        # -hide_banner reduce output clutter
        # -select_streams v:0 only want video stream
        # -show_streams gets all information about each media stream in the input
        # -of json output information in json format
        probe_command = [
            'ffprobe',
            '-hide_banner',
            '-select_streams', 'v:0',
            '-show_streams',
            '-of', 'json',
            input_audio
        ]
        probe_process = None

        with self.assertRaises(CalledProcessError) as cm:
            probe_process = subprocess_utils.subprocess_run(probe_command)

        self.assertIsNone(probe_process)
        stderr = cm.exception.stderr.strip()
        expected_err = f"{input_audio}: No such file or directory"
        self.assertEqual(stderr, expected_err)


    @unittest.skip("complete")
    def test_subprocess_run_unicode_error(self):
        '''
        @brief Tests running subprocess for command throws UnicodeDecodeError.
        '''

        # @todo will need mocking of some type
        # art.has_video_stream calls subprocess_run with ffprobe command
        # metadata.get_media_tags calls subprocess_run with ffprobe command
        # normalization.ebu_normalize_files calls subprocess_run with ffmpeg command
        # normalization.get_bit_rate calls subprocess_run with ffprobe command
        # normalization.get_sample_rate calls subprocess_run with ffprobe command
        # normalization.ebu_get_volume_info calls subprocess_run with ffmpeg command
        # normalization.peak_normalize_files calls subprocess_run with ffmpeg command
        # normalization.rms_normalize_files calls subprocess_run with ffmpeg command
        pass


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
