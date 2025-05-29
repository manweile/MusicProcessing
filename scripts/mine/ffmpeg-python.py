import ffmpeg

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
    media_stream  = ffmpeg.input(input_file)
    # specifies the output file
    # map argument selects video stream to get cover art
    # map_metadata prevents copying metadata form input file to output image
    media_stream = ffmpeg.output(media_stream, output_file, map='0:v', map_metadata='-1')
    # run executes the ffmpeg command
    ffmpeg.run(media_stream)
    print(f"Cover art extracted and saved to {output_file}")
  except ffmpeg.Error as e:
    print(f"An error occurred: {e.stderr.decode()}")


# Example usage:
input_file = r"\\192.168.0.14\sambashare\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"
output_file = "Folder.jpg"
extract_cover_art(input_file, output_file)