import numpy as np
from pydub import AudioSegment
import ffmpeg


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
