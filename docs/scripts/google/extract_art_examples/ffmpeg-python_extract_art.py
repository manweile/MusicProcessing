import ffmpeg
import platform

_ART_FILE = "Cover.jpg"

# also see https://blog.1a23.com/2020/03/16/read-and-write-tags-of-music-files-with-ffmpeg/ for an
# ffmpeg cli that works!


def extract_art_from_any(input_file, output_file):
    '''
    @brief Extracts cover art from a media file.

    @details Uses ffmpeg and is audio file type agnostic.
    @details The input file is assumed to have cover art.

    @param input_file {str} Path to the input media file.
    @param output_file {str} Path to save the extracted cover art image.
    @exception Error A ffmpeg error.
    @exception Exception A common baseclass exception to handle unforeseen errors.
    '''

    try:
        # specifies the input media for input stream
        input_stream = ffmpeg.input(input_file)

        # map argument specifies which input stream(s) should be included in the output.
        # by default, the covert art is the first (and only frame) of the of the (only) video stream.
        # 0: Refers to the first input file (index 0).
        # v: Refers to the video stream within that input file.
        # results in only including the video stream from the first input file in the output,
        # discarding any other streams (audio or video).
        map = '0:v'

        # map_metadata controls how metadata is handled.
        # -1: discard all alphanumeric metadata from the input.
        # results in no copying of metadata from input file to output image.
        map_metadata = '-1'

        # specify the output stream
        output_stream = ffmpeg.output(input_stream, output_file, map=map, map_metadata=map_metadata)

        # run executes the ffmpeg command
        # the capture_stdout and stderr are for debugging purposes
        # quiet prevents output to terminal
        # overwrite_output since won't be able to respond to an overwrite y/n prompt
        out, err = ffmpeg.run(output_stream, capture_stdout=True, capture_stderr=True, quiet=True, overwrite_output=True)
        print(f"Cover art extracted from {input_file} and saved to {output_file}")
    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr.decode()}")
    except Exception as e:
        raise Exception(f"Exception {e} extracting art from {input_file} to {output_file}")


file_path = None
if platform.system() == "Linux":
    file_path = r"/home/gerald/Music/Elton John/Goodbye Yellow Brick Road/Elton John-Saturday Night's Alright for Fighting.wma"  # has art
    # file_path = r"/home/gerald/Music/The Eagles/Desperado/The Eagles-Desperado.m4a"       # no art
elif platform.system() == "Windows":
    file_path = r"C:\Music\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"  # has art
    # file_path = r"\\192.168.0.14\sambashare\Elton John\Goodbye Yellow Brick Road\Elton John-Saturday Night's Alright for Fighting.wma"
    # file_path = r"C:\Music\The Eagles\Hotel California\The Eagles-Hotel California.wma"       # no art

extract_art_from_any(file_path, _ART_FILE)
