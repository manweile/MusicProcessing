import numpy as np
from pydub import AudioSegment
import ffmpeg


# def normalize_audio(input_filepath, output_filepath):
#     """
#     Normalizes the amplitude of an audio file to the range of -1.0 to 1.0.

#     Args:
#         input_filepath (str): Path to the input WAV audio file.
#         output_filepath (str): Path to save the normalized WAV audio file.
#     """
#     try:
#         # Read the audio file
#         sample_rate, audio_data = read(input_filepath)

#         # Convert audio data to float for accurate calculations
#         audio_data = audio_data.astype(np.float64)

#         # Find the maximum absolute amplitude in the audio data
#         max_amplitude = np.max(np.abs(audio_data))

#         # Normalize the audio data by dividing by the maximum amplitude.
#         # Handle the case where max_amplitude is zero to prevent division by zero.
#         if max_amplitude > 0:
#             normalized_audio_data = audio_data / max_amplitude
#         else:
#             normalized_audio_data = audio_data  # Already "normalized" if all zeros

#         # If the original audio was integer-based (e.g., 16-bit),
#         # convert back to the appropriate integer type if desired for saving.
#         # For 16-bit audio, the range is -32768 to 32767.
#         # Multiply by 32767 for 16-bit signed integer representation.
#         # Ensure to clip values to the valid range to prevent overflow.
#         # This step is optional if you want to keep the data as float for further processing.
#         if audio_data.dtype == np.int16:
#             normalized_audio_data = (normalized_audio_data * 32767).astype(np.int16)
#         elif audio_data.dtype == np.int32:
#             normalized_audio_data = (normalized_audio_data * 2147483647).astype(np.int32) # For 32-bit signed integer

#         # Write the normalized audio data to a new WAV file
#         write(output_filepath, sample_rate, normalized_audio_data)

#         print(f"Audio normalized and saved to: {output_filepath}")

#     except FileNotFoundError:
#         print(f"Error: Input file not found at {input_filepath}")
#     except Exception as e:
#         print(f"An error occurred: {e}")


# # Example usage:
# # Create a dummy WAV file for demonstration (replace with your actual file)
# # from scipy.io.wavfile import write
# # dummy_audio = np.random.randint(-10000, 10000, size=44100, dtype=np.int16)
# # write("input_audio.wav", 44100, dummy_audio)

# # normalize_audio("input_audio.wav", "normalized_audio.wav")
# input_audio = r"D:\MusicProcessing\src\generated_files\Music\Crush\Here\Crush-Live.mp3"
# output_audio = r"D:\MusicProcessing\src\generated_files\Music\Crush\Here\Normalized.mp3"
# normalize_audio(input_audio, output_audio)


input_mp3_path = r"D:\MusicProcessing\src\generated_files\Music\Crush\Here\Crush-Live.mp3" # Replace with your MP3 file path

# Load the MP3 using pydub
audio = AudioSegment.from_mp3(input_mp3_path)

# Convert to NumPy array
# Get raw audio data and convert to appropriate dtype
raw_audio_data = np.array(audio.get_array_of_samples())

# Reshape for stereo if necessary (pydub handles channels)
if audio.channels == 2:
    audio_array = raw_audio_data.reshape((-1, 2))
else:
    audio_array = raw_audio_data

# Convert to float32 for normalization (standard for audio processing)
audio_array = audio_array.astype(np.float32) / (2**15)  # Normalize to [-1, 1] for 16-bit audio

# Find the maximum absolute value for normalization
max_abs_val = np.max(np.abs(audio_array))

if max_abs_val > 0:
    normalized_audio_array = audio_array / max_abs_val
else:
    normalized_audio_array = audio_array   # Handle cases where audio is silent

output_mp3_path = r"D:\MusicProcessing\src\generated_files\Music\Crush\Here\Normalized.mp3"

# Convert normalized NumPy array back to bytes for ffmpeg
# Scale back to original range (e.g., 16-bit integer) and convert to bytes
output_bytes = (normalized_audio_array * (2**15 - 1)).astype(np.int16).tobytes()

# Use ffmpeg-python to write the normalized audio to an MP3 file
(
    ffmpeg
    .input('pipe:', format='s16le', acodec='pcm_s16le', ar=audio.frame_rate, ac=audio.channels)
    .output(output_mp3_path, acodec='libmp3lame', audio_bitrate='128k')  # Adjust bitrate as needed
    .run(input=output_bytes, overwrite_output=True)
)
