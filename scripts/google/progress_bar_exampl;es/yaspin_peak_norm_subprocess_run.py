import platform
import subprocess
from yaspin import yaspin


def test(in_file, out_file):
    # ffmpeg -hide_banner
    # -i F:\ConvertedMusic\Crush\Here\Crush-Live.mp3
    # -filter:a "volume=6dB"
    # -c:v copy
    # -c:a libmp3lame
    # -b:a 128k
    # -id3v2_version 3
    # D:\MusicProcessing\src\generated_files\Music\Crush\Here\Peak-Crush-Live.mp3 -y
    normalize_command = [
        "ffmpeg", "-hide_banner",
        "-i", in_file,
        "-filter:a", "volume=6dB",
        "-c:v", "copy",
        "-c:a", "libmp3lame",
        "-b:a", "128000",
        "-id3v2_version", "3",
        out_file, "-y"
    ]
    try:
        text = "Running external command..."
        with yaspin(text) as sp:
            result = subprocess.run(
                normalize_command,
                capture_output=True,
                text=True,
                check=True
            )

        sp.ok(f"✔ Command completed! in {sp.elapsed_time:.2f} secs")      # Indicate success
        print(result.stderr)               # Print output after spinner stops
    except subprocess.CalledProcessError as e:
        sp.fail("✖ Command failed!")       # Indicate failure
        print(f"Error: {e}")
        print(f"Stderr: {e.stderr}")


# Example usage:
if __name__ == "__main__":
    if platform.system() == "Windows":
        in_file = r"C:\Music\Crush\Here\Crush-Live.mp3"
        out_file = r"C:\MusicProcessing\src\generated_files\Music\Crush\Here\Peak-Crush-Live.mp3"
    elif platform.system() == "Linux":
        in_file = r"/home/gerald/Music/Crush/Here/Crush-Live.mp3"
        out_file = r"/home/gerald/MusicProcessing/src/generated_files/Music/Crush/Here/Peak-Crush-Live.mp3"

test(in_file, out_file)
