
'''
@file test_audio_metadata.py
@brief Defines the test audio metadata class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import logging
import os
import platform
import unittest

# third party modules
from mutagen._util import MutagenError

# local modules
from src import EXPORT_TLD
from src import MusicProcessingError
from src.audio_info import AudioMetadata

gc.enable()

# instantiate module levels vars here
TESTS_TLD = os.path.dirname(os.path.abspath(__file__))
MP3_FILE = os.path.join("Crush", "Here", "Crush-Live.mp3")
MP3_PATH = os.path.join(TESTS_TLD, EXPORT_TLD, MP3_FILE)

'''
ffprobe command line that is source for media info dictionary definition
ffprobe -v quiet -show_format -show_streams <file_path>
'''

# linux ffprobe dict
LINUX_RESULT = {
    'index': '1', 'codec_name': 'mjpeg', 'codec_long_name': 'Motion JPEG', 'profile': 'Baseline', 'codec_type': 'video', 'codec_tag_string': '[0][0][0][0]',
    'codec_tag': '0x0000', 'sample_fmt': 'fltp', 'sample_rate': '44100', 'channels': '2', 'channel_layout': 'stereo', 'bits_per_sample': '0', 'initial_padding': '0',
    'id': 'N/A', 'r_frame_rate': '90000/1', 'avg_frame_rate': '0/0', 'time_base': '1/90000', 'start_pts': 'N/A', 'start_time': '0.000000', 'duration_ts': '22131951',
    'duration': '245.910567', 'bit_rate': '129156', 'max_bit_rate': 'N/A', 'bits_per_raw_sample': '8', 'nb_frames': 'N/A', 'nb_read_frames': 'N/A', 'nb_read_packets': 'N/A',
    'DISPOSITION': {
        'default': '0', 'dub': '0', 'original': '0', 'comment': '0', 'lyrics': '0', 'karaoke': '0', 'forced': '0', 'hearing_impaired': '0', 'visual_impaired': '0',
        'clean_effects': '0', 'attached_pic': '1', 'timed_thumbnails': '0', 'non_diegetic': '0', 'captions': '0', 'descriptions': '0', 'metadata': '0', 'dependent': '0',
        'still_image': '0'},
    'width': '500', 'height': '490', 'coded_width': '500', 'coded_height': '490', 'closed_captions': '0', 'film_grain': '0', 'has_b_frames': '0', 'sample_aspect_ratio': '1:1', 'display_aspect_ratio': '50:49',
    'pix_fmt': 'yuvj420p', 'level': '-99', 'color_range': 'pc', 'color_space': 'bt470bg', 'color_transfer': 'unknown', 'color_primaries': 'unknown',
    'chroma_location': 'center', 'field_order': 'unknown', 'refs': '1',
    'TAG': {
        'comment': 'Cover (front)', 'title': 'Live', 'artist': 'Crush', 'track': '1/12', 'album': 'Here', 'disc': '1/1', 'genre': 'Pop', 'TMED': 'CD', 'TORY': '2002',
        'MusicBrainz Release Track Id': '2475137d-6745-3951-a361-d4c29798f5d1', 'album_artist': 'Crush', 'TSO2': 'Crush', 'artist-sort': 'Crush', 'composer': 'Paul Lamb',
        'SCRIPT': 'Latn', 'publisher': 'Sonic Records', 'ARTISTS': 'Crush', 'ASIN': 'B000065PP6', 'originalyear': '2002', 'BARCODE': '627915092229',
        'CATALOGNUMBER': '2 50922', 'MusicBrainz Album Type': 'album', 'MusicBrainz Album Status': 'official', 'MusicBrainz Album Release Country': 'CA',
        'Acoustid Id': '4fdf7757-ba58-4a4b-a1df-1ad4d102a474', 'MusicBrainz Album Id': '18f635aa-dc20-4fbf-a3f3-d63de3bd0fb6',
        'MusicBrainz Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f', 'MusicBrainz Album Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f',
        'MusicBrainz Release Group Id': 'a7927f70-2431-3a58-b7ae-48576808cec1', 'date': '2002'},
    'filename': '/home/gerald/MusicProcessing/tests/Music/Crush/Here/Crush-Live.mp3', 'nb_streams': '2', 'nb_programs': '0', 'format_name': 'mp3',
    'format_long_name': 'MP2/3 (MPEG audio layer 2/3)', 'size': '3970122', 'probe_score': '51'
}

# windows ffprobe dict
WIN_RESULT = {
    'index': '1', 'codec_name': 'mjpeg', 'codec_long_name': 'Motion JPEG', 'profile': 'Baseline', 'codec_type': 'video', 'codec_tag_string': '[0][0][0][0]',
    'codec_tag': '0x0000', 'sample_fmt': 'fltp', 'sample_rate': '44100', 'channels': '2', 'channel_layout': 'stereo', 'bits_per_sample': '0', 'initial_padding': '0',
    'id': 'N/A', 'r_frame_rate': '90000/1', 'avg_frame_rate': '0/0', 'time_base': '1/90000', 'start_pts': 'N/A', 'start_time': '0.000000', 'duration_ts': '22131951',
    'duration': '245.910567', 'bit_rate': '129156', 'max_bit_rate': 'N/A', 'bits_per_raw_sample': '8', 'nb_frames': 'N/A', 'nb_read_frames': 'N/A', 'nb_read_packets': 'N/A',
    'DISPOSITION': {
        'default': '0', 'dub': '0', 'original': '0', 'comment': '0', 'lyrics': '0', 'karaoke': '0', 'forced': '0', 'hearing_impaired': '0', 'visual_impaired': '0',
        'clean_effects': '0', 'attached_pic': '1', 'timed_thumbnails': '0', 'non_diegetic': '0', 'captions': '0', 'descriptions': '0', 'metadata': '0', 'dependent': '0',
        'still_image': '0', 'multilayer': '0'},
    'width': '500', 'height': '490', 'coded_width': '500', 'coded_height': '490', 'has_b_frames': '0', 'sample_aspect_ratio': '1:1', 'display_aspect_ratio': '50:49',
    'pix_fmt': 'yuvj420p', 'level': '-99', 'color_range': 'pc', 'color_space': 'bt470bg', 'color_transfer': 'unknown', 'color_primaries': 'unknown',
    'chroma_location': 'center', 'field_order': 'unknown', 'refs': '1',
    'TAG': {
        'comment': 'Cover (front)', 'title': 'Live', 'artist': 'Crush', 'track': '1/12', 'album': 'Here', 'disc': '1/1', 'genre': 'Pop', 'TMED': 'CD', 'TORY': '2002',
        'MusicBrainz Release Track Id': '2475137d-6745-3951-a361-d4c29798f5d1', 'album_artist': 'Crush', 'TSO2': 'Crush', 'artist-sort': 'Crush', 'composer': 'Paul Lamb',
        'SCRIPT': 'Latn', 'publisher': 'Sonic Records', 'ARTISTS': 'Crush', 'ASIN': 'B000065PP6', 'originalyear': '2002', 'BARCODE': '627915092229',
        'CATALOGNUMBER': '2 50922', 'MusicBrainz Album Type': 'album', 'MusicBrainz Album Status': 'official','MusicBrainz Album Release Country': 'CA',
        'Acoustid Id': '4fdf7757-ba58-4a4b-a1df-1ad4d102a474', 'MusicBrainz Album Id': '18f635aa-dc20-4fbf-a3f3-d63de3bd0fb6',
        'MusicBrainz Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f', 'MusicBrainz Album Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f',
        'MusicBrainz Release Group Id': 'a7927f70-2431-3a58-b7ae-48576808cec1', 'date': '2002'},
    'filename': 'D:\\MusicProcessing\\tests\\Music\\Crush\\Here\\Crush-Live.mp3', 'nb_streams': '2', 'nb_programs': '0', 'nb_stream_groups': '0', 'format_name': 'mp3',
    'format_long_name': 'MP2/3 (MPEG audio layer 2/3)', 'size': '3970122', 'probe_score': '51'
}

CI_RESULT = {
    'index': '1', 'codec_name': 'mjpeg', 'codec_long_name': 'Motion JPEG', 'profile': 'Baseline', 'codec_type': 'video', 'codec_tag_string': '[0][0][0][0]',
    'codec_tag': '0x0000', 'sample_fmt': 'fltp', 'sample_rate': '44100', 'channels': '2', 'channel_layout': 'stereo', 'bits_per_sample': '0', 'initial_padding': '0',
    'id': 'N/A', 'r_frame_rate': '90000/1', 'avg_frame_rate': '0/0', 'time_base': '1/90000', 'start_pts': 'N/A', 'start_time': '0.000000', 'duration_ts': '22131951',
    'duration': '245.910567', 'bit_rate': '129156', 'max_bit_rate': 'N/A', 'bits_per_raw_sample': '8', 'nb_frames': 'N/A', 'nb_read_frames': 'N/A', 'nb_read_packets': 'N/A',
    'DISPOSITION': {
        'default': '0', 'dub': '0', 'original': '0', 'comment': '0', 'lyrics': '0', 'karaoke': '0', 'forced': '0', 'hearing_impaired': '0', 'visual_impaired': '0',
        'clean_effects': '0', 'attached_pic': '1', 'timed_thumbnails': '0', 'non_diegetic': '0', 'captions': '0', 'descriptions': '0', 'metadata': '0', 'dependent': '0',
        'still_image': '0', 'multilayer': '0'},
    'width': '500', 'height': '490', 'coded_width': '500', 'coded_height': '490', 'closed_captions': '0', 'film_grain': '0', 'has_b_frames': '0', 'sample_aspect_ratio': '1:1', 'display_aspect_ratio': '50:49',
    'pix_fmt': 'yuvj420p', 'level': '-99', 'color_range': 'pc', 'color_space': 'bt470bg', 'color_transfer': 'unknown', 'color_primaries': 'unknown',
    'chroma_location': 'center', 'field_order': 'unknown', 'refs': '1',
    'TAG': {
        'comment': 'Cover (front)', 'title': 'Live', 'artist': 'Crush', 'track': '1/12', 'album': 'Here', 'disc': '1/1', 'genre': 'Pop', 'TMED': 'CD', 'TORY': '2002',
        'MusicBrainz Release Track Id': '2475137d-6745-3951-a361-d4c29798f5d1', 'album_artist': 'Crush', 'TSO2': 'Crush', 'artist-sort': 'Crush', 'composer': 'Paul Lamb',
        'SCRIPT': 'Latn', 'publisher': 'Sonic Records', 'ARTISTS': 'Crush', 'ASIN': 'B000065PP6', 'originalyear': '2002', 'BARCODE': '627915092229',
        'CATALOGNUMBER': '2 50922', 'MusicBrainz Album Type': 'album', 'MusicBrainz Album Status': 'official', 'MusicBrainz Album Release Country': 'CA',
        'Acoustid Id': '4fdf7757-ba58-4a4b-a1df-1ad4d102a474', 'MusicBrainz Album Id': '18f635aa-dc20-4fbf-a3f3-d63de3bd0fb6',
        'MusicBrainz Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f', 'MusicBrainz Album Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f',
        'MusicBrainz Release Group Id': 'a7927f70-2431-3a58-b7ae-48576808cec1', 'date': '2002'},
    'filename': '/home/runner/work/MusicProcessing/MusicProcessing/tests/Music/Crush/Here/Crush-Live.mp3', 'nb_streams': '2', 'nb_programs': '0', 'nb_stream_groups': '0',
    'format_name': 'mp3', 'format_long_name': 'MP2/3 (MPEG audio layer 2/3)', 'size': '3970122', 'probe_score': '51'
}

# instantiate classes here
metadata = AudioMetadata()

'''
Get the effective level so we can disable logging when necessary.
In tests that use assertRaises, disable the logger at or below the log level of the tested function,
encapsulate the assertRaises in a try block, and use a finally to restore the original log level.
'''
original_log_level = logging.getLogger().getEffectiveLevel()


class TestAudioMetadata(unittest.TestCase):
    '''
    @brief Tests AudioMetadata class functions.
    '''

    def test_get_media_info_dict(self):
        '''
        @brief Tests returns dictionary with media info.
        '''

        os_name = platform.system()
        if os_name == "Linux":
            expected_info = LINUX_RESULT
        elif os_name == "Windows":
            expected_info = WIN_RESULT

        if os.environ.get('GITHUB_ACTIONS') == 'true':
            expected_info = CI_RESULT

        results_info = metadata.get_media_info_dict(MP3_PATH)
        self.maxDiff = None

        '''
        every os flavour has a slight diff in the return dict,
        especially the filename, so we just compare the TAG inner dict instead.
        '''
        self.assertDictEqual(expected_info['TAG'], results_info['TAG'])


    def test_load_any_file(self):
        '''
        @brief Tests attempt to load an audio file with mutagen.
        '''

        loaded_file = metadata.load_any_file(MP3_PATH)
        audio_class_name = loaded_file.__class__.__name__
        self.assertEqual(audio_class_name, "MP3")


    '''
    With a non-extant file, a mutagen load call will return a chained exception:
    MutagenError encapsulating a FileNotFoundError, so we check the exception context dunder,
    disable logging to prevent console clutter.


    '''
    def test_load_any_file_non_extant(self):
        '''
        @brief Tests attempt to load a non-extant audio file with mutagen.
        '''

        audio_file = None
        file_path = os.path.join(TESTS_TLD, EXPORT_TLD, "Non-extant.wav")

        logging.disable(logging.ERROR)

        try:
            with self.assertRaises(MutagenError) as cm:
                audio_file = metadata.load_any_file(file_path)

            self.assertIsNone(audio_file)
            self.assertIsInstance(cm.exception.__context__, FileNotFoundError)
        finally:
            logging.disable(original_log_level)


    def test_load_m4a_file_non_extant(self):
        '''
        @brief Tests attempt to load a non-extant audio file with mutagen.
        '''

        audio_file = None
        file_path = os.path.join(TESTS_TLD, EXPORT_TLD, "Non-extant.m4a")

        logging.disable(logging.ERROR)

        try:
            with self.assertRaises(MutagenError) as cm:
                audio_file = metadata.load_m4a_file(file_path)

            self.assertIsNone(audio_file)
            self.assertIsInstance(cm.exception.__context__, FileNotFoundError)
        finally:
            logging.disable(original_log_level)


    def test_load_mp3_file_non_extant(self):
        '''
        @brief Tests attempt to load a non-extant audio file with mutagen.
        '''

        audio_file = None
        file_path = os.path.join(TESTS_TLD, EXPORT_TLD, "Non-extant.mp3")

        logging.disable(logging.ERROR)

        try:
            with self.assertRaises(MutagenError) as cm:
                audio_file = metadata.load_mp3_file(file_path)

            self.assertIsNone(audio_file)
            self.assertIsInstance(cm.exception.__context__, FileNotFoundError)
        finally:
            logging.disable(original_log_level)


    def test_load_wma_file_non_extant(self):
        '''
        @brief Tests attempt to load a non-extant audio file with mutagen.
        '''

        audio_file = None
        file_path = os.path.join(TESTS_TLD, EXPORT_TLD, "Non-extant.wma")

        logging.disable(logging.ERROR)

        try:
            with self.assertRaises(MutagenError) as cm:
                audio_file = metadata.load_wma_file(file_path)

            self.assertIsNone(audio_file)
            self.assertIsInstance(cm.exception.__context__, FileNotFoundError)
        finally:
            logging.disable(original_log_level)


    def test_load_wma_file_with_mp3(self):
        '''
        @brief Attempt to load a mp3 as wma with mutagen.

        @details Expected to throw custom exception, so we disable logging to keep console uncluttered.
        '''

        audio_file = None

        logging.disable(logging.ERROR)

        try:
            with self.assertRaises(MusicProcessingError) as cm:
                audio_file = metadata.load_wma_file(MP3_PATH)

            self.assertIsNone(audio_file)
            self.assertEqual(cm.exception.message, f"MusicProcessingError {MP3_PATH} not wma")
        finally:
            logging.disable(original_log_level)


def get_method_names(cls):
    '''
    @brief Returns a list of methods defined within a given class.

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
    methods = get_method_names(TestAudioMetadata)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestAudioMetadata(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

