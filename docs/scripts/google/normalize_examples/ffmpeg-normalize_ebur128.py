import subprocess

input_file = '/home/gerald/ProcessedMusic/Crush/Here/Crush-Live.mp3'
output_file = '/home/gerald/MusicProcessing/src/generated_files/Music/Crush/Here/Crush-Live.mp3'

try:
    # Example for EBU R128 normalization, t -23, tp -2 and lrt 7 are ebu r128 default values
    command = [
        'ffmpeg-normalize',
        input_file,
        '-o', output_file,
        '-ebu',         # EBU R128 normalization
        '-t', '-23',    # Target Integrated Loudness (LUFS)
        '-tp', '-2',    # Target True Peak (dBTP)
        '-lrt', '7'     # Target Loudness Range (LU)
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
