# google search: Ffmpeg loudnorm filter output parsing python
import subprocess
import json
import platform
from subprocess import CalledProcessError


def loudnorm_two_pass(input_file):
    # first part, getting the information
    # Construct the FFmpeg command
    # since integrated loudness target, max true peak and loudness target range not set, defaults -24, -2 & 7 are used
    command = [
        "ffmpeg",
        "-hide_banner",
        "-i", input_file,
        "-af", "loudnorm=print_format=json",
        "-f", "null",                       # Output to null to avoid creating an actual output file
        "-"                                 # Direct output to stdout for the first pass (stderr for loudnorm stats)
    ]

    # Execute the command and capture stderr
    try:
        process = subprocess.run(
            command,
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


    # 2nd part, get the JSON in the stderr output
    json_start = loudnorm_output.find('{')
    json_end = loudnorm_output.rfind('}')

    if json_start != -1 and json_end != -1:
        json_string = loudnorm_output[json_start: json_end + 1]

        # Parse the JSON string
        try:
            loudnorm_data = json.loads(json_string)
            print("Parsed loudnorm data:")
            print(json.dumps(loudnorm_data, indent=4))  # Pretty print for readability

            # Access specific values, e.g., integrated loudness
            measured_i = loudnorm_data.get("input_i")
            print(f"Measured Integrated Loudness (input_i): {measured_i} LUFS")

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Problematic JSON string: {json_string}")
    else:
        print("Could not find JSON output in loudnorm stderr.")


if __name__ == "__main__":

    if platform.system() == "Windows":
        audio_file = r"C:\Music\Crush\Here\Crush-Live.mp3"
    elif platform.system() == "Linux":
        audio_file = r"/home/gerald/Music/Crush/Here/Crush-Live.mp3"  # Replace with your audio/video file

    loudnorm_two_pass(audio_file)

    '''
    import subprocess
    import json

    input_file = "input.wav"
    output_file = "output_normalized_two_pass.wav"

    # First pass: Analyze and print loudnorm statistics as JSON
    first_pass_command = [
        "ffmpeg",
        "-i", input_file,
        "-af", "loudnorm=print_format=json",
        "-f", "null", "-"  # Output to null, print JSON to stderr
    ]

    try:
        first_pass_result = subprocess.run(
            first_pass_command,
            check=True,
            capture_output=True,
            text=True
        )

        # Extract JSON data from stderr
        json_output_lines = []
        for line in first_pass_result.stderr.splitlines():
            if line.startswith('{') or line.startswith(' ' * 4): # Adjust based on actual JSON output format
                json_output_lines.append(line)

        json_data = json.loads("".join(json_output_lines))

        # Extract measured values for the second pass
        measured_i = json_data['input_i']
        measured_tp = json_data['input_tp']
        measured_lra = json_data['input_lra']
        measured_thresh = json_data['input_thresh']
        offset = json_data['target_offset'] # Or calculate based on measured_i and target_i

        # Second pass: Apply loudnorm with measured values and linear normalization
        second_pass_command = [
            "ffmpeg",
            "-i", input_file,
            "-af", (f"loudnorm=I=-23:LRA=7:TP=-1:"
                    f"measured_I={measured_i}:measured_TP={measured_tp}:"
                    f"measured_LRA={measured_lra}:measured_thresh={measured_thresh}:"
                    f"offset={offset}:linear=true"),
            output_file
        ]

        subprocess.run(second_pass_command, check=True)
        print(f"Audio normalized (two-pass) and saved to {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error during FFmpeg execution: {e}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON output from loudnorm: {e}")
    '''
