'''
@class AudioNormalization
@file audio_normalization.py
@author Gerald Manweiler

@brief Defines the audio normalization class.

@details Defines methods for analyzing and normalizing MP3 audio levels.

@version 1.0.0
@date 2026-09-22

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import gc                                                   # for garbage collection management
import inspect                                              # for current function inspection
import json                                                 # for FFmpeg JSON output parsing
import logging                                              # for module logging
import math                                                 # for volume calculations
import os                                                   # for operating-system interfaces
import re                                                   # for volume-output pattern matching
from json import JSONDecodeError                            # for JSON parsing errors
from pathlib import Path                                    # for object-oriented filesystem paths
from subprocess import CompletedProcess                     # for completed subprocess results

# Local Module Methods
from src import add_module_handler                          # for module-specific logging handlers

# Local Module Constants
from src import ILT                                         # for integrated loudness target
from src import LRA                                         # for loudness range target
from src import MP3_EXT                                     # for MP3 file extension
from src import TP                                          # for true-peak target

# Local Module Errors
from src.errors import JSONOutputError                      # for missing FFmpeg JSON output
from src.errors import PathInfoError                        # for missing generated-file paths

# Local Module Classes
from src.dir_processing import DirectoryProcessing          # for directory processing functionality
from src.subprocess_utils import SubprocessUtilities        # for subprocess utility functionality

gc.enable()

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

## @var subprocess_utils
# @brief Subprocess utilities instance.
# @details Provides subprocess utility functionality.
subprocess_utils = SubprocessUtilities()


class AudioNormalization():
    '''
    @brief Defines the audio normalization processing class.

    @details Provides methods to analyze audio levels and apply supported normalization strategies.
    '''

    def __init__(self) -> None:
        '''
        @brief Initializes the AudioNormalization class.

        @details Initializes an AudioNormalization instance without instance-specific state.
        '''

        pass


    def __loudnorm_json_parse(self, input_process: CompletedProcess) -> dict:
        '''
        @brief Parses JSON from FFmpeg loudnorm standard-error output.

        @details Expects the subprocess standard-error output to contain exactly one JSON object embedded within the log stream.

        @note A typical FFmpeg stderr payload contains text logs followed by the loudnorm statistics block.

        @code{.json}
        {
            "input_i" : "-16.77",
            "input_tp" : "-6.66",
            "input_lra" : "8.10",
            "input_thresh" : "-26.99",
            "output_i" : "-15.36",
            "output_tp" : "-2.00",
            "output_lra" : "5.60",
            "output_thresh" : "-25.47",
            "normalization_type" : "dynamic",
            "target_offset" : "-0.64"
        }
        @endcode

        @param input_process A subprocess.CompletedProcess instance containing the stderr data.
        @return A dictionary containing the following FFmpeg loudnorm statistics:
        - **input_i** *(str)*: Input integrated loudness (numeric string).
        - **input_tp** *(str)*: Input maximum true peak (numeric string).
        - **input_lra** *(str)*: Input loudness range target (numeric string).
        - **input_thresh** *(str)*: Input threshold (numeric string).
        - **output_i** *(str)*: Output integrated loudness (numeric string).
        - **output_tp** *(str)*: Output maximum true peak (numeric string).
        - **output_lra** *(str)*: Output loudness range target (numeric string).
        - **output_thresh** *(str)*: Output threshold (numeric string).
        - **normalization_type** *(str)*: Scaling type to apply (alphabetic string).
        - **target_offset** *(str)*: Offset gain applied before true peak limiter (numeric string).

        @exception JSONOutputError Indicates an error occurred finding the JSON structure.
        @exception json.JSONDecodeError A native JSON decoding error occurred if the block is malformed.
        '''

        try:
            output_data = None
            json_input = input_process.stderr

            json_start = json_input.find('{')
            json_end = json_input.rfind('}')

            if json_start != -1 and json_end != -1:
                json_string = json_input[json_start: json_end + 1]
            else:
                logger.error(f"JSONOutputError could not find JSON output in subprocess stderr\n{json_input}", exc_info=True)
                raise JSONOutputError(f"JSONOutputError could not find JSON output in subprocess stderr\n{json_input}")

            output_data = json.loads(json_string)

        except JSONDecodeError as jd_error:
            logger.error(f"JSONDecodeError parsing \n{json_input}", exc_info=True)
            raise jd_error
        except JSONOutputError as jo_error:
            raise jo_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} parsing ffmpeg loudnorm subprocess stderr", stack_info=True)
            raise e_error
        else:
            return output_data


    def ebu_normalize_file(self, file_path: str, show_spinner: bool = True) -> None:
        '''
        @brief Normalizes an audio file to the EBU R128 standard.

        @details Uses two-pass loudnorm normalization with FFmpeg.<br>
        The first pass checks audio properties of source file, which are then used as inputs in 2nd pass to apply the loudnorm normalization.<br>
        REQUIRES an MP3 file.

        @note Uses the loudnorm algorithm documented at https://k.ylo.ph/2016/04/04/loudnorm.html.<br>
        Uses the FFmpeg workflow described at https://wiki.tnonline.net/w/Blog/Audio_normalization_with_FFmpeg.<br>
        Refer to https://ffmpeg.org/ffmpeg-filters.html#loudnorm for filter documentation.<br>
        Refer to AESTD1004_1_15_10.pdf, official document from Audio Engineering Society https://aes.org/community/technical-council/<br>
        ffmpeg loudnorm integrated loudness target EBU R128 default: -24.0, using -16.0, which is the AES recommendation for streamed files<br>
        ffmpeg loudnorm loudness range target EBU R128 default: 7, using 11.0 for  wider range<br>
        ffmpeg loudnorm maximum true peak EBU R128 default: -2.0, using default for the extra headroom space vs -1.0 or 0.0<br>

        @code{.text}
        1st pass stats command to get loudnorm statistics
        ffmpeg -hide_banner -i file_path -vn -af loudnorm=I={ILT}:TP={TP}:LRA={LRA}:print_format=json -f null -

        -hide_banner; to reduce output clutter
        -i; input file path
        -vn; to save cycles by not dealing with video stream
        -af loudnorm=I={ILT}:TP={TP}:LRA={LRA}:; apply loudnorm filter with constants for ILT, TP and LRA
        print_format=json; output in json format
        -f null -; Output to null to avoid creating an actual output file

        2nd pass normalize command to apply loudnorm statistics
        ffmpeg -hide_banner -i file_path -id3v2_version 3
        -af loudnorm=I={ILT}:TP={TP}:LRA={LRA}:
          measured_I={measured_i}:measured_TP={measured_tp}:measured_LRA={measured_lra}:measured_thresh={measured_thresh}:
          offset={offset}:
          linear=true:
          print_format=json
        -b:a target_bitrate -ar sample_rate export_path -y

        -hide_banner; to reduce output clutter
        -i; input file path
        -id3v2_version 3; to enforce ID3v2.3 tags (it's a known bug of ffmpeg that when not set will default to ID3v2.4)
        -af loudnorm=I={ILT}:TP={TP}:LRA={LRA}:; apply loudnorm filter with constants for ILT, TP and LRA
          measured_I=...:; apply measured parameters from 1st pass
          offset={offset}:; apply the offset from the 1st pass
          linear=true:; use linear scaling
          print_format=json; output in json format
        -b:a; set the target audio bitrate
        -ar; set the audio sample rate
        export_path; the output file path
        -y; overwrite the output file if it exists
        @endcode

        @param file_path {str} The full file path for mp3 audio file.
        @param show_spinner {bool} Whether to display a progress spinner.

        @exception PathInfoError Indicates directory_processing.path_info function returned None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        txt_filename = inspect.currentframe().f_code.co_name

        try:
            _, input_file_ext = os.path.splitext(file_path)
            if input_file_ext.lower() != MP3_EXT:
                logger.warning(f"{file_path} is not an mp3")
                return

            export_path = directory.path_info(file_path)

            if export_path is None:
                logger.exception(f"PathInfoError with file {file_path} returned None", stack_info=True)
                raise PathInfoError(f"PathInfoError with file {file_path} returned None")
            else:
                directory.make_dir(os.path.dirname(export_path))

            input_path_basename = os.path.basename(file_path)
            input_path_dir = os.path.dirname(file_path)

            beginning_text = f"Beginning ebu normalization on: {input_path_basename}"
            source_text = f"Source directory path: {input_path_dir}"
            data.append(beginning_text)
            data.append(source_text)

            # get original sample rate for down sampling
            sample_rate = self.get_sample_rate(file_path)
            data.append(f"Source sample rate: {sample_rate} hz")

            # get original bitrate and ensure it does not exceed 192000 bps to have nice compromise between file size and audio quality
            original_bitrate = self.get_bit_rate(file_path)
            target_bitrate = min(original_bitrate, 192000)
            data.append(f"Source bitrate: {original_bitrate} bps -> Target bitrate: {target_bitrate} bps")

            stats_text = "Getting loudnorm stats"
            data.append(stats_text)

            stats_command = [
                "ffmpeg",
                "-hide_banner",
                "-i", file_path,
                "-vn",
                "-af", (f"loudnorm=I={ILT}:TP={TP}:LRA={LRA}:"
                        f"print_format=json"
                        ),
                "-f", "null", "-"
            ]
            data.append(stats_command)

            stats_pre_text = "Pre-normalization stats:"
            data.append(stats_pre_text)

            if show_spinner:
                # stats_process, stats_spinner = subprocess_utils.spinner_subprocess_run(stats_text, stats_command)
                stats_process, stats_spinner = subprocess_utils.spinner_subprocess_run(stats_command, stats_text)
                stats_time = stats_spinner.elapsed_time
                stats_post_text = f"Analyzed loudnorm stats in {stats_time:.2f} secs"
            else:
                stats_process = subprocess_utils.subprocess_run(stats_command)
                stats_post_text = "Analyzed loudnorm stats"

            # Even though hide banner & json is specified in ffmpeg cli, output will still have garbage, and needs parsing
            stats_data = self.__loudnorm_json_parse(stats_process)
            data.append(json.dumps(stats_data, indent=4))

            data.append(stats_post_text)

            # Access the loudnorm results needed for 2nd pass
            measured_i = stats_data.get("input_i")
            measured_lra = stats_data.get("input_lra")
            measured_tp = stats_data.get("input_tp")
            measured_thresh = stats_data.get("input_thresh")
            offset = stats_data.get("target_offset")

            normalizing_text = "Normalizing audio"
            data.append(normalizing_text)

            normalize_command = [
                "ffmpeg",
                "-hide_banner",
                "-i", file_path,
                "-id3v2_version", "3",
                "-af", (f"loudnorm=I={ILT}:TP={TP}:LRA={LRA}:"
                        f"measured_I={measured_i}:measured_TP={measured_tp}:"
                        f"measured_LRA={measured_lra}:measured_thresh={measured_thresh}:"
                        f"offset={offset}:linear=true"
                        f":print_format=json"
                        ),
                "-b:a", str(target_bitrate),
                "-ar", str(sample_rate),
                export_path, "-y"
            ]
            data.append(normalize_command)

            post_text = "Post normalization stats:"
            data.append(post_text)

            if show_spinner:
                normalize_process, normalize_spinner = subprocess_utils.spinner_subprocess_run(
                    normalize_command,
                    normalizing_text,
                )
                normalization_time = normalize_spinner.elapsed_time
                apply_post_text = f"Applied loudnorm stats in {normalization_time:.2f} secs"
                total_time = normalization_time + stats_time
                total_time_text = f" in total time {total_time:.2f} secs\n "
            else:
                normalize_process = subprocess_utils.subprocess_run(normalize_command)
                apply_post_text = "Applied loudnorm stats"
                total_time_text = ""

            normalize_data = self.__loudnorm_json_parse(normalize_process)
            data.append(json.dumps(normalize_data, indent=4))

            data.append(apply_post_text)

            normalization_type = normalize_data.get("normalization_type")
            if normalization_type == "dynamic":
                result_type_text = f"FFMPEG used {normalization_type} normalization on {input_path_basename}"
            elif normalization_type == "linear":
                result_type_text = f"Successful linear normalization on {input_path_basename}"

            results_text = result_type_text + total_time_text

            data.append(results_text)
            directory.create_txt(txt_filename, data)

        except PathInfoError as pi_error:
            raise pi_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} while ebu normalizing audio file: {file_path}", stack_info=True)
            raise e_error


    def get_bit_rate(self, file_path: str) -> int | None:
        '''
        @brief Retrieves the bitrate of a media file using ffprobe.

        @details Uses FFprobe to read the media container's bitrate.

        @code{.text}
        get bit rate command
        ffprobe -v error -print_format json -show_entries format=bit_rate file_path

        -v error; reduce clutter
        -print_format json; output in json format
        -show_entries format=bit_rate; get just the bit rate
        file_path; the path to the media file to be analyzed.
        @endcode

        @param file_path {str} The path to the media file.
        @return bit_rate {int | None} The bitrate in bits per second, or None if not found.

        @exception JSONDecodeError A json decoding error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            bit_rate = None

            command = [
                'ffprobe',
                '-v', 'error',
                '-print_format', 'json',
                '-show_entries', 'format=bit_rate',
                file_path
            ]

            result = subprocess_utils.subprocess_run(command)

            # unlike ffmpeg, ffprobe does use stdout
            data = json.loads(result.stdout)

            if 'format' in data and 'bit_rate' in data['format']:
                bit_rate = int(data['format']['bit_rate'])

        except IndexError as i_error:
            logger.error(f"IndexError no format found or bit rate information missing for audio file: {file_path}", exc_info=True)
            raise i_error
        except JSONDecodeError as jd_error:
            logger.error(f"JSONDecodeError decoding JSON output from ffprobe on audio file: {file_path}", exc_info=True)
            raise jd_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} normalizing audio file: {file_path}", stack_info=True)
            raise e_error
        else:
            return bit_rate


    def get_sample_rate(self, file_path: str) -> int | None:
        '''
        @brief Gets the sample rate from audio file.

        @details Uses FFprobe to read the first audio stream's sample rate.

        @code{.text}
        get sample rate command
        ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of json file_path

        -v error: reduce clutter
        -select_streams a:0; only want audio stream
        -show_entries stream=sample_rate; we only get the one entry specified
        -of json; to output in json format
        file_path; the path to the audio file to be analyzed.
        @endcode

        @param file_path {str} The full path to audio file.
        @return sample_rate {int | None} The sample rate in Hz, or None if not found.

        @exception IndexError An index error finding audio stream or sample rate information.
        @exception JSONDecodeError A json decoding error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            sample_rate = None

            command = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'a:0',
                '-show_entries', 'stream=sample_rate',
                '-of', 'json',
                file_path
            ]

            result = subprocess_utils.subprocess_run(command)

            # unlike ffmpeg, ffprobe does use stdout
            data = json.loads(result.stdout)

            if 'streams' in data and data['streams']:
                sample_rate = int(data['streams'][0]['sample_rate'])

        except IndexError as i_error:
            logger.error(f"IndexError no audio stream found or sample rate information missing for audio file: {file_path}", exc_info=True)
            raise i_error
        except JSONDecodeError as jd_error:
            logger.error(f"JSONDecodeError decoding JSON output from ffprobe on audio file: {file_path}", exc_info=True)
            raise jd_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} getting sample rate for audio file: {file_path}", stack_info=True)
            raise e_error
        else:
            return sample_rate


    def get_volume_info(self, file_path: str) -> dict:
        '''
        @brief Gets mean and max volume from audio file using ffmpeg.

        @details Uses FFmpeg's volumedetect filter to collect mean and maximum volume values.

        @code{.text}
        get volume information command
        ffmpeg -hide_banner -i file_path -filter:a volumedetect -f null -

        -hide_banner; to reduce output clutter
        -i file_path; specifies the input audio file
        -filter:a volumedetect; applies the volumedetect filter to the audio stream
        -f null -; sends the output to null to avoid creating an actual output file
        @endcode

        @param file_path {str} The full path to audio file.
        @return volumes {dict} The mean and max volumes of audio file in decibels relative to max PCM value.
        @code{.text}
        Key                 |Value
        --------------------|----------------------------------------
        mean_value {str}    |the root mean square volume {float}
        max_volume {str}    |the per-sample maximum volume {float}
        @endcode

        @exception re.error An error occurred processing a regular expression with re module.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            volumes = dict()

            command = [
                'ffmpeg',
                '-hide_banner',
                '-i', file_path,
                '-filter:a', 'volumedetect',
                '-f', 'null', '-'
            ]

            process = subprocess_utils.subprocess_run(command)

            # ffmpeg sends its output to stderr, not stdout
            output_str = process.stderr

            mean_volume_match = re.search(r'mean_volume: ([-]?\d+\.\d+) dB', output_str)
            max_volume_match = re.search(r'max_volume: ([-]?\d+\.\d+) dB', output_str)

            if mean_volume_match and max_volume_match:
                mean_volume = float(mean_volume_match.group(1))
                max_volume = float(max_volume_match.group(1))
                volumes['mean_volume'] = mean_volume
                volumes['max_volume'] = max_volume

        except re.error as re_error:
            logger.error(f"Regex error processing {output_str}", exc_info=True)
            raise re_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} getting volume for file {file_path}", stack_info=True)
            raise e_error
        else:
            return volumes


    def level_normalize_walk(self, tld_path: str, norm_type: str, show_spinner: bool = True) -> None:
        '''
        @brief Normalizes all audio files in specified top level directory per input normalization type.

        @details Normalizes only MP3 files beneath the specified top-level directory.

        @param tld_path {str} The top level directory path that contains all the music files.
        @param norm_type {str} The type of normalization to perform.
        @param show_spinner {bool} Whether to display a progress spinner.

        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            input_file_ext = None
            input_path = Path(tld_path)

            for dir_path, _, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    # file is not mp3, carry on to next file
                    if input_file_ext.lower() != MP3_EXT:
                        continue

                    input_file_path = os.path.join(dir_path, file)

                    if norm_type == "ebu":
                        self.ebu_normalize_file(input_file_path, show_spinner)
                    elif norm_type == "peak":
                        self.peak_normalize_file(input_file_path, show_spinner)
                    elif norm_type == "rms":
                        self.rms_normalize_file(input_file_path, show_spinner)

        except Exception as e_error:
            logger.exception(
                f"Exception {type(e_error).__name__} on {input_file_path} while walking {tld_path} "
                f"to {norm_type} normalize audio files",
                stack_info=True,
            )
            raise e_error


    def peak_normalize_file(self, file_path: str, show_spinner: bool = True) -> None:
        '''
        @brief Peak normalizes audio file level.

        @details Finds peak amplitude and scales audio to maximize the peak without clipping.<br>
        Peak normalization (aka volume normalization) is a single pass process.
        Peak normalization does not take into account the perceived loudness of the audio.<br>
        It only ensures that the highest peak reaches the target level.
        Requires an MP3 file.

        @code{.text}
        ffmpeg -hide_banner -i file_path -filter:a volume=adjustmentdB -c:v copy -c:a libmp3lame -b:a bitrate -id3v2_version 3 export_path -y

        -hide_banner; to reduce output clutter
        -i file_path; input file path
        -filter:a volume=adjustmentdB; where adjustment is computed dB value from volume info return and true peak constant
        -c:v copy; to copy embedded art, since no explicit -map_metadata, the default global copy will happen on both streams
        -c:a libmp3lame; to keep same encoding
        -b:a bitrate; where bit rate in bps, not kbps
        -id3v2_version 3; required to properly copy embedded art, known ffmpeg bug
        export_path-y; force an overwrite on the output file if needed
        @endcode

        @param file_path {str} The full file path for mp3 audio file.
        @param show_spinner {bool} Whether to display a progress spinner.

        @exception PathInfoError Indicates directory_processing.path_info function returned None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        txt_filename = inspect.currentframe().f_code.co_name

        try:
            _, input_file_ext = os.path.splitext(file_path)
            if input_file_ext.lower() != MP3_EXT:
                logger.warning(f"{file_path} is not an mp3")
                return

            export_path = directory.path_info(file_path)

            if export_path is None:
                logger.exception(f"PathInfoError with file {file_path} returned None", stack_info=True)
                raise PathInfoError(f"PathInfoError with file {file_path} returned None")
            else:
                directory.make_dir(os.path.dirname(export_path))

            input_path_basename = os.path.basename(file_path)
            input_path_dir = os.path.dirname(file_path)

            beginning_text = f"Beginning peak normalization on: {input_path_basename}"
            source_text = f"Source directory path: {input_path_dir}"
            data.append(beginning_text)
            data.append(source_text)

            # want bitrate so can preserve the quality in exported file
            bitrate = self.get_bit_rate(file_path)
            data.append(f"bit rate: {bitrate}")

            volume_info = self.get_volume_info(file_path)
            # want the floor so don't inadvertently cause clipping (more negative dbs are quieter)
            max_volume = math.floor(volume_info['max_volume'])
            data.append(f"floor max volume: {max_volume:.2f}")

            if max_volume >= 0.0:
                max_text = f"{input_path_basename} has max volume: {max_volume:.2f} dB, peak normalization not needed"
                logger.warning(max_text)
                return
            else:
                data.append(f"max volume: {max_volume:.2f} dB")

            adjustment = 0.0 + float(TP) - float(max_volume)
            clip_amount = float(max_volume) + adjustment

            if clip_amount > 0:
                clip_text = (
                    f"peak normalizing by {TP} minus {max_volume:.2f} equals {adjustment:.2f}; "
                    f"max volume {max_volume} plus {adjustment} clips by {clip_amount} dB in {export_path}"
                )
                logger.warning(clip_text)
                return
            else:
                data.append(f"adjustment: {adjustment:.2f} dB")

            command = [
                "ffmpeg",
                "-hide_banner",
                "-i", file_path,
                "-filter:a", (f"volume={adjustment:.2f}dB"),
                "-c:v", "copy",
                "-c:a", "libmp3lame",
                "-b:a", str(bitrate),
                "-id3v2_version", "3",
                export_path, '-y'
            ]

            text = f"Peak normalizing {input_path_basename}"
            data.append(text)
            data.append(command)

            if show_spinner:
                # _, spinner = subprocess_utils.spinner_subprocess_run(text, command)
                _, spinner = subprocess_utils.spinner_subprocess_run(command, text)
                success_text = f"Successful peak normalization on {input_path_basename} in {spinner.elapsed_time:.2f} secs\n"
            else:
                _ = subprocess_utils.subprocess_run(command)
                success_text = f"Successful peak normalization on {input_path_basename}"

            data.append(success_text)
            directory.create_txt(txt_filename, data)

        except PathInfoError as pi_error:
            raise pi_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} while peak normalizing audio file: {file_path}", stack_info=True)
            raise e_error


    def rms_normalize_file(self, file_path: str, show_spinner: bool = True) -> None:
        '''
        @brief RMS normalizes audio file level.

        @details Finds mean amplitude and scales audio to maximize the mean without clipping.<br>
        RMS normalization (aka volume normalization) is a single pass process.
        RMS normalization adjusts the audio level based on the root mean square (RMS) value,.<br>
        This better represents perceived loudness compared to peak normalization.
        Requires an MP3 file.

        @code{.text}
        ffmpeg -hide_banner -i file_path -filter:a volume=adjustmentdB -c:v copy -c:a libmp3lame -b:a bitrate -id3v2_version 3 export_path -y

        -hide_banner; to reduce output clutter
        -i file_path; input file path
        -filter:a volume=adjustmentdB; where adjustment is computed dB value from volume info return and true peak constant
        -c:v copy; to copy embedded art, since no explicit -map_metadata, the default global copy will happen on both streams
        -c:a libmp3lame; to keep same encoding
        -b:a bitrate; where bit rate in bps, not kbps
        -id3v2_version 3; required to properly copy embedded art, known ffmpeg bug
        export_path-y; force an overwrite on the output file if needed
        @endcode

        @param file_path {str} The full file path for mp3 audio file.
        @param show_spinner {bool} Whether to display a progress spinner.

        @exception PathInfoError Indicates directory_processing.path_info function returned None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        txt_filename = inspect.currentframe().f_code.co_name

        try:
            _, input_file_ext = os.path.splitext(file_path)
            if input_file_ext.lower() != MP3_EXT:
                logger.warning(f"{file_path} is not an mp3")
                return

            export_path = directory.path_info(file_path)

            if export_path is None:
                logger.exception(f"PathInfoError with file {file_path} returned None", stack_info=True)
                raise PathInfoError(f"PathInfoError with file {file_path} returned None")
            else:
                directory.make_dir(os.path.dirname(export_path))

            input_path_basename = os.path.basename(file_path)
            input_path_dir = os.path.dirname(file_path)

            beginning_text = f"Beginning rms normalization on {input_path_basename}"
            source_text = f"Source directory path: {input_path_dir}"
            data.append(beginning_text)
            data.append(source_text)

            # want bitrate so can preserve the quality in exported file
            bitrate = self.get_bit_rate(file_path)
            data.append(f"bit rate: {bitrate}")

            volume_info = self.get_volume_info(file_path)
            # want the floor so don't inadvertently cause clipping (more negative dbs are quieter)
            mean_volume = math.floor(volume_info['mean_volume'])
            max_volume = math.floor(volume_info['max_volume'])
            data.append(f"floor mean volume: {mean_volume:.2f}")
            data.append(f"floor max volume: {max_volume:.2f}")

            if mean_volume >= 0.0:
                mean_text = f"{input_path_basename} has mean volume: {mean_volume:.2f}, rms normalization not needed"
                logger.warning(mean_text)
                return
            else:
                data.append(f"mean volume: {mean_volume:.2f} dB")

            adjustment = float(TP) - float(mean_volume)
            clip_amount = float(max_volume) + adjustment

            if clip_amount > 0:
                clip_text = (
                    f"rms normalizing by {TP} minus {mean_volume:.2f} equals {adjustment:.2f}; "
                    f"max volume {max_volume} plus {adjustment} clips by {clip_amount} dB in {export_path}"
                )
                logger.warning(clip_text)
                return
            else:
                data.append(f"adjustment: {adjustment:.2f} dB")

            command = [
                "ffmpeg",
                "-hide_banner",
                "-i", file_path,
                "-filter:a", (f"volume={adjustment:.2f}dB"),
                "-c:v", "copy",
                "-c:a", "libmp3lame",
                "-b:a", str(bitrate),
                "-id3v2_version", "3",
                export_path, '-y'
            ]

            text = f"rms normalizing {input_path_basename}"
            data.append(text)
            data.append(command)

            if show_spinner:
                _, spinner = subprocess_utils.spinner_subprocess_run(command, text)
                success_text = f"Successful rms normalization on {input_path_basename} in {spinner.elapsed_time:.2f} secs\n"
            else:
                _ = subprocess_utils.subprocess_run(command)
                success_text = f"Successful rms normalization on {input_path_basename}"

            data.append(success_text)
            directory.create_txt(txt_filename, data)

        except PathInfoError as pi_error:
            return pi_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} while rms normalizing audio file: {file_path}", stack_info=True)
            raise e_error
