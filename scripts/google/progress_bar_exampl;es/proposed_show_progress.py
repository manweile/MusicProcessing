# @register_pydub_effect
# def strip_silence(seg, silence_len=1000, silence_thresh=-16, padding=100, show_progress=False):
#     if padding > silence_len:
#         raise InvalidDuration("padding cannot be longer than silence_len")

#     chunks = split_on_silence(seg, silence_len, silence_thresh, padding)
#     crossfade = padding / 2

#     if not len(chunks):
#         return seg[0:0]

#     if show_progress:
#         from tqdm import tqdm
#         chunks = tqdm(chunks, desc="Processing chunks")

#     seg = chunks[0]
#     for chunk in chunks[1:]:
#         seg = seg.append(chunk, crossfade=crossfade)

#     return seg