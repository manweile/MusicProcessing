import json
import platform
import subprocess
from json import JSONDecodeError
from subprocess import CalledProcessError

_I = "-16.0"        # ffmpeg loudnorm integrated loudness target RBU 128 default: -24.0 to -23.0, I want louder (less negative)
_LRA = "11.0"       # ffmpeg loudnorm loudness range target RBU 128 default: 7, I want wider range
_TP = "-2.0"        # ffmpeg loudnorm maximum true peak RBU 128 default: -2.0, I will keep that


def normalize(in_file):
    try:
        command = [
            "ffmpeg",
            "-hide_banner",
            "-i", in_file,
            "-af", (f"loudnorm=I{_I}:TP={_TP}:LRA={_LRA}:print_format=json"),
            "-f", "null", "-"
        ]

        stats_pass = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True               # Decode stdout/stderr as text
        )

        loudnorm_output = stats_pass.stderr

        json_start = loudnorm_output.find('{')
        json_end = loudnorm_output.rfind('}')

        if json_start != -1 and json_end != -1:
            json_string = loudnorm_output[json_start: json_end + 1]
        else:
            raise Exception(f"Could not find JSON output in loudnorm stderr\n{json_string}")

    except CalledProcessError as e:
        raise CalledProcessError(f"FFmpeg error {e} Stderr: {e.stderr}")
    except JSONDecodeError as e:
        raise JSONDecodeError(f"JSON parsing error: {e} with {json_string}")
    except Exception as e:
        raise Exception(f"Exception {e} while getting loudnorm stats from {in_file}")


if __name__ == "__main__":

    if platform.system() == "Windows":
        in_file = r"C:\Music\Crush\Here\Crush-Live.mp3"
        out_file = r"C:\MusicProcessing\src\generated_files\Music\Crush\Here\RBU-Crush-Live.mp3"
    elif platform.system() == "Linux":
        in_file = r"/home/gerald/Music/Crush/Here/Crush-Live.mp3"
        out_file = r"/home/gerald/MusicProcessing/src/generated_files/Music/Crush/Here/RBU-Crush-Live.mp3"
