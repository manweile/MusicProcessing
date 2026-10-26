
'''
@class AudioUtilities
@file audio_utilities.py
@author Gerald Manweiler

@brief Defines the audio utilities class.

@details Defines utility methods that coordinate audio processing operations across project components.

@version 1.0.0
@date 2026-09-22

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import inspect                                              # for current function inspection
import logging                                              # for module logging
import math                                                 # for volume calculations
import os                                                   # for operating-system interfaces
from pathlib import Path                                    # for object-oriented filesystem paths

# Local Module Methods
from src import add_module_handler                          # for module-specific logging handlers

# Local Module Constants
from src import ILT                                         # for integrated loudness target
from src import LRA                                         # for loudness range target
from src import MP3_EXT                                     # for MP3 file extension
from src import TP                                          # for true-peak normalization target

# Local Module Classes
from src.audio_normalize import AudioNormalization          # for audio normalization functionality
from src.dir_processing import DirectoryProcessing          # for directory processing functionality
from src.subprocess_utils import SubprocessUtilities        # for subprocess utility functionality

## @var logger
# @brief Logger instance for the module.
# @details Sets the logger name to the current module name.
logger = logging.getLogger(__name__)

## @var basename
# @brief Base name for the logger file handler.
# @details Gets the module file name from the current file path.
basename = os.path.basename(__file__)

add_module_handler(logger, basename)

## @var directory
# @brief Directory processing instance.
# @details Provides directory processing functionality.
directory = DirectoryProcessing()

## @var normalization
# @brief Audio normalization instance.
# @details Provides audio normalization functionality.
normalization = AudioNormalization()

## @var subprocess_utils
# @brief Subprocess utilities instance.
# @details Provides subprocess utility functionality.
subprocess_utils = SubprocessUtilities()


class AudioUtilities():
    '''
    @brief Defines the audio utilities processing class.

    @details Provides utility methods that coordinate audio processing operations across project components.
    '''

    def __init__(self) -> None:
        '''
        @brief Initializes the AudioUtilities class.

        @details Initializes an AudioUtilities instance without instance-specific state.
        '''

        pass


    def clip_check_file(self, file_path: str, text_mode: str | None = None) -> None:
        '''
        @brief Checks for potential clipping and headroom in a single MP3 file.

        @details Analyzes the specified MP3 file and records volume-normalization information.<br>
        Creates a text file in the specified or default directory to store the analysis results.

        @param self {AudioUtilities} The instance of the class.
        @param file_path {str} The path to the audio file.
        @param text_mode {str} Optional text mode for writing the file.
        @return {None} This function does not return any value.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        txt_filename = inspect.currentframe().f_code.co_name

        true_peak = float(TP)

        try:
            _, input_file_ext = os.path.splitext(file_path)
            if input_file_ext.lower() != MP3_EXT:
                logger.warning(f"{file_path} is not an mp3")
                return

            file_text = f"\n{file_path}"
            data.append(file_text)

            # Retrieve volume and loudness information for the audio file
            volume_info = normalization.get_volume_info(file_path)
            ebu_info = normalization.get_ebu_loudness_info(file_path)

            # Check if volume information is available before proceeding with peak/rms analysis
            if 'mean_volume' not in volume_info or 'max_volume' not in volume_info:
                vol_text = "volume information unavailable"
                data.append(vol_text)
            else:
                # want the floor so don't inadvertently cause clipping (more negative dbs are quieter)
                mean_volume = float(math.floor(volume_info['mean_volume']))
                max_volume = float(math.floor(volume_info['max_volume']))

                if max_volume >= 0.0:
                    vol_text = f"no headroom (already clipping), max volume: {max_volume:.2f} dB"
                else:
                    vol_text = f"headroom available, max volume: {max_volume:.2f} dB"

                data.append(vol_text)

                # Apply an implicit 1.0 dB buffer pad to TP target to counter mp3 lossy compression overshoots
                target_tp = true_peak - 1.0
                TOLERANCE = 0.2

                # peak normalization lands on the target peak, so only a target above 0.0 dBFS can clip
                if target_tp > 0.0:
                    peak_text = f"peak clipping amount: {target_tp:.2f} dB with target peak above digital full scale"
                elif math.isclose(max_volume, target_tp, abs_tol=TOLERANCE):
                    peak_text = f"already at target peak: {max_volume:.2f} dB, peak normalization not needed"
                else:
                    peak_adjustment = target_tp - max_volume
                    peak_text = f"peak leveling adjustment: {peak_adjustment:+.2f} dB to target peak: {target_tp:.2f} dB"

                data.append(peak_text)

                # Skip processing if the average root mean square is already hitting the target window
                if math.isclose(mean_volume, true_peak, abs_tol=TOLERANCE):
                    rms_text = f"already at target rms: {mean_volume:.2f} dB, rms normalization not needed"
                else:
                    rms_adjustment = true_peak - mean_volume
                    rms_clip_amount = max_volume + rms_adjustment

                    if rms_clip_amount > 0.0:
                        rms_text = (
                            f"rms clipping amount: {rms_clip_amount:.2f} dB "
                            f"with mean volume: {mean_volume:.2f} dB, max volume: {max_volume:.2f} dB "
                            f"and rms adjustment: {rms_adjustment:+.2f} dB"
                        )
                    else:
                        rms_text = f"rms leveling adjustment: {rms_adjustment:+.2f} dB"

                data.append(rms_text)

            # Check if EBU loudness information is available before proceeding with ebu analysis
            required_ebu_values = ('input_i', 'input_tp', 'input_lra')
            if not all(value in ebu_info for value in required_ebu_values):
                ebu_text = "ebu loudness information unavailable"
                data.append(ebu_text)
            else:
                integrated_loudness = float(ebu_info['input_i'])
                ebu_true_peak = float(ebu_info['input_tp'])
                loudness_range = float(ebu_info['input_lra'])

                if not all(math.isfinite(value) for value in (integrated_loudness, ebu_true_peak, loudness_range)):
                    ebu_text = "ebu loudness information unavailable"
                    data.append(ebu_text)
                else:
                    target_loudness = float(ILT)
                    target_true_peak = float(TP)
                    target_loudness_range = float(LRA)
                    ebu_adjustment = target_loudness - integrated_loudness
                    projected_true_peak = ebu_true_peak + ebu_adjustment

                    # Determine if dynamic leveling is required based on projected true peak and loudness range
                    dynamic_reasons = []
                    if projected_true_peak > target_true_peak:
                        true_peak_excess = projected_true_peak - target_true_peak
                        dynamic_reasons.append(f"linear gain would exceed the true-peak target by {true_peak_excess:.2f} dB")

                    if loudness_range > target_loudness_range:
                        dynamic_reasons.append(
                            f"input loudness range {loudness_range:.2f} LU exceeds the {target_loudness_range:.2f} LU target"
                        )

                    if dynamic_reasons:
                        ebu_text = (
                            f"ebu dynamic leveling required for {ebu_adjustment:+.2f} dB adjustment: "
                            f"{'; '.join(dynamic_reasons)}"
                        )
                    elif math.isclose(ebu_adjustment, 0.0, abs_tol=0.2):
                        ebu_text = f"already at target ebu loudness: {integrated_loudness:.2f} LUFS"
                    else:
                        ebu_text = (
                            f"ebu linear leveling adjustment: {ebu_adjustment:+.2f} dB "
                            f"to target integrated loudness: {target_loudness:.2f} LUFS"
                        )

                data.append(ebu_text)

            directory.create_txt(txt_filename, data, None, text_mode)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} checking clipping and headroom for file {file_path}", stack_info=True)
            raise e_error


    def clip_check_walk(self, tld_path: str) -> None:
        '''
        @brief Analyzes volume and ebu loudness for MP3 files.

        @details Walks the input directory, calls `clip_check_file` to analyze & record what leveling techniques can be used for each MP3 file.<br>
        Will append the analysis results to any extant `clip_check_file.txt` for each MP3 file encountered.

        @param self {AudioUtilities} The instance of the class.
        @param tld_path {str} The top level directory path that contains all the music files.<br>
        The starting path can be the top level directory (tld), an artist folder (fld), but not an album folder (sld).
        @return {None} This function does not return any value.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            input_file_ext = None
            input_path = Path(tld_path)
            file_path = None

            for root, dirs, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    if input_file_ext.lower() != MP3_EXT:
                        continue
                    else:
                        file_path = os.path.join(root, file)

                    self.clip_check_file(file_path, "a")

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} while clip and max volume checking audio file: {file_path}", stack_info=True)
            raise e_error
