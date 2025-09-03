'''
@package tests
@brief Gets directory name for importing by other modules.
'''

# standard modules
import os

# local module constants
from src import MUSIC_TLD

## @var TESTS_PATH
# @brief Path to where test files and inputs used by the tests are stored.
# @details Getting the directory name for importing means will not need a hard coded "magic spell" else where in codebase.
# @details Ie. need /tests/
TESTS_PATH = ""
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))

## @var TESTS_TLD
# @brief Path to where the music audio files for tests are stored.
# @details Use this this when working with audio file tests.
# @details Ie. need /tests/Music/
TESTS_TLD = ""
TESTS_TLD = os.path.join(TESTS_PATH, MUSIC_TLD)

## @var INPUT_MRU
# @brief Path to where music playlist file for tests.
# @details Use this when needing an input m3u for audio playlist tests.
# @details Refer to the file contents for what type of tests it is valid for.
TEST_M3U = ""
TEST_M3U = os.path.join(TESTS_TLD, "test.m3u")

## @var TEST_M4A_DAVIS
# @brief Path to m4a audio file for tests.
# @details Use this when needing a m4a audio file for audio art tests.
# @details Use this when needing a valid audio file for directory processing tests.
# @details This m4a has a MP4 covr album art tag.
TEST_M4A_DAVIS = ""
TEST_M4A_DAVIS = os.path.join(TESTS_TLD, "Joshua Davis", "The Voice Peformance", "Joshua Davis-The Workingman's Hymn.m4a")

## @var TEST_M4A_EAGLES
# @brief Path to m4a audio file for tests.
# @details Use this when needing a m4a audio file for audio metadata tests.
# @details This mp3 has a co-located Folder.jpg file.
TEST_M4A_EAGLES = ""
TEST_M4A_EAGLES = os.path.join(TESTS_TLD, "The Eagles", "Desperado", "The Eagles-Desperado.m4a")

## @var TEST_MP3_ABBA
# @brief Path to mp3 audio file for tests.
# @details Use this when needing a mp3 audio file for audio art tests.
# @details Use this when needing a mp3 audio file for audio metadata tests.
# @details Use this when needing a mp3 audio file for audio normalization tests.
# @details This mp3 has a co-located Folder.jpg file.
TEST_MP3_ABBA = ""
TEST_MP3_ABBA = os.path.join(TESTS_TLD, "Abba", "Waterloo", "ABBA-Waterloo.mp3")

## @var TEST_MP3_CRUSH
# @brief Path to mp3 audio file for tests.
# @details Use this when needing a mp3 audio file for audio art tests.
# @details Use this when needing a mp3 audio file for audio metadata tests
# @details Use this when needing a mp3 audio file for audio normalization tests.
# @details This mp3 has a video stream and an ID3 APIC album art tag.
TEST_MP3_CRUSH = ""
TEST_MP3_CRUSH = os.path.join(TESTS_TLD, "Crush", "Here", "Crush-Live.mp3")

## @var TEST_MP3_X
# @brief Path to mp3 audio file for tests.
# @details Use this when needing a mp3 audio file for audio normalization tests.
TEST_MP3_X = ""
TEST_MP3_X = os.path.join(TESTS_TLD, "X Ambassadors", "VHS", "X Ambassadors-Renegades.mp3")

## @var TEST_WAV_NONE
# @brief Path to wav audio file for tests..
# @details Use this when needing a non-extant wav audio file for audio metadata tests.
# @details Use this when needing a non-extant wav audio file for subprocess utilities tests.
TEST_WAV_NONE = ""
TEST_WAV_NONE = os.path.join(TESTS_TLD, "Non-extant.wav")

## @var TEST_WMA_CCR
# @brief Path to wma audio file for tests.
# @details Use this when needing a wma audio file for audio metadata tests.
# @details This wma has a co-located Folder.jpg file.
TEST_WMA_CCR = ""
TEST_WMA_CCR = os.path.join(TESTS_TLD, "Creedence Clearwater Revival", "Chronicle, Vol. 1", "Creedence Clearwater Revival-Fortunate Son.wma")

## @var TEST_WMA_HOLIDAY
# @brief Path to wma audio file for tests.
# @details Use this when needing a wma audio file for audio art tests.
# @details This does not have a video stream and and does have a WM/Picture album art tag.
TEST_WMA_HOLIDAY = ""
TEST_WMA_HOLIDAY = os.path.join(TESTS_TLD, "Billie Holiday", "Georgia On My Mind", "Billie Holiday-Georgia On My Mind.wma")

## @var TEST_WMA_JOHN
# @brief Path to wma audio file for tests.
# @details Use this when needing a wma audio file for audio art tests.
# @details This wma has a video stream and a WM/Picture album art tag.
TEST_WMA_JOHN = ""
TEST_WMA_JOHN = os.path.join(TESTS_TLD, "Elton John", "Goodbye Yellow Brick Road", "Elton John-Saturday Night's Alright for Fighting.wma")

## @var __all__
# @brief Exposes variable for importing by other modules.
# @details In modules needing the directory, add `from src.tests.TESTS_PATH`
# @details In modules needing the directory, add `from src.tests.TESTS_TLD`
# @details In modules needing the directory, add `from src.tests.TEST_MRU`
# @details In modules needing the directory, add `from src.tests.TEST_M4A_DAVIS`
# @details In modules needing the directory, add `from src.tests.TEST_M4A_EAGLES`
# @details In modules needing the directory, add `from src.tests.TEST_MP3_ABBA`
# @details In modules needing the directory, add `from src.tests.TEST_MP3_CRUSH`
# @details In modules needing the directory, add `from src.tests.TEST_MP3_X`
# @details In modules needing the directory, add `from src.tests.TEST_WAV_NONE`
# @details In modules needing the directory, add `from src.tests.TEST_WMA_CCR`
# @details In modules needing the directory, add `from src.tests.TEST_WMA_HOLIDAY`
# @details In modules needing the directory, add `from src.tests.TEST_WMA_JOHN`
__all__ = [
    "TESTS_PATH", "TESTS_TLD",
    "TEST_M3U", "TEST_WAV_NONE",
    "TEST_M4A_DAVIS", "TEST_M4A_EAGLES"
    "TEST_MP3_ABBA", "TEST_MP3_CRUSH", "TEST_MP3_X",
    "TEST_WMA_CCR", "TEST_WMA_HOLIDAY", "TEST_WMA_JOHN"
]
