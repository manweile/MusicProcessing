import platform
import subprocess
from yaspin import yaspin


def test(in_file, out_file):
    normalize_command = [
        "ffmpeg",
        "-hide_banner",
        "-i", in_file,
        "-af", ("loudnorm=I=-16.0:TP=-2.0:LRA=11.0:"
                "measured_I=-16.7:measured_TP=-6.7:"
                "measured_LRA=8.1:measured_thresh=-27.0:"
                "offset=-0.64:linear=true:"
                "print_format=json"
                ),
        "-ar", str(44100),
        out_file, "-y"
    ]
    with yaspin(text="Running external command...") as sp:
        try:
            result = subprocess.run(normalize_command, capture_output=True, text=True, check=True)
            sp.ok("✔ Command completed!") # Indicate success
            print(result.stderr) # Print output after spinner stops
        except subprocess.CalledProcessError as e:
            sp.fail("✖ Command failed!") # Indicate failure
            print(f"Error: {e}")
            print(f"Stderr: {e.stderr}")


# Example usage:
if __name__ == "__main__":
    if platform.system() == "Windows":
        in_file = r"C:\Music\Crush\Here\Crush-Live.mp3"
        out_file = r"C:\MusicProcessing\src\generated_files\Music\Crush\Here\RBU-Crush-Live.mp3"
    elif platform.system() == "Linux":
        in_file = r"/home/gerald/Music/Crush/Here/Crush-Live.mp3"
        out_file = r"/home/gerald/MusicProcessing/src/generated_files/Music/Crush/Here/RBU-Crush-Live.mp3"

test(in_file, out_file)
