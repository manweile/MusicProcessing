'''
@file audio_metadata.py
@brief Defines the audio metadata class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import gc
import inspect
import json
import logging
import math
import os
import re
from json import JSONDecodeError
from pathlib import Path

# local modules
from src import AUDIO_EXTS, AUDIO_TYPES
from src import ERROR_LOG_FORMAT, LOG_DIR, LOG_EXT, UTF8          # logging constants
from src.generated_files import GENERATED_FILES
from src.errors import JSONOutputError
from src.errors import PathInfoError
from src.dir_processing import DirectoryProcessing
from src.subprocess_utils import SubprocessUtilities

gc.enable()

directory = DirectoryProcessing()
subprocess_utils = SubprocessUtilities()

# Configure logging
basename = os.path.basename(__file__)
stem = os.path.splitext(basename)[0]
file = stem + LOG_EXT
log_filename = os.path.join(GENERATED_FILES, LOG_DIR, file)
# override the default logging level WARN to lowest level so we can log all levels
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=ERROR_LOG_FORMAT, filemode="a", encoding=UTF8)

# create logger for module and restrict to module
# use raise in exception handling if we need send something inter-module
logger = logging.getLogger(__name__)
logger.propagate = False

r'''
AES https://www.aes.org/technical/documents/AESTD1004_1_15_10.pdf
ffmpeg loudnorm integrated loudness target EBU R128 default: -24.0,
I want -16, which is the AES recommendation for streamed files
ffmpeg loudnorm loudness range target EBU R128 default: 7,
I want wider range because most of my collection has a wider range
ffmpeg loudnorm maximum true peak EBU R128 default: -2.0,
I will keep that cause I want the extra headroom space vs -1.0 or 0.0
'''
ILT = "-16.0"
LRA = "11.0"
TP = "-2.0"


class AudioNormalization():
    '''
    @brief Defines the base normalization processing used by project.
    '''

    def __init__(self):
        '''
        @brief Initializes the AudioNormalization class.

        @details A basic class implementation with no instantiation parameters.

        @return AudioNormalization {instance} An instance of the class.
        '''

        pass


    def __loudnorm_json_parse(self, input_process):
        '''
        @brief Parse json element out of ffmpeg loudnorm subprocess stderr output.

        @details The subprocess stderr is expected to have a single json element.
        Expecting this in input_process.stderr, from a ffmpeg loudnorn run
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
        @param input_process {CompletedProcess} A completed subprocess object.
        @return input_data {dict} FFmpeg loudnorm statistics.
        Key                         |Value
        ----------------------------|----------------------------------------------------------------
        input_i {str}               | input integrated loudness {str} (numeric)
        input_tp {str}              | input maximum true peak {str} (numeric)
        input_lra {str}             | input loudness range target {str} (numeric)
        input_thresh {str}          | input threshold {str} (numeric)
        output_i{str}               | output integrated loudness {str} (numeric)
        output_tp {str}             | output maximum true peak {str} (numeric)
        output_lra {str}            | output loudness range target {str} (numeric)
        output_thresh {str}         | output threshold {str} (numeric)
        normalization_type {str}    | scaling type to apply {str} (alphabetic)
        target_offset {str}         | offset gain applied before true peak limiter {str} (numeric)
        @exception JSONDecodeError A json decoding error occurred.
        @exception JSONOutputError Indicates error occurred finding json output.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            input_data = None
            json_input = input_process.stderr

            json_start = json_input.find('{')
            json_end = json_input.rfind('}')

            if json_start != -1 and json_end != -1:
                json_string = json_input[json_start: json_end + 1]
            else:
                logger.error(f"JSONOutputError could not find JSON output in subprocess stderr\n{json_string}", exc_info=True)
                raise JSONOutputError(f"JSONOutputError could not find JSON output in subprocess stderr\n{json_string}")

            input_data = json.loads(json_string)

        except JSONDecodeError as jd_error:
            logger.error(f"JSONDecodeError parsing \n{json_string}", exc_info=True)
            raise jd_error
        except JSONOutputError as jo_error:
            raise jo_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} parsing ffmpeg loudnorm subprocess stderr", stack_info=True)
            raise e_error
        else:
            return input_data


    def ebu_normalize_file(self, file_path):
        '''
        @brief Normalizes audio file level to ebu r128 standard.

        @details See https://k.ylo.ph/2016/04/04/loudnorm.html for algorithm & example.
        @details See https://wiki.tnonline.net/w/Blog/Audio_normalization_with_FFmpeg for example
        @details See https://ffmpeg.org/ffmpeg-filters.html#loudnorm for documentation.
        @details Audio file must be mp3 format, and already processed by convert_file function.

        @param file_path {str} The full file path for mp3 audio file.
        @exception PathInfoError Indicates directory_processing.path_info function returned None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        txt_filename = inspect.currentframe().f_code.co_name

        try:
            _, input_file_ext = os.path.splitext(file_path)
            if input_file_ext.lower() != AUDIO_EXTS[0]:
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
            data.append[beginning_text]
            data.append(source_text)

            # get original sample rate for down sampling
            sample_rate = self.get_sample_rate(file_path)
            data.append(f"Source sample rate: {sample_rate} hz")

            '''
            1st pass to get loudnorm statistics
            -hide_banner to reduce output clutter
            -vn to save cycles by not dealing with video stream
            -af loudnorm audio filter with my desired I integrated loudness target, LRA loudness range target, TP max true peak, output in json format
            -f Output to null to avoid creating an actual output file
            '''

            stats_command = [
                "ffmpeg",
                "-hide_banner",
                "-i", file_path,
                "-vn",
                "-af", (f"loudnorm=I={ILT}:TP={TP}:LRA={LRA}:print_format=json"),
                "-f", "null", "-"
            ]

            text = "Getting normalizing stats"
            data.append(text)
            data.append(stats_command)
            stats_process, stats_spinner = subprocess_utils.spinner_subprocess_run(text, stats_command)

            pre_text = "Pre normalization stats:"
            data.append(pre_text)
            stats_data = self.__loudnorm_json_parse(stats_process)
            data.append(json.dumps(stats_data, indent=4))
            stats_time = stats_spinner.elapsed_time
            data.append(f"Analyzed loudnorm stats in {stats_time:.2f} secs")

            # Access the loudnorm results needed for 2nd pass
            measured_i = stats_data.get("input_i")
            measured_lra = stats_data.get("input_lra")
            measured_tp = stats_data.get("input_tp")
            measured_thresh = stats_data.get("input_thresh")
            offset = stats_data.get("target_offset")

            # 2nd pass to apply loudnorm statistics
            # -hide_banner to reduce output clutter
            # do not need a -map_metadata 0 by default if flag omitted, metadata is copied globally from first input file
            # -id3v2 3 to enforce ID3v2.3 tags, otherwise will default to ID3v2.4 and album art will NOT be copied (it's a known bug)
            # -af loudnorm audio filter needs same I integrated loudness target, LRA loudness range target, TP max true peak,
            # and from first pass, measured_I=input_i, measured_LRA=input_lra, measured_TP=input_tp, measured_thresh=input_thresh, offset=target_offset,
            # linear=true to normalize by linearly scaling source audio, output in json format
            # -ar input file sample_rate, 1st pass loudnorm filter auto up scales to 192 khz, so need to down scale to original
            # -y on the output file to force an overwrite if needed

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
                "-ar", str(sample_rate),
                export_path, "-y"
            ]

            text = "Normalizing audio"
            data.append(text)
            data.append(normalize_command)
            normalize_process, normalize_spinner = subprocess_utils.spinner_subprocess_run(text, normalize_command)

            post_text = "Post normalization stats:"
            data.append(post_text)
            normalize_data = self.__loudnorm_json_parse(normalize_process)
            data.append(json.dumps(normalize_data, indent=4))
            normalization_time = normalize_spinner.elapsed_time
            data.append(f"Applied normalization in {normalization_time:.2f} secs")

            total_time = normalize_spinner.elapsed_time + stats_time

            normalization_type = normalize_data.get("normalization_type")
            if normalization_type != "linear":
                results_text = f"FFMPEG used {normalization_type} normalization on {input_path_basename} in total time {total_time:.2f} secs\n "
            else:
                results_text = f"Successful linear normalization on {input_path_basename} in total time {total_time:.2f} secs\n"

            data.append(results_text)
            directory.create_txt(txt_filename, data)

        except PathInfoError as pi_error:
            raise pi_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} while ebu normalizing audio file: {file_path}", stack_info=True)
            raise e_error


    def get_bit_rate(self, file_path):
        '''
        @brief Retrieves the bitrate of a media file using ffprobe.

        @param file_path (str): The path to the media file.
        @return bit_rate {int} The bitrate in bits per second, or None if not found.
        @exception JSONDecodeError A json decoding error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            bit_rate = None

            # -v quiet suppress output clutter (-hide_banner works too)
            # -print_format json for json output
            # -show_entries format=bit_rate gets just the bit rate
            command = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_entries', 'format=bit_rate',
                file_path
            ]

            result = subprocess_utils.subprocess_run(command)

            # unlike ffmpeg, ffprobe does use stdout
            data = json.loads(result.stdout)

            if 'format' in data and 'bit_rate' in data['format']:
                bit_rate = int(data['format']['bit_rate'])

        except JSONDecodeError as jd_error:
            logger.error("JSONDecodeError decoding JSON output from ffprobe", exc_info=True)
            raise jd_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} normalizing audio file: {file_path}", stack_info=True)
            raise e_error
        else:
            return bit_rate


    def get_sample_rate(self, file_path):
        '''
        @brief Gets the sample rate from audio file.

        @param file_path {str} The full path to audio file.
        @return sample_rate {int} The sample rate in Hz, otherwise None.
        @exception IndexError An index error finding audio stream or sample rate information.
        @exception JSONDecodeError A json decoding error occurred.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            sample_rate = None

            # -v error or -hide_banner, either work to reduce clutter
            # -select_streams a:0 only want audio stream
            # -show_entries stream=sample_rate we only get the one entry specified
            # -of json to output in json format
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


    def get_volume_info(self, file_path):
        '''
        @brief Gets mean and max volume from audio file using ffmpeg.

        @details
        @param file_path {str} The full path to audio file.
        @return volumes {dict} The mean and max volumes of audio file in decibels relative to max PCM value.
        Key                 |Value
        --------------------|----------------------------------------
        mean_value {str}    |the root mean square volume {float}
        max_volume {str}    |the per-sample maximum volume {float}
        @exception re.error An error occurred processing a regular expression with re module.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            volumes = dict()

            # -hide_banner to reduce output clutter
            # -filter:a volumedetect so get volume stats on audio stream
            # -f null - send output to stdout
            command = [
                'ffmpeg', '-hide_banner',
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


    def normalize_walk(self, tld_path, norm_type):
        '''
        @brief Normalizes all audio files in specified top level directory per input normalization type.

        @param tld_path {str} The top level directory path that contains all the music files.
        @param norm_type {str} The type of normalization to perform.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            input_file_ext = None
            input_path = Path(tld_path)

            for dir_path, _, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    # file is not mp3, carry on to next file
                    if input_file_ext.lower() != AUDIO_EXTS[0]:
                        logger.info(f"{file} is not an mp3, continuing to next file")
                        continue

                    input_file_path = os.path.join(dir_path, file)

                    if norm_type == "ebu":
                        self.ebu_normalize_file(input_file_path)
                    elif norm_type == "peak":
                        self.peak_normalize_file(input_file_path)
                    elif norm_type == "rms":
                        self.rms_normalize_file(input_file_path)

        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} on {input_file_path} while walking {tld_path} to {norm_type} normalize audio files", stack_info=True)
            raise e_error


    def peak_normalize_file(self, file_path):
        '''
        @brief Peak normalizes audio file level.

        @details Automatically finds peak amplitude ands scales entire audio to maximize peak without clipping.
        @details Audio file must be mp3 format, and already processed by convert_file function.

        @param file_path {str} The full file path for mp3 audio file.
        @exception PathInfoError Indicates directory_processing.path_info function returned None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        txt_filename = inspect.currentframe().f_code.co_name

        try:
            export_path = directory.path_info(file_path)

            if export_path is None:
                logger.exception(f"PathInfoError with file {file_path} returned None", stack_info=True)
                raise PathInfoError(f"PathInfoError with file {file_path} returned None")
            else:
                directory.make_dir(os.path.dirname(export_path))

            export_format = AUDIO_TYPES[0]
            input_format = os.path.splitext(file_path)[1].lower()[1:]
            input_path_stem = os.path.splitext(os.path.basename(file_path))[0]
            input_path_dir = os.path.dirname(file_path)

            beginning_text = f"Beginning peak normalization on {input_path_stem} from {input_format} to {export_format}"
            source_text = f"Source directory path: {input_path_dir}"
            data.append(beginning_text)
            data.append(source_text)

            # want bitrate so can preserve the quality in exported file
            bitrate = self.get_bit_rate(file_path)
            data.append(f"bit rate: {bitrate}")

            volume_info = self.get_volume_info(file_path)
            # want the floor so don't inadvertently cause clipping (more negative dbs are quieter)
            max_volume = math.floor(volume_info['max_volume'])

            if max_volume == 0.0:
                unnecessary_text = print(f"{input_path_stem} has max volume: {max_volume:.2f} dB, peak normalization not needed")
                data.append(unnecessary_text)
                return
            else:
                data.append(f"max volume: {max_volume:.2f} dB")

            adjustment = 0 + float(TP) - float(max_volume)
            clip_amount = max_volume + adjustment

            if clip_amount > 0:
                peak_text = print(f"peak normalizing by {TP} minus {max_volume:.2f} dB equaling {adjustment:.2f} dB will result in clipping level: {clip_amount:.2f} dB in {export_path}")
                data.append(peak_text)
                return
            else:
                data.append(f"adjustment: {adjustment:.2f} dB")

            # -hide_banner to reduce output clutter
            # -filter:a volume=6dB where dB is the adjustment value from volume stats return
            # -c:v copy to copy embedded art
            # since no explicit -map_metadata, the default global copy will happen,on both streams
            # -c:a libmp3lame to keep same encoding
            # -b:a 128k where bit rate in bps, not kbps
            # -id3v2_version 3 required to properly copy embedded art, known ffmpeg bug
            # -y on the output file to force an overwrite if needed
            command = [
                "ffmpeg", "-hide_banner",
                "-i", file_path,
                "-filter:a", (f"volume={adjustment:.2f}dB"),
                "-c:v", "copy",
                "-c:a", "libmp3lame",
                "-b:a", str(bitrate),
                "-id3v2_version", "3",
                export_path, '-y'
            ]

            text = f"Peak normalizing {input_path_stem}"
            data.append(text)
            data.append(command)

            _, spinner = subprocess_utils.spinner_subprocess_run(text, command)

            success_text = f"Successful peak normalization on {input_path_stem} in {spinner.elapsed_time:.2f} secs\n"
            data.append(success_text)
            directory.create_txt(txt_filename, data)

        except PathInfoError as pi_error:
            raise pi_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} while peak normalizing audio file: {file_path}", stack_info=True)
            raise e_error


    def rms_normalize_file(self, file_path):
        '''
        @brief RMS normalizes audio file level.

        @details Automatically finds mean amplitude ands scales entire audio to maximize mean without clipping.
        @details Audio file must be mp3 format, and already processed by convert_file function.

        @param file_path {str} The full file path for mp3 audio file.
        @exception PathInfoError Indicates directory_processing.path_info function returned None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        data = []
        txt_filename = inspect.currentframe().f_code.co_name

        try:
            export_path = directory.path_info(file_path)

            if export_path is None:
                logger.exception(f"PathInfoError with file {file_path} returned None", stack_info=True)
                raise PathInfoError(f"PathInfoError with file {file_path} returned None")
            else:
                directory.make_dir(os.path.dirname(export_path))

            export_format = AUDIO_TYPES[0]
            input_format = os.path.splitext(file_path)[1].lower()[1:]
            input_path_stem = os.path.splitext(os.path.basename(file_path))[0]
            input_path_dir = os.path.dirname(file_path)

            beginning_text = f"Beginning rms normalization on {input_path_stem} from {input_format} to {export_format}"
            source_text = f"Source directory path: {input_path_dir}"
            data.append[beginning_text]
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

            if max_volume == 0.0:
                unnecessary_text = print(f"{input_path_stem} has max volume: {max_volume:.2f}, rms normalization not needed")
                data.append(unnecessary_text)
                return
            else:
                data.append(f"max volume: {max_volume:.2f} dB")

            adjustment = float(TP) - float(mean_volume)
            clip_amount = max_volume + adjustment

            if clip_amount > 0:
                peak_text = print(f"rms normalizing by {TP} minus {mean_volume:.2f} equaling {adjustment:.2f} will result in clipping amount: {clip_amount} dB in {export_path}")
                data.append(peak_text)
                return
            else:
                data.append(f"adjustment: {adjustment:.2f} dB")

            # -hide_banner to reduce output clutter
            # -filter:a volume=6dB where dB is the adjustment value from volume stats return
            # -c:v copy to copy embedded art
            # since no explicit -map_metadata, the default global copy will happen,on both streams
            # -c:a libmp3lame to keep same encoding
            # -b:a 128k where bit rate in bps, not kbps
            # -id3v2_version 3 required to properly copy embedded art, known ffmpeg bug
            # -y on the output file to force an overwrite if needed
            command = [
                "ffmpeg", "-hide_banner",
                "-i", file_path,
                "-filter:a", (f"volume={adjustment:.2f}dB"),
                "-c:v", "copy",
                "-c:a", "libmp3lame",
                "-b:a", str(bitrate),
                "-id3v2_version", "3",
                export_path, '-y'
            ]

            text = f"rms normalizing {input_path_stem}"
            data.append(text)
            data.append(command)

            _, spinner = subprocess_utils.spinner_subprocess_run(text, command)

            success_text = f"Successful rms normalization on {input_path_stem} in {spinner.elapsed_time:.2f} secs\n"
            data.append(success_text)
            directory.create_txt(txt_filename, data)

        except PathInfoError as pi_error:
            return pi_error
        except Exception as e_error:
            logger.exception(f"Exception {type(e_error).__name__} while rms normalizing audio file: {file_path}", stack_info=True)
            raise e_error
