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
import os
import re
import subprocess
from json import JSONDecodeError
from pathlib import Path
from subprocess import CalledProcessError

# third party modules
# from pydub import AudioSegment
# from pydub.utils import mediainfo
from yaspin import yaspin
from yaspin.spinners import Spinners

# local modules
from src import _AUDIO_EXTS, _AUDIO_TYPES, _EXPORT_TLD, _HOME, _MEDIA
from src.generated_files import generated_files

gc.enable()

_I = "-16.0"        # ffmpeg loudnorm integrated loudness target RBU 128 default: -24.0 to -23.0, I want louder (less negative)
_LRA = "11.0"       # ffmpeg loudnorm loudness range target RBU 128 default: 7, I want wider range
_TP = "-2.0"        # ffmpeg loudnorm maximum true peak RBU 128 default: -2.0, I will keep that


class AudioNormalization():
    '''
    @brief Defines the base metadata processing used by project.
    '''

    def __init__(self):
        '''
        @brief Initializes the AudioMetadata class.

        @details A basic class implementation with no instantiation parameters.

        @return AudioNormalization {instance} An instance of the class.
        '''

        pass


    def get_sample_rate(self, file_path):
        '''
        @brief Gets the sample rate from audio file.

        @param file_path {str} The full path to audio file.
        @return sample_rate {str} The sample rate in Hz, otherwise None.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            sample_rate = None
            probe = ffmpeg.probe(file_path)
            audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)

            if audio_stream and 'sample_rate' in audio_stream:
                sample_rate = audio_stream['sample_rate']

        except ffmpeg.Error as e:
            raise Exception(f"An ffmpeg error occurred: {e.stderr.decode()}")
        except Exception as e:
            raise Exception(f"Exception {e} getting sample rate for file {file_path}")

        return sample_rate


    def get_volume_info(self, file_path):
        '''
        @brief Gets mean and max volume from audio file using ffmpeg.

        @param file_path {str} The full path to audio file.
        @return volumes {dict} The mean and max
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


    def ebu_normalize_file(self, file_path):
        '''
        @todo complete
        @brief Normalizes audio file level to ebu r128 standard.

        @details see https://k.ylo.ph/2016/04/04/loudnorm.html for an example.

        @param file_path {str} The full file path for audio file.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        try:
            # get original sample rate for down sampling
            # @todo research if sample rate is >=192k, do i really need to apply loudnorm?
            sample_rate = self.get_sample_rate(file_path)

            r'''
            loudnorm https://k.ylo.ph/2016/04/04/loudnorm.html
            rbu 128 https://ffmpeg.org/ffmpeg-filters.html#loudnorm
            AES https://www.aes.org/technical/documents/AESTD1004_1_15_10.pdf
            https://wiki.tnonline.net/w/Blog/Audio_normalization_with_FFmpeg

            1st pass to get loudnorm statistics
            Output to null to avoid creating an actual output file
            Direct output to stdout for the first pass (stderr for loudnorm stats)

            ffmpeg -hide_banner -i /home/gerald/Music/Crush/Here/Crush-Live.mp3 \
            -af loudnorm=I=-16:TP=-2.0:LRA=11:print_format=json \
            -f null -

            {
                    "input_i" : "-27.61",
                    "input_tp" : "-4.47",
                    "input_lra" : "18.06",
                    "input_thresh" : "-39.20",
                    "output_i" : "-16.58",
                    "output_tp" : "-1.50",
                    "output_lra" : "14.78",
                    "output_thresh" : "-27.71",
                    "normalization_type" : "dynamic",
                    "target_offset" : "0.58"
            }
            '''
            loudnorm_stats = "loudnorm=I=" + _I + ":TP=" + _TP + ":LRA=" + _LRA + ":print_format=json"
            first_command = [
                "ffmpeg",
                "-hide_banner",
                "-i", file_path,
                "-af",
                loudnorm_stats,
                "-f", "null", "-"
            ]

            process = subprocess.run(
                first_command,
                check=True,
                capture_output=True,
                text=True               # Decode stdout/stderr as text
            )
            # ffmpeg outputs information to stderr
            loudnorm_output = process.stderr
        except CalledProcessError as e:
            raise CalledProcessError(f"FFmpeg error {e} Stderr: {e.stderr}")
        except Exception as e:
            raise Exception(f"Exception {e} getting loudnorm filter")

        try:
            json_start = loudnorm_output.find('{')
            json_end = loudnorm_output.rfind('}')

            if json_start != -1 and json_end != -1:
                json_string = loudnorm_output[json_start: json_end + 1]
            else:
                raise Exception(f"Could not find JSON output in loudnorm stderr\n{json_string}")

            loudnorm_data = json.loads(json_string)
            print(json.dumps(loudnorm_data, indent=4))  # Pretty print for readability

            # Access specific values, e.g., integrated loudness
            measured_i = loudnorm_data.get("input_i")
            measured_lra = loudnorm_data.get("input_lra")
            measured_tp = loudnorm_data.get("input_tp")
            measured_thresh = loudnorm_data.get("input_thresh")
            offset = loudnorm_data.get("target_offset")

            loudnorm_apply = loudnorm_stats +
            second_pass = [
                "ffmpeg",
                "-hide_banner",
                "-i", file_path,
                "-af", loudnorm_apply,
                "-ar", sample_rate,
                export_path
            ]

            # 2nd pass to apply loudnorm statistics
            # ffmpeg
            # -i in.wav
            # -af loudnorm=I=-16:TP=-2.0:LRA=11             # needs to be same as 1st pass
            #   :measured_I=-27.61                          # from 1st pass input_i
            #   :measured_LRA=18.06                         # from 1st pass input_lra
            #   :measured_TP=-4.47                          # from 1st pass input_tp
            #   :measured_thresh=-39.20                     # from 1st pass input_thresh
            #   :offset=0.58                                # from 1st pass target_offset
            #   :linear=true
            #   :print_format=summary                       # consider json, like 1st pass
            # -ar 48k out.wav                               # necessary to down sample back to original because loudnorm auto up samples to 192k

        except JSONDecodeError as e:
            raise JSONDecodeError(f"JSON parsing error: {e} with {json_string}")
        except Exception as e:
            raise Exception(f"Exception {e} normalizing audio file: {file_path}")


    def peak_normalize_file(self, file_path):
        '''
        @brief Peak normalizes audio file level.

        @details Automatically finds peak amplitude ands scales entire audio to maximize peak without clipping.
        @details Audio file must be mp3 format.

        @param file_path {str} The full file path for audio file.
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

            export_name = input_path.name
            export_path = os.path.join(export_dir, export_name)

            # get the input file info - want bitrate so can preserve the quality in exported file
            media_info = self.get_media_info(input_path)
            bitrate = media_info['bit_rate']

            # @todo research setting for headroom and re-write
            volume_info = self.get_volume_info(input_path)
            max_volume = volume_info['max_volume']

            if max_volume <= -1:
                target_level = -1 - max_volume
            else:
                target_level = -1

            # working ubuntu/windows cli:
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
        except subprocess.CalledProcessError:
            raise Exception(
                f"ffmpeg-normalize returned error code: {p.returncode}\n\n for command line: {command}\n\n Output from ffmpeg-normalize: {p_err.decode(errors='ignore')}")
        except Exception as e:
            raise Exception(f"Exception {e} normalizing audio file: {file_path}")


    # @todo generalize for peak, rbu, and rms normalization
    def peak_normalize_walk(self, file_path):
        '''
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
