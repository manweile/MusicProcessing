'''
@package tests
@file tests/__init__.py
@author Gerald Manweiler

@brief Package for MusicProcessing test fixtures.

@details Exposes shared fixture paths and metadata constants for project test modules.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import os                                                   # for operating-system path operations

# Local Module Methods
from src.core.logging_config import bootstrap_logging       # for test logging startup

# Local Module Constants
from src.core.constants import MUSIC_TLD                    # for the test music top level directory

# Configure package logging before test modules import application modules
bootstrap_logging()

## @var TESTS_PATH
# @brief Test-fixture directory path.
# @details Provides a shared path without hard-coded test directory values elsewhere in the codebase.
TESTS_PATH = os.path.dirname(os.path.abspath(__file__))

## @var TESTS_TLD
# @brief Test music top level directory path.
# @details Provides the root directory for audio test fixtures.
TESTS_TLD = os.path.join(TESTS_PATH, MUSIC_TLD)

## @var TEST_M3U
# @brief Test M3U playlist path.
# @details Provides an input playlist fixture for audio playlist tests.
TEST_M3U = os.path.join(TESTS_TLD, "test.m3u")

## @var TEST_M4A_DAVIS
# @brief Path to m4a audio file for tests.
# @details Use this when needing a m4a audio file for audio art tests.
# @details Use this when needing a valid audio file for directory processing tests.
# @details This m4a has a MP4 covr album art tag.
TEST_M4A_DAVIS = os.path.join(TESTS_TLD, "Joshua Davis", "The Voice Peformance", "Joshua Davis-The Workingman's Hymn.m4a")

## @var TEST_M4A_DAVIS_ALBUM_ARTIST
# @brief Album artist metadata in the Joshua Davis M4A fixture.
# @details Provides the expected album artist for metadata assertions.
TEST_M4A_DAVIS_ALBUM_ARTIST = "Joshua Davis"

## @var TEST_M4A_DAVIS_TITLE
# @brief Title metadata in the Joshua Davis M4A fixture.
# @details Provides the expected title for metadata assertions.
TEST_M4A_DAVIS_TITLE = "The Workingman’s Hymn"

## @var TEST_M4A_EAGLES
# @brief Path to m4a audio file for tests.
# @details Use this when needing a m4a audio file for audio metadata tests.
# @details This mp3 has a co-located Folder.jpg file.
TEST_M4A_EAGLES = os.path.join(TESTS_TLD, "The Eagles", "Desperado", "The Eagles-Desperado.m4a")

## @var TEST_M4A_EAGLES_ALBUM_ARTIST
# @brief Album artist metadata in the Eagles M4A fixture.
# @details Provides the expected album artist for metadata assertions.
TEST_M4A_EAGLES_ALBUM_ARTIST = "The Eagles"

## @var TEST_M4A_EAGLES_TITLE
# @brief Title metadata in the Eagles M4A fixture.
# @details Provides the expected title for metadata assertions.
TEST_M4A_EAGLES_TITLE = "Desperado"

## @var TEST_FLAC_ALANNAH_MYLES
# @brief Path to Alannah Myles FLAC file for tests.
# @details Use this when needing a FLAC file with embedded album art for audio art tests.
TEST_FLAC_ALANNAH_MYLES = os.path.join(TESTS_TLD, "Alannah Myles", "A-Lan-Nah", "Alannah Myles-Do You Really Wanna Know Me.flac")

## @var TEST_FLAC_CREAM
# @brief Path to FLAC file for tests.
# @details Use this when needing a FLAC file with embedded album art for audio art tests.
TEST_FLAC_CREAM = os.path.join(TESTS_TLD, "Cream", "Goodbye", "02. Politician.flac")

## @var TEST_FLAC_CREAM_BADGE
# @brief Path to Cream-Badge FLAC file for audio metadata tests.
# @details This FLAC has a co-located Folder.jpg file.
TEST_FLAC_CREAM_BADGE = os.path.join(TESTS_TLD, "Cream", "Goodbye", "Cream-Badge.flac")

## @var TEST_FLAC_CREAM_ALBUM_ARTIST
# @brief Album artist metadata in the Cream FLAC fixture.
# @details Provides the expected album artist for metadata assertions.
TEST_FLAC_CREAM_ALBUM_ARTIST = "Cream"

## @var TEST_FLAC_CREAM_TITLE
# @brief Title metadata in the Cream FLAC fixture.
# @details Provides the expected title for metadata assertions.
TEST_FLAC_CREAM_TITLE = "Politician (Live)"

## @var TEST_FLAC_CREAM_INVALID_TITLE
# @brief Title metadata containing a Windows-invalid filename character.
# @details Provides an invalid filename value for directory-name sanitization tests.
TEST_FLAC_CREAM_INVALID_TITLE = "Politician (Live?)"

## @var TEST_MP3_10CC
# @brief Path to mp3 audio file for tests.
# @details Use this when needing a mp3 audio file for audio metadata tests.
TEST_MP3_10CC = os.path.join(TESTS_TLD, "10cc", "10cc", "04 - Donna.mp3")

## @var TEST_MP3_10CC_ALBUM_ARTIST
# @brief Album artist metadata in the 10cc MP3 fixture.
# @details Provides the expected album artist for metadata assertions.
TEST_MP3_10CC_ALBUM_ARTIST = "10cc"

## @var TEST_MP3_10CC_TITLE
# @brief Title metadata in the 10cc MP3 fixture.
# @details Provides the expected title for metadata assertions.
TEST_MP3_10CC_TITLE = "Donna"

## @var TEST_MP3_ABBA
# @brief Path to mp3 audio file for tests.
# @details Use this when needing a mp3 audio file for audio art tests.
# @details Use this when needing a mp3 audio file for audio metadata tests.
# @details Use this when needing a mp3 audio file for audio normalization tests.
# @details This mp3 has a co-located Folder.jpg file.
TEST_MP3_ABBA = os.path.join(TESTS_TLD, "Abba", "Waterloo", "ABBA-Waterloo.mp3")

## @var TEST_MP3_CRUSH
# @brief Path to mp3 audio file for tests.
# @details Use this when needing a mp3 audio file for audio art tests.
# @details Use this when needing a mp3 audio file for audio metadata tests.
# @details Use this when needing a mp3 audio file for audio normalization tests.
# @details This mp3 has a video stream and an ID3 APIC album art tag.
TEST_MP3_CRUSH = os.path.join(TESTS_TLD, "Crush", "Here", "Crush-Live.mp3")

## @var TEST_DIAMOND_RIO
# @brief Path to Diamond Rio MP3 file for audio utility tests.
# @details Use this when needing an MP3 with no headroom for clip-check tests.
TEST_DIAMOND_RIO = os.path.join(TESTS_TLD, "Diamond Rio", "Diamond Rio-Lyin' Eyes.mp3")

## @var TEST_LENNOX
# @brief Path to Annie Lennox MP3 file for audio utility tests.
# @details Use this when needing an MP3 already at target peak for clip-check tests.
TEST_LENNOX = os.path.join(TESTS_TLD, "The Lord of the Rings", "The Return of the King", "Annie Lennox - Into the West.mp3")

## @var TEST_MP3_GENESIS
# @brief Path to mp3 audio file for tests.
# @details Use this when needing a mp3 audio file for audio metadata tests.
TEST_MP3_GENESIS = os.path.join(TESTS_TLD, "Genesis", "In Too Deep-I’d Rather Be You", "Genesis-In Too Deep.mp3")

## @var TEST_MP3_NO_METADATA
# @brief Path to mp3 audio file for tests.
# @details Use this when needing a mp3 audio file with no metadata for audio metadata tests.
TEST_MP3_NO_METADATA = os.path.join(TESTS_TLD, "NoMetadata", "Here", "No_tag_Crush-Live.mp3")

## @var TEST_MP3_NO_TAG
# @brief Path to mp3 audio file for tests.
# @details Use this when needing a mp3 audio file with no metadata for audio art tests.
# @details Use this when needing a mp3 audio file with no metadata for audio metadata tests.
TEST_MP3_NO_TAG = os.path.join(TESTS_TLD, "Crush", "Here", "No_tag_Crush-Live.mp3")

## @var TEST_MP3_SMEAGOL
# @brief Path to mp3 audio file for tests.
# @details Use this when needing a mp3 audio file for audio normalization tests.
TEST_MP3_SMEAGOL = os.path.join(TESTS_TLD, "The Lord of the Rings", "The Two Towers", "Howard Shore-The Taming Of Smeagol.mp3")

## @var TEST_MP3_X
# @brief Path to mp3 audio file for tests.
# @details Use this when needing a mp3 audio file for audio normalization tests.
TEST_MP3_X = os.path.join(TESTS_TLD, "X Ambassadors", "VHS", "X Ambassadors-Renegades.mp3")

## @var TEST_WAV_NONE
# @brief Path to wav audio file for tests.
# @details Use this when needing a nonextant wav audio file for audio metadata tests.
# @details Use this when needing a nonextant wav audio file for subprocess utilities tests.
TEST_WAV_NONE = os.path.join(TESTS_TLD, "nonextant.wav")

## @var TEST_WMA_CCR
# @brief Path to wma audio file for tests.
# @details Use this when needing a wma audio file for audio metadata tests.
# @details This wma has a co-located Folder.jpg file.
TEST_WMA_CCR = os.path.join(TESTS_TLD, "Creedence Clearwater Revival", "Chronicle, Vol. 1", "Creedence Clearwater Revival-Fortunate Son.wma")

## @var TEST_WMA_HOLIDAY
# @brief Path to wma audio file for tests.
# @details Use this when needing a wma audio file for audio art tests.
# @details This does not have a video stream and and does have a WM/Picture album art tag.
TEST_WMA_HOLIDAY = os.path.join(TESTS_TLD, "Billie Holiday", "Georgia On My Mind", "Billie Holiday-Georgia On My Mind.wma")

## @var TEST_WMA_JOHN
# @brief Path to wma audio file for tests.
# @details Use this when needing a wma audio file for audio art tests.
# @details This wma has a video stream and a WM/Picture album art tag.
TEST_WMA_JOHN = os.path.join(TESTS_TLD, "Elton John", "Goodbye Yellow Brick Road", "Elton John-Saturday Night's Alright for Fighting.wma")

## @var TEST_WMA_JOHN_ALBUM_ARTIST
# @brief Album artist metadata in the Elton John WMA fixture.
# @details Provides the expected album artist for metadata assertions.
TEST_WMA_JOHN_ALBUM_ARTIST = "Elton John"

## @var TEST_WMA_JOHN_TITLE
# @brief Title metadata in the Elton John WMA fixture.
# @details Provides the expected title for metadata assertions.
TEST_WMA_JOHN_TITLE = "Saturday Night’s Alright (for Fighting)"

## @var __all__
# @brief Exposes test fixtures for importing by test modules.
# @details In modules needing the constant, add `from tests import <CONSTANT_NAME>`.
__all__ = [
    "TEST_DIAMOND_RIO",
    "TEST_FLAC_ALANNAH_MYLES",
    "TEST_FLAC_CREAM",
    "TEST_FLAC_CREAM_ALBUM_ARTIST",
    "TEST_FLAC_CREAM_BADGE",
    "TEST_FLAC_CREAM_INVALID_TITLE",
    "TEST_FLAC_CREAM_TITLE",
    "TEST_LENNOX",
    "TEST_M3U",
    "TEST_M4A_DAVIS",
    "TEST_M4A_DAVIS_ALBUM_ARTIST",
    "TEST_M4A_DAVIS_TITLE",
    "TEST_M4A_EAGLES",
    "TEST_M4A_EAGLES_ALBUM_ARTIST",
    "TEST_M4A_EAGLES_TITLE",
    "TEST_MP3_10CC",
    "TEST_MP3_10CC_ALBUM_ARTIST",
    "TEST_MP3_10CC_TITLE",
    "TEST_MP3_ABBA",
    "TEST_MP3_CRUSH",
    "TEST_MP3_GENESIS",
    "TEST_MP3_NO_METADATA",
    "TEST_MP3_NO_TAG",
    "TEST_MP3_SMEAGOL",
    "TEST_MP3_X",
    "TESTS_PATH",
    "TESTS_TLD",
    "TEST_WAV_NONE",
    "TEST_WMA_CCR",
    "TEST_WMA_HOLIDAY",
    "TEST_WMA_JOHN",
    "TEST_WMA_JOHN_ALBUM_ARTIST",
    "TEST_WMA_JOHN_TITLE"
]
