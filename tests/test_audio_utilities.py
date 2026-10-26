'''
@class TestAudioUtilities
@file test_audio_utilities.py
@author Gerald Manweiler

@brief Defines the test audio utilities class.

@details Tests utility behavior that checks audio clipping and volume levels.

@version 1.0.0
@date 2026-09-22

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import os
import tempfile                                             # for temporary fake audio files
import unittest                                             # for direct test-suite execution
from unittest import TestCase                               # for test-case assertions
from unittest.mock import patch                             # for patched subprocess calls

# Local Module Methods
from tests.support import get_method_names                  # for direct test-suite construction

# Local Module Constants
from src import RESULT_DIR                                  # for result text directory
from src import RESULT_EXT                                  # for result text extension
from src.generated_files import GENERATED_PATH              # for generated output paths
from tests import TESTS_TLD                                 # for audio utility walk input

# Local Module Classes
from src.audio_info import AudioUtilities                   # for utility functionality under test
from src.audio_info.audio_utilities import normalization    # for test-specific loudness configuration

## @var utilities
# @brief AudioUtilities instance under test.
# @details Provides access to audio utility functionality.
utilities = AudioUtilities()


class TestAudioUtilities(TestCase):
    '''
    @brief Tests AudioUtilities class functions.

    @details Verifies audio utility behavior using music test fixtures.
    '''


    def _run_clip_check(self, volume_info, ebu_info=None):
        '''
        @brief Run clip_check_walk on one fake mp3 with mocked loudness information.

        @details Creates a temporary directory with a single fake MP3 file and runs the clip check on it.<br>
        Using mocked volume and EBU loudness information is easier than creating actual audio with specific characteristics.

        @param self {TestAudioUtilities} The instance of the test class.
        @param volume_info {dict} Mocked volume information returned for the file.
        @param ebu_info {dict} Mocked EBU loudness information returned for the file.
        @return report {str} The report lines joined by newlines.
        '''

        # Ensure EBU info is set to default if not provided
        if ebu_info is None:
            ebu_info = {'input_i': -20.0, 'input_tp': -10.0, 'input_lra': 5.0}

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create an empty fake MP3 file for testing
            fake_mp3 = os.path.join(tmp_dir, "song.mp3")
            open(fake_mp3, "w").close()

            # Define the paths to the functions that will be mocked during the test
            get_volume_info_path = "src.audio_info.audio_utilities.normalization.get_volume_info"
            get_ebu_info_path = "src.audio_info.audio_utilities.normalization.get_ebu_loudness_info"
            create_txt_path = "src.audio_info.audio_utilities.directory.create_txt"

            # Prepare the patch objects for mocking the utility functions
            patch_volume_info = patch(get_volume_info_path, return_value=volume_info)
            patch_ebu_info = patch(get_ebu_info_path, return_value=ebu_info)
            patch_create_txt = patch(create_txt_path)

            # Patch the volume info, EBU info, and create_txt functions to control their behavior during the test
            with patch_volume_info, patch_ebu_info, patch_create_txt as create_txt:
                utilities.clip_check_walk(tmp_dir)

        # Retrieve the mock report content from the create_txt call arguments
        mock_report = create_txt.call_args[0][1]
        format_report = "\n".join(mock_report)

        return format_report


    def test_clip_check_walk(self):
        '''
        @brief Test for potential clipping and headroom analysis over a directory walk.

        @details Verifies the utility processes all audio fixtures in the top-level music directory.

        @test Happy path.

        @param self {TestAudioUtilities} The instance of the test class.
        '''

        # walk through audio test fixtures in the top-level music directory
        converted_tld = TESTS_TLD
        get_ebu_loudness_info = normalization.get_ebu_loudness_info

        # Patch the get_ebu_loudness_info function to control its behavior during the test
        with patch.object(
            normalization,
            "get_ebu_loudness_info",
            side_effect=lambda file_path: get_ebu_loudness_info(file_path, show_spinner=False)
        ):
            utilities.clip_check_walk(converted_tld)

        #  verify output txt file exists
        txt_filename = "clip_check_file"
        output_path = os.path.join(GENERATED_PATH, RESULT_DIR, f"{txt_filename}{RESULT_EXT}")
        self.assertTrue(os.path.exists(output_path))

        # verify file contains expected leveling information
        with open(output_path, "r") as f:
            content = f.read()

        self.assertIn("headroom available", content)
        self.assertIn("no headroom", content)

        self.assertIn("peak leveling adjustment", content)
        self.assertIn("already at target peak", content)

        self.assertIn("rms leveling adjustment", content)
        self.assertIn("rms clipping amount", content)

        self.assertIn("ebu dynamic leveling required", content)
        self.assertIn("ebu linear leveling adjustment", content)


    def test_clip_check_leveling(self):
        '''
        @brief Test peak and rms leveling reports match the normalizers when headroom exists.

        @details Uses TP -2.0, so peak target is -3.0 dB and rms target is -2.0 dB.

        @test Happy path.

        @param self {TestAudioUtilities} The instance of the test class.
        '''

        report = self._run_clip_check({'mean_volume': -20.0, 'max_volume': -10.0})

        self.assertIn("headroom available", report)
        self.assertIn("peak leveling adjustment: +7.00 dB", report)

        # rms +18 dB would push the -10 dB peak to +8 dB
        self.assertIn("rms clipping amount: 8.00 dB", report)
        self.assertNotIn("peak clipping amount", report)
        self.assertIn("ebu linear leveling adjustment: +4.00 dB", report)


    def test_clip_check_no_headroom(self):
        '''
        @brief Test a file already clipping is reported as having no headroom.

        @details Verifies that when a file is already clipping, the function reports no headroom and indicates the necessary adjustments.

        @test Edge case.

        @param self {TestAudioUtilities} The instance of the test class.
        '''

        report = self._run_clip_check({'mean_volume': -10.0, 'max_volume': 0.0})

        self.assertIn("no headroom", report)
        self.assertIn("peak leveling adjustment: -3.00 dB", report)
        self.assertIn("rms clipping amount: 8.00 dB", report)


    def test_clip_check_already_at_target(self):
        '''
        @brief Test files within tolerance of the targets are reported as not needing normalization.

        @details Verifies when the file is already at target levels, function reports it correctly without suggesting further normalization.

        @test Edge case.

        @param self {TestAudioUtilities} The instance of the test class.
        '''

        report = self._run_clip_check({'mean_volume': -2.0, 'max_volume': -3.0})

        self.assertIn("already at target peak", report)
        self.assertIn("already at target rms", report)


    def test_clip_check_ebu_dynamic_required(self):
        '''
        @brief Test EBU leveling reports when dynamic normalization is required.

        @details Verifies projected true-peak or loudness-range limits prevent linear normalization.

        @test Edge case.

        @param self {TestAudioUtilities} The instance of the test class.
        '''

        report = self._run_clip_check(
            {'mean_volume': -20.0, 'max_volume': -10.0},
            {'input_i': -20.0, 'input_tp': -8.0, 'input_lra': 12.0}
        )

        self.assertIn("ebu dynamic leveling required", report)


    def test_clip_check_ebu_already_at_target(self):
        '''
        @brief Test EBU leveling reports when all EBU targets are already met.

        @details Verifies that when all EBU targets are already met, the function reports it correctly without suggesting further normalization.

        @test Edge case.

        @param self {TestAudioUtilities} The instance of the test class.
        '''

        report = self._run_clip_check(
            {'mean_volume': -2.0, 'max_volume': -3.0},
            {'input_i': -16.0, 'input_tp': -3.0, 'input_lra': 8.0}
        )

        self.assertIn("already at target ebu loudness", report)


    @patch("src.audio_info.audio_utilities.TP", "2.0")
    def test_clip_check_bad_target(self):
        '''
        @brief Test a true-peak target above digital full scale is reported as clipping.

        @details Verifies a true-peak target above digital full scale is reported as clipping.<br>
        Patches TP to 2.0, so the buffered target peak is +1.0 dB.

        @test Edge case.

        @param self {TestAudioUtilities} The instance of the test class.
        '''

        report = self._run_clip_check({'mean_volume': -20.0, 'max_volume': -10.0})

        self.assertIn("peak clipping amount: 1.00 dB", report)


    def test_clip_check_missing_volume_info(self):
        '''
        @brief Test a file with no volume information is reported and skipped without error.

        @details Verifies that when no volume information is available, the function reports it and skips processing without raising an error.

        @test Edge case.

        @param self {TestAudioUtilities} The instance of the test class.
        '''

        report = self._run_clip_check({})

        self.assertIn("volume information unavailable", report)


if __name__ == "__main__":
    '''
    @brief Run the AudioUtilities test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.

    @note This test module can be run directly with `python tests/test_audio_utilities.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestAudioUtilities)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestAudioUtilities(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
