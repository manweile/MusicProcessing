
'''
@file test_audio_metadata.py
@brief Defines the test audio metadata class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import os
import unittest

# third party modules
# import ipsumlorem

# local modules
# from src import AUDIO_EXTS, AUDIO_TYPES
from src import EXPORT_TLD
# from src import FOLDER_ART
# from src import PLAYLIST_EXTS
# from src.generated_files import GENERATED_FILES
# from src.audio_info import AudioArt
from src.audio_info import AudioMetadata
# from src.audio_info import AudioPlaylist
# from src.audio_normalize import AudioNormalization
# from src.dir_processing import DirectoryProcessing

gc.enable()

# instantiate module levels vars here
TESTS_TLD = os.path.dirname(os.path.abspath(__file__))
MP3_FILE = os.path.join("Crush", "Here", "Crush-Live.mp3")
SRC_FILE = os.path.join(TESTS_TLD, EXPORT_TLD, MP3_FILE)
EXPECTED_MEDIA_INFO = {
    'index': '1',
    'codec_name': 'mjpeg', 'codec_long_name': 'Motion JPEG', 'profile': 'Baseline', 'codec_type': 'video', 'codec_tag_string': '[0][0][0][0]', 'codec_tag': '0x0000',
    'sample_fmt': 'fltp', 'sample_rate': '44100',
    'channels': '2', 'channel_layout': 'stereo',
    'bits_per_sample': '0',
    'initial_padding': '0',
    'id': 'N/A',
    'r_frame_rate': '90000/1', 'avg_frame_rate': '0/0',
    'time_base': '1/90000',
    'start_pts': 'N/A', 'start_time': '0.000000', 'duration_ts': '22131951', 'duration': '245.910567',
    'bit_rate': '129156', 'max_bit_rate': 'N/A', 'bits_per_raw_sample': '8',
    'nb_frames': 'N/A', 'nb_read_frames': 'N/A', 'nb_read_packets': 'N/A',
    'DISPOSITION': {'default': '0', 'dub': '0', 'original': '0', 'comment': '0', 'lyrics': '0', 'karaoke': '0', 'forced': '0',
                    'hearing_impaired': '0', 'visual_impaired': '0', 'clean_effects': '0', 'attached_pic': '1',
                    'timed_thumbnails': '0', 'non_diegetic': '0', 'captions': '0', 'descriptions': '0', 'metadata': '0',
                    'dependent': '0', 'still_image': '0', 'multilayer': '0'},
    'width': '500', 'height': '490', 'coded_width': '500', 'coded_height': '490', 'has_b_frames': '0', 'sample_aspect_ratio': '1:1',
    'display_aspect_ratio': '50:49', 'pix_fmt': 'yuvj420p', 'level': '-99', 'color_range': 'pc', 'color_space': 'bt470bg',
    'color_transfer': 'unknown', 'color_primaries': 'unknown', 'chroma_location': 'center', 'field_order': 'unknown', 'refs': '1',
    'TAG': {'comment': 'Cover (front)', 'title': 'Live', 'artist': 'Crush', 'track': '1/12', 'album': 'Here', 'disc': '1/1',
            'genre': 'Pop', 'TMED': 'CD', 'TORY': '2002', 'MusicBrainz Release Track Id': '2475137d-6745-3951-a361-d4c29798f5d1',
            'album_artist': 'Crush', 'TSO2': 'Crush', 'artist-sort': 'Crush', 'composer': 'Paul Lamb', 'SCRIPT': 'Latn',
            'publisher': 'Sonic Records', 'ARTISTS': 'Crush', 'ASIN': 'B000065PP6', 'originalyear': '2002', 'BARCODE': '627915092229',
            'CATALOGNUMBER': '2 50922', 'MusicBrainz Album Type': 'album', 'MusicBrainz Album Status': 'official',
            'MusicBrainz Album Release Country': 'CA', 'Acoustid Id': '4fdf7757-ba58-4a4b-a1df-1ad4d102a474',
            'MusicBrainz Album Id': '18f635aa-dc20-4fbf-a3f3-d63de3bd0fb6', 'MusicBrainz Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f',
            'MusicBrainz Album Artist Id': '6d5088d8-e756-47c4-84ae-bc675dee004f', 'MusicBrainz Release Group Id': 'a7927f70-2431-3a58-b7ae-48576808cec1',
            'date': '2002'},
    'filename': 'D:\\MusicProcessing\\tests\\Music\\Crush\\Here\\Crush-Live.mp3',
    'nb_streams': '2', 'nb_programs': '0', 'nb_stream_groups': '0',
    'format_name': 'mp3', 'format_long_name': 'MP2/3 (MPEG audio layer 2/3)',
    'size': '3970122', 'probe_score': '51'}

# instantiate classes here
# art = AudioArt()
# directory = DirectoryProcessing()
metadata = AudioMetadata()
# normalization = AudioNormalization()
# playlist = AudioPlaylist()


class TestAudioMetadata(unittest.TestCase):
    '''
    @brief Tests AudioMetadata class functions.
    '''

    def test_get_media_info_dict(self):
        '''
        @brief Tests Returns dictionary with media info.
        '''

        media_info = metadata.get_media_media_info_dict(SRC_FILE)
        self.assertDictEqual(media_info, EXPECTED_MEDIA_INFO)



if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestAudioMetadata('test_get_media_info_dict'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
