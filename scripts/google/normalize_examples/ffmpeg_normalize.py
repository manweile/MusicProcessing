import ffmpeg
import subprocess

input_file = '/home/gerald/ProcessedMusic/Crush/Here/Crush-Live.mp3'
output_file = '/home/gerald/MusicProcessing/src/generated_files/Music/Crush/Here/Crush-Live.mp3'

# try:
#     # First pass to measure loudness
#     ffmpeg.input(input_file).output('/dev/null',
#                                     f='null',
#                                     af='loudnorm=print_format=json',
#                                     loglevel='error') \
#         .run(capture_stdout=True, capture_stderr=True)

#     # Note: Extracting the JSON data for the second pass is more complex
#     # and often involves parsing stderr output. For simplicity, this example
#     # directly applies a generic loudnorm without a second pass based on
#     # measured values. For precise EBU R128, you'd parse the JSON from the first pass.

#     # Second pass with loudnorm filter
#     (
#         ffmpeg.input(input_file)
#         .output(output_file, af='loudnorm=i=-13:lra=7:tp=-2', c='copy') # Adjust i, lra, tp as needed
#         .run(overwrite_output=True)
#     )
#     print(f"Successfully normalized '{input_file}' to '{output_file}'")

# except ffmpeg.Error as e:
#     print(f"Error: {e.stderr.decode()}")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")

# working ubuntu cli:
# ffmpeg-normalize ~/ProcessedMusic/Crush/Here/Crush-Live.mp3 -c:a libmp3lame -b:a 128k --extra-output-options "-id3v2_version 3" --normalization-type peak --target-level 0 -f -o ~/MusicProcessing/src/generated_files/Music/Crush/Here/Crush-Live.mp3
# working windows powershell cli:
# ffmpeg-normalize F:\ProcessedMusic\Crush\Here\Crush-Live.mp3 -c:a libmp3lame -b:a 128k --extra-output-options "-id3v2_version 3" --normalization-type peak --target-level 0 -f -o D:\MusicProcessing\src\generated_files\Music\Crush\Here\Crush-Live.mp3
# album art and tags are preserved!!!

try:
    # Example for EBU R128 normalization
    command = [
        'ffmpeg-normalize',
        input_file,
        '-o', output_file,
        '-ebu',  # EBU R128 normalization
        '-t', '-23', # Target Integrated Loudness (LUFS)
        '-tp', '-2', # Target True Peak (dBTP)
        '-lrt', '7'  # Target Loudness Range (LU)
    ]
    subprocess.run(command, check=True)
    print(f"Successfully normalized '{input_file}' to '{output_file}' using ffmpeg-normalize.")

except subprocess.CalledProcessError as e:
    print(f"Error during normalization: {e}")
    print(f"Stderr: {e.stderr.decode()}")
except FileNotFoundError:
    print("Error: 'ffmpeg-normalize' command not found. Please ensure it is installed and in your PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
