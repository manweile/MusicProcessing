import ffmpeg
import platform

_ART_FILE = "Folder.jpg"

# also see https://blog.1a23.com/2020/03/16/read-and-write-tags-of-music-files-with-ffmpeg/ for an
# ffmpeg cli that works!

def extract_cover_art(input_file, output_file):
    """
    Extracts cover art from a media file.

    Args:
      input_file: Path to the input media file.
      output_file: Path to save the extracted cover art image.
    """
    try:
      # (
      #   ffmpeg
      #   .input(input_file)
      #   .output(output_file, map='0:v', map_metadata='-1')
      #   .run(capture_stdout=True, capture_stderr=True)
      # )

      # specifies the input media file
      input_stream  = ffmpeg.input(input_file)
      # specifies the output file
      # map argument selects video stream to get cover art
      # map_metadata prevents copying metadata form input file to output image
      output_stream = ffmpeg.output(input_stream, output_file, map='0:v', map_metadata='-1')
      # run executes the ffmpeg command
      out, err = ffmpeg.run(output_stream, capture_stdout=True, capture_stderr=True, quiet=True, overwrite_output=True)
      print(f"Cover art extracted from {input_file} and saved to {output_file}")
    except ffmpeg.Error as e:
      print(f"An error occurred: {e.stderr.decode()}")



# Example usage:
# input_file = r"\\192.168.0.14\sambashare\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"
# output_file = "Folder.jpg"
# extract_cover_art(input_file, output_file)

file_path = None
if platform.system() == "Linux":
  file_path = r"/home/gerald/Music/Elton John/Goodbye Yellow Brick Road/Elton John-Saturday Night's Alright for Fighting.wma"  # has art
  # file_path = r"/home/gerald/Music/The Eagles/Desperado/The Eagles-Desperado.m4a"       # no art
elif platform.system() == "Windows":
  file_path = r"C:\Music\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"  # has art
  # file_path = r"\\192.168.0.14\sambashare\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"
  # file_path = r"C:\Music\The Eagles\Hotel California\The Eagles-Hotel California.wma"       # no art

extract_cover_art(file_path, _ART_FILE)