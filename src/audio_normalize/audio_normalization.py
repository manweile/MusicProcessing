'''
@file audio_metadata.py
@brief Defines the audio metadata class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# standard modules
import ffmpeg
import gc
import json
import math
import os
import re
import subprocess
from ffmpeg import Error
from json import JSONDecodeError
from pathlib import Path
from subprocess import CalledProcessError

# third party modules
from yaspin import yaspin
from yaspin.spinners import Spinners

# local modules
from src import _AUDIO_EXTS, _AUDIO_TYPES, _EXPORT_TLD, _HOME, _MEDIA
from src.dir_processing import DirectoryProcessing
from src.generated_files import generated_files

gc.enable()

_I = "-16.0"        # ffmpeg loudnorm integrated loudness target RBU 128 default: -24.0 to -23.0, I want louder (less negative)
_LRA = "11.0"       # ffmpeg loudnorm loudness range target RBU 128 default: 7, I want wider range
_TP = "-2.0"        # ffmpeg loudnorm maximum true peak RBU 128 default: -2.0, I will keep that


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


    def ebu_normalize_file(self, file_path):
        '''
        @todo complete add yaspin, update exceptions
        @brief Normalizes audio file level to ebu r128 standard.

        @details see https://k.ylo.ph/2016/04/04/loudnorm.html for an example.

        @param file_path {str} The full file path for audio file.
        @exception CalledProcessError A subprocess error from ffmpeg command execution.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        @exception JSONDecodeError as json decoding error.
        '''

        try:
            # get original sample rate for down sampling
            # @todo research if sample rate is >=192k, do i really need to apply loudnorm?
            sample_rate = self.get_sample_rate(file_path)
            export_path = DirectoryProcessing.path_info(file_path)
            r'''
            loudnorm https://k.ylo.ph/2016/04/04/loudnorm.html
            rbu 128 https://ffmpeg.org/ffmpeg-filters.html#loudnorm
            AES https://www.aes.org/technical/documents/AESTD1004_1_15_10.pdf
            https://wiki.tnonline.net/w/Blog/Audio_normalization_with_FFmpeg

            1st pass to get loudnorm statistics
            -hide_banner to reduce output clutter
            -vn to save cycles by not dealing with video stream
            -af loudnorm audio filter with desired I integrated loudness target, LRA loudness range target, TP max true peak, output in json format
            -f Output to null to avoid creating an actual output file
            Direct output to stdout for the first pass (stderr for loudnorm stats)

            PS C:\Users\gmanw> ffmpeg -hide_banner -i C:\Music\Crush\Here/Crush-Live.mp3 -vn /
            -af loudnorm=I=-16:TP=-2.0:LRA=11:print_format=json /
            -f null NULL

            [Parsed_loudnorm_0 @ 000001b9bb260740] peed=31.3x
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
            '''

            stats_command = [
                "ffmpeg",
                "-hide_banner",
                "-i", file_path,
                "-vn",
                "-af", (f"loudnorm=I={_I}:TP={_TP}:LRA={_LRA}:print_format=json"),
                "-f", "null", "-"
            ]

            stats_process = subprocess.run(
                stats_command,
                check=True,
                capture_output=True,
                text=True               # Decode stdout/stderr as text
            )

            # ffmpeg outputs information to stderr
            stats_output = stats_process.stderr

            json_start = stats_output.find('{')
            json_end = stats_output.rfind('}')

            if json_start != -1 and json_end != -1:
                json_string = stats_output[json_start: json_end + 1]
            else:
                raise Exception(f"Could not find JSON output in ffmpeg loudnorm stats stderr\n{json_string}")

            stats_data = json.loads(json_string)
            print(json.dumps(stats_data, indent=4))  # Pretty print for readability

            # Access specific values, e.g., integrated loudness
            measured_i = stats_data.get("input_i")
            measured_lra = stats_data.get("input_lra")
            measured_tp = stats_data.get("input_tp")
            measured_thresh = stats_data.get("input_thresh")
            offset = stats_data.get("target_offset")

            r'''
            2nd pass to apply loudnorm statistics
            -hide_banner to reduce output clutter
            do not need a -map_metadata 0 by default if flag omitted, metadata is copied globally from first input file
            -id3v2 3 to enforce ID3v2.3 tags, otherwise will default to ID3v2.4 and album art will NOT be copied (it's a known bug)
            -af loudnorm audio filter same I integrated loudness target, LRA loudness range target, TP max true peak,
            and from first pass, measured_I=input_i, measured_LRA=input_lra, measured_TP=input_tp, measured_thresh=input_thresh, offset=target_offset,
            linear=true to normalize by linearly scaling source audio, output in json format
            -ar input file sample_rate, 1st pass loudnorm filter auto up scales to 192 khz, so need to down scale to original
            -y on the output file to force an overwrite if needed

            PS C:\Users\gmanw> ffmpeg -hide_banner -i C:\Music\Crush\Here/Crush-Live.mp3 -id3v2_version 3 /
            -af loudnorm=I=-16:TP=-2.0:LRA=11:measured_I=-16.77:measured_LRA=8.10:measured_TP=-6.66:measured_thresh=-26.99:offset=-0.64:linear=true:print_format=json /
            -ar 44100 D:\MusicProcessing\src\generated_files\Music\Crush\Here\Crush-Live.mp3 -y

            [Parsed_loudnorm_0 @ 0000021b0d796e80] 8KiB time=N/A bitrate=N/A speed=N/A
            {
                    "input_i" : "-16.73",
                    "input_tp" : "-6.73",
                    "input_lra" : "8.00",
                    "input_thresh" : "-26.93",
                    "output_i" : "-15.96",
                    "output_tp" : "-5.96",
                    "output_lra" : "8.10",
                    "output_thresh" : "-26.16",
                    "normalization_type" : "linear",
                    "target_offset" : "-0.04"
            }
            '''

            normalize_command = [
                "ffmpeg",
                "-hide_banner",
                "-i", file_path,
                "-af", (f"loudnorm=I={_I}:TP={_TP}:LRA={_LRA}"
                        f"measured_I={measured_i}:measured_TP={measured_tp}:"
                        f"measured_LRA={measured_lra}:measured_thresh={measured_thresh}:"
                        f"offset={offset}:linear=true"
                        f":print_format=json"
                        ),
                "-ar", sample_rate,
                export_path, "-y"
            ]

            normalize_process = subprocess.run(
                normalize_command,
                check=True,
                capture_output=True,
                text=True
            )
            normalize_output = normalize_process.stderr

            json_start = normalize_output.find('{')
            json_end = normalize_output.rfind('}')

            if json_start != -1 and json_end != -1:
                json_string = normalize_output[json_start: json_end + 1]
            else:
                raise Exception(f"Could not find JSON output in ffmpeg loudnorm normalize stderr\n{json_string}")

            normalize_data = json.loads(json_string)
            print(json.dumps(normalize_data, indent=4))

            normalization_type = normalize_data.get("normalization_type")

            if normalization_type != "linear":
                print(f"ffmpeg used normalization type: {normalization_type}")

        except CalledProcessError as e:
            raise CalledProcessError(f"FFmpeg error {e} Stderr:\n{e.stderr}")
        except Exception as e:
            raise Exception(f"Exception {e} normalizing audio file: {file_path}")
        except JSONDecodeError as e:
            raise JSONDecodeError(f"JSON parsing error: {e} with\n{json_string}")


    def get_bitrate(file_path):
        """
        @brief Retrieves the bitrate of a media file using ffprobe.

        @param file_path (str): The path to the media file.

        @return bit_rate {int} The bitrate in bits per second, or None if not found.
        @exception CalledProcessError A subprocess error from ffprobe command execution.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        @exception JSONDecodeError as json decoding error.
        """

        try:
            bit_rate = None
            command = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_entries', 'format=bit_rate',
                file_path
            ]

            result = subprocess.run(command, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            if 'format' in data and 'bit_rate' in data['format']:
                bit_rate = int(data['format']['bit_rate'])

        except CalledProcessError as e:
            raise CalledProcessError(f"Error {e} executing ffprobe")
        except Exception as e:
            raise Exception(f"Exception {e} normalizing audio file: {file_path}")
        except JSONDecodeError as e:
            raise JSONDecodeError(f"Error {e} decoding JSON output from ffprobe.")

        return bit_rate


    def get_sample_rate(self, file_path):
        '''
        @brief Gets the sample rate from audio file.

        @param file_path {str} The full path to audio file.
        @return sample_rate {str} The sample rate in Hz, otherwise None.
        @exception Error A ffmpeg-python module error.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            sample_rate = None
            probe = ffmpeg.probe(file_path)
            audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)

            if audio_stream and 'sample_rate' in audio_stream:
                sample_rate = audio_stream['sample_rate']

        except Error as e:
            raise Exception(f"An ffmpeg error occurred: {e.stderr.decode()}")
        except Exception as e:
            raise Exception(f"Exception {e} getting sample rate for file {file_path}")

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
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            volumes = dict()

            command = [
                'ffmpeg',
                '-i', file_path,
                '-hide_banner',
                '-filter:a', 'volumedetect',
                '-f', 'null',
                '-'                             # Send output to stdout
            ]

            # Run FFmpeg and capture stderr (where volumedetect output goes)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            # Decode stderr to string and search for volume information
            output_str = stderr.decode('utf-8')

            mean_volume_match = re.search(r'mean_volume: ([-]?\d+\.\d+) dB', output_str)
            max_volume_match = re.search(r'max_volume: ([-]?\d+\.\d+) dB', output_str)

            if mean_volume_match and max_volume_match:
                mean_volume = float(mean_volume_match.group(1))
                max_volume = float(max_volume_match.group(1))
                volumes['mean_volume'] = mean_volume
                volumes['max_volume'] = max_volume

        except Exception as e:
            raise Exception(f"Exception {e} getting volume for file {file_path}")

        return volumes


    def peak_normalize_file(self, file_path):
        '''
        @todo use DirectoryProcessing.path_info()
        @brief Peak normalizes audio file level.

        @details Automatically finds peak amplitude ands scales entire audio to maximize peak without clipping.
        @details Audio file must be mp3 format.

        @param file_path {str} The full file path for audio file.
        @exception CalledProcessError A subprocess error from ffmpeg-normalize command execution.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            export_dir = None
            export_name = None
            export_path = None

            input_path = Path(file_path)

            input_ext = input_path.suffix
            if input_ext.lower() != _AUDIO_EXTS[0]:
                raise Exception(f"File {input_path} is not an {_AUDIO_TYPES[0]}")

            # get the full parent w/o filename so I can start removing unnecessary path components
            input_path_parent = input_path.parent

            # remove the anchor (ie. / or H:\), have no use for it
            input_path_parts = input_path_parent.parts[1:]

            # platform module doesn't help us here, ubuntu has differing paths for hdd (home) vs usb (media), unlike windows
            # to keep the artist dir and album dir we need to look at the 1st element of our anchor trimmed path parts
            if input_path_parts[0] == _MEDIA:
                # Ubuntu usb is going to have <mount point>/<usr>/<drive label>/<tld>/<artist dir>/<album dir>
                # so 6 elements, we don't want elements 0 to 3: 'media', 'gerald', 'Lexar', 'Music'
                input_path_components = input_path_parts[4:]
            elif input_path_parts[0] == _HOME:
                # Ubuntu hdd is going to have <mount point>/<usr>/<tld>/<artist dir>/<album dir>
                # so 5 elements, we don't want  elements 0 to 2: 'home', 'gerald', 'Music'
                input_path_components = input_path_parts[3:]
            else:
                # Windows is going to have <tld>/<artist dir>/<album dir>
                # so 3 elements, we don't want element 1: 'Music'
                input_path_components = input_path_parts[1:]

            # using fixed storage path because will always know project structure
            export_dir = os.path.join(generated_files, _EXPORT_TLD)

            for component in input_path_components:
                export_dir = os.path.join(export_dir, component)

            # directory is already extant if we are processing multiple songs for the same artist & album
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)

            # get mp3 audio format & extension from package constants
            export_format = _AUDIO_TYPES[0]
            export_ext = _AUDIO_EXTS[0]

            input_name = input_path.stem

            export_name = input_name + export_ext
            export_path = os.path.join(export_dir, export_name)

            input_format = os.path.splitext(file_path)[1].lower()[1:]
            input_path_stem = os.path.splitext(os.path.basename(file_path))[0]
            input_path_dir = os.path.dirname(file_path)
            print(f"Beginning peak normalization on {input_path_stem} from {input_format} to {export_format}")
            print(f"Source directory path: {input_path_dir}")

            # get the input file info - want bitrate so can preserve the quality in exported file
            media_info = self.get_media_info(file_path)
            # media_info = self.get_media_info(input_path)
            bitrate = media_info['bit_rate']

            volume_info = self.get_volume_info(file_path)
            # want the floor so don't inadvertently cause clipping (more negative dbs are quieter)
            max_volume = math.floor(volume_info['max_volume'])

            if max_volume <= -1:
                target_level = -1 - max_volume
            elif max_volume > -1 and max_volume <= 0:
                print(f"{input_path_stem} has max volume: {max_volume}, normalization not needed")
                return
            elif max_volume > 0:
                print(f"{input_path_stem} has max volume: {max_volume}, process with Goldwave or Audacity")
                return

            # @todo switch to ffmpeg
            # ffmpeg -i C:\Music\Crush\Here\Crush-Live.mp3 -filter:a "volume=6dB" -c:v copy -ab 128k -map_metadata 0 -id3v2_version 3 "D:\MusicProcessing\src\generated_files\Music\Crush\Here\Peak-Crush-live.mp3" -y
            # use target_level in volume
            # use bit_rate in -ab

            # working ffmpeg-normalize ubuntu/windows cli:
            # ffmpeg-normalize ~/ProcessedMusic/Crush/Here/Crush-Live.mp3 -c:a libmp3lame -b:a 128k --extra-output-options "-id3v2_version 3" --normalization-type peak --target-level 0 -f -o ~/MusicProcessing/src/generated_files/Music/Crush/Here/Crush-Live.mp3
            # ffmpeg-normalize F:\ProcessedMusic\Crush\Here\Crush-Live.mp3 -c:a libmp3lame -b:a 128k --extra-output-options "-id3v2_version 3" --normalization-type peak --target-level 0 -f -o D:\MusicProcessing\src\generated_files\Music\Crush\Here\Crush-Live.mp3
            # album art and tags are preserved!!!
            # the extra output option setting the ID3v2.3 is necessary, else can't preserve embedded art
            command = [
                "ffmpeg-normalize",
                file_path,
                "-c:a", "libmp3lame",
                "-b:a", bitrate,
                "--extra-output-options", r"-id3v2_version 3",
                "--normalization-type", "peak",
                "--target-level", str(target_level),
                "-f", "-o", export_path
            ]

            print(f"Beginning peak normalization on {input_path} using ffmpeg-normalize.")
            text = f"Normalizing {input_path.stem}"
            with yaspin(Spinners.dots, text=text, timer=True) as sp:
                with open(os.devnull, 'rb') as devnull:
                    p = subprocess.Popen(
                        command,
                        stdin=devnull,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )

                while True:
                    line = p.stderr.readline()
                    if not line:
                        break

                p_out, p_err = p.communicate()

            print(f"Successful normalization on {input_path.stem} in {sp.elapsed_time} secs\r\n")
        except CalledProcessError:
            raise Exception(
                f"ffmpeg-normalize returned error code: {p.returncode}\n\n for command line: {command}\n\n Output from ffmpeg-normalize: {p_err.decode(errors='ignore')}")
        except Exception as e:
            raise Exception(f"Exception {e} normalizing audio file: {file_path}")


    def peak_normalize_walk(self, file_path):
        '''
        @todo generalize for peak, ebu, and rms normalization
        @brief Peak normalizes mp3 audio files in under starting top level directory.

        @details Automatically finds peak amplitude ands scales entire audio to maximize peak without clipping.

        @param file_path {str} The starting point of the directory walk.
        @param file_pattern {str} Optional, the audio file pattern we want to get tags from.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        input_file_ext = None

        try:
            input_path = Path(file_path)

            for dir_path, _, file_names in os.walk(input_path):
                for file in file_names:
                    _, input_file_ext = os.path.splitext(file)

                    # file is not mp3, carry on to next file
                    if input_file_ext.lower() != _AUDIO_EXTS[0]:
                        continue

                    input_file_path = os.path.join(dir_path, file)
                    self.peak_normalize_file(input_file_path)

        except Exception as e:
            raise Exception(f"Exception {e} walking {file_path} to normalize audio files")
