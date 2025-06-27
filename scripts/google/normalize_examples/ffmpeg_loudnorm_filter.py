# google search: Ffmpeg loudnorm filter output parsing python


import subprocess
import json

input_file = "input.wav"  # Replace with your input audio file

# Construct the FFmpeg command
command = [
    "ffmpeg",
    "-i", input_file,
    "-af", "loudnorm=print_format=json",
    "-f", "null",  # Output to null to avoid creating an actual output file
    "-"  # Direct output to stdout for the first pass (stderr for loudnorm stats)
]

# Execute the command and capture stderr
try:
    process = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True  # Decode stdout/stderr as text
    )
    loudnorm_output = process.stderr
except subprocess.CalledProcessError as e:
    print(f"FFmpeg error: {e}")
    print(f"Stderr: {e.stderr}")
    exit()


# 2nd part
# Find the JSON part in the stderr output
json_start = loudnorm_output.find('{')
json_end = loudnorm_output.rfind('}')

if json_start != -1 and json_end != -1:
    json_string = loudnorm_output[json_start : json_end + 1]

    # Parse the JSON string
    try:
        loudnorm_data = json.loads(json_string)
        print("Parsed loudnorm data:")
        print(json.dumps(loudnorm_data, indent=4)) # Pretty print for readability

        # Access specific values, e.g., integrated loudness
        measured_i = loudnorm_data.get("input_i")
        print(f"Measured Integrated Loudness (input_i): {measured_i} LUFS")

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Problematic JSON string: {json_string}")
else:
    print("Could not find JSON output in loudnorm stderr.")
