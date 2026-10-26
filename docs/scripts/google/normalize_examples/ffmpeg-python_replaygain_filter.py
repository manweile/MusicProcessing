import ffmpeg

input_file = '/home/gerald/Music/Crush/Here/Crush-Live.mp3'
output_file = '/home/gerald/Music/Crush/Here/replaygain-crush-live.mp3'

try:
    # Analyze ReplayGain values using the 'replaygain' filter
    # This filter calculates the gain and peak values but does not apply them directly.
    # The calculated values are usually stored in metadata or used for subsequent processing.
    # For a full ReplayGain implementation, you would need to extract these values
    # and then apply them using a 'volume' filter.
    # The 'replaygain' filter itself is more for analysis.
    stream = ffmpeg.input(input_file)
    stream = ffmpeg.filter(stream, 'replaygain')  # This calculates, not applies.

    # To apply ReplayGain, you would typically use the 'volume' filter with the calculated gain.
    # As 'ffmpeg-python' doesn't directly expose ReplayGain values for programmatic use within the same chain,
    # a common approach is to first analyze, then apply the gain in a separate step or with external tools.
    # For a simplified demonstration of applying a volume adjustment based on an assumed ReplayGain value:
    # Assume you have a ReplayGain value (e.g., -8.5 dB) you want to apply.
    replaygain_value_db = -8.5  # Replace with actual calculated ReplayGain if available

    # Applying a volume filter based on a hypothetical ReplayGain value
    audio_stream = ffmpeg.input(input_file).audio
    processed_audio = ffmpeg.filter(audio_stream, 'volume', f'{replaygain_value_db}dB')

    # Output the processed audio
    ffmpeg.output(processed_audio, output_file).run()

    print(f"Audio processed with ReplayGain-like volume adjustment and saved to {output_file}")

except ffmpeg.Error as e:
    print(f"FFmpeg error: {e.stderr.decode()}")
except Exception as e:
    print(f"An error occurred: {e}")
