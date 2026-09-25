'''
exhaustive search for all possible metadata formats across  collection using Mutagen.<br>
Mutagen is phenomenal at detecting overlapping tagging structures (like APEv2 co-existing with ID3v2).

Script uses Mutagen's internal scanners to give you a complete architectural picture of every file.

The Overlap Catch: If you throw a rogue MP3 file at this that has a legacy ID3v1 footer, an active ID3v2.3 header,<br>
and an APEv2 block attached via a legacy replaygain tool, it will accurately print all three formats for that single file.

Troubleshooting: "No recognized base metadata formats found (Untagged)"

If a file returns this status, it means one of three things:
1. **The file is completely untagged:** The audio stream is intact, but no metadata blocks have ever been written to the file container.
2. **Corrupted headers:** The file may have metadata, but the binary syncsafe headers (like `ID3` or `APETAGEX`) are malformed or corrupted,<br>
preventing Mutagen from safely identifying the block.
3. **Stream-only metadata:** The file relies purely on container-level stream properties rather than a dedicated, standard tagging architecture.
'''

import os
import json
import subprocess
from pathlib import Path

# Main baseline error class
from mutagen import MutagenError

# Individual module formats and their expected clean "missing" errors
from mutagen.id3 import ID3
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import error as ID3BadError

from mutagen.apev2 import APEv2
from mutagen.apev2 import APENoHeaderError
from mutagen.apev2 import error as APEBadError

from mutagen.flac import FLAC
from mutagen.flac import FLACNoHeaderError
from mutagen.flac import error as FLACBadError

from mutagen.mp4 import MP4
from mutagen.mp4 import MP4StreamInfoError
from mutagen.mp4 import error as MP4BadError

from mutagen.asf import ASF
from mutagen.asf import ASFHeaderError
from mutagen.asf import error as ASFBadError

from mutagen.wave import WAVE


def check_ffprobe_tags(file_path: str) -> bool:
    """
    Fallback method using ffprobe. Returns True if a global container tags
    dictionary exists and has at least one key-value pair populated.
    """
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        file_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, encoding="utf-8", check=True)
        probe_data = json.loads(result.stdout)
        fmt_tags = probe_data.get("format", {}).get("tags", {})
        return bool(fmt_tags and len(fmt_tags.keys()) > 0)
    except Exception:
        return False


def scan_base_encoding_formats(file_path: str) -> tuple[list[str], list[str]]:
    """
    Scans a file's binary blocks.
    Returns: (detected_formats_list, corruption_errors_list)
    Exceptions:
        FileNotFoundError: If the specified file does not exist.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    detected = set()
    corruptions = []
    ext = path.suffix.lower()

    # --- MP3 FORMAT SCOPE ---
    if ext == '.mp3':
        try:
            id3_tag = ID3(str(path))
            v = id3_tag.version
            if len(v) >= 2:
                v_str = f"ID3v2.{v[1]}"  # Transforms (2, 3, 0) directly into "ID3v2.3"
            else:
                v_str = "ID3v2"
            detected.add(v_str)
        except ID3NoHeaderError:
            pass
        except (ID3BadError, MutagenError, Exception) as e:
            corruptions.append(f"Corrupted ID3 Structure ({type(e).__name__}: {e})")

        if path.stat().st_size >= 128:
            try:
                with open(path, "rb") as f:
                    f.seek(-128, os.SEEK_END)
                    if f.read(3) == b"TAG":
                        detected.add("ID3v1 / ID3v1.1")
            except Exception as e:
                corruptions.append(f"Unreadable trailing block check: {e}")

        try:
            APEv2(str(path))
            detected.add("APEv2")
        except APENoHeaderError:
            pass
        except (APEBadError, MutagenError, Exception) as e:
            corruptions.append(f"Corrupted APEv2 Structure ({type(e).__name__}: {e})")

    # --- FLAC FORMAT SCOPE ---
    elif ext == '.flac':
        try:
            flac_file = FLAC(str(path))
            if flac_file.tags is not None:
                detected.add("FLAC Vorbis Comment Blocks")
            if flac_file.pictures:
                detected.add("FLAC Picture Blocks")
        except FLACNoHeaderError:
            pass
        except (FLACBadError, MutagenError, Exception) as e:
            corruptions.append(f"Corrupted FLAC Metadata Block ({type(e).__name__}: {e})")

    # --- M4A / MP4 FORMAT SCOPE ---
    elif ext in ('.m4a', '.mp4'):
        try:
            mp4_file = MP4(str(path))
            if mp4_file.tags is not None and len(mp4_file.tags.keys()) > 0:
                detected.add("iTunes / MP4 Metadata (ITMF)")
        except MP4StreamInfoError:
            pass
        except (MP4BadError, MutagenError, Exception) as e:
            corruptions.append(f"Corrupted MP4/ITMF Atom Structure ({type(e).__name__}: {e})")

    # --- WMA / ASF FORMAT SCOPE ---
    elif ext in ('.wma', '.asf'):
        try:
            asf_file = ASF(str(path))
            if asf_file.tags is not None and len(asf_file.tags.keys()) > 0:
                detected.add("ASF Metadata / WMT")
        except ASFHeaderError:
            pass
        except (ASFBadError, MutagenError, Exception) as e:
            corruptions.append(f"Corrupted ASF/WMA GUID Table ({type(e).__name__}: {e})")

    # --- WAV FORMAT SCOPE ---
    elif ext == '.wav':
        try:
            wave_file = WAVE(str(path))
            if wave_file.tags is not None:
                non_id3_keys = [k for k in wave_file.keys() if not k.startswith("ID3")]
                if non_id3_keys:
                    detected.add("RIFF LIST INFO Chunks")

            # WAV embedded ID3 check with updated clean string conversion
            try:
                id3_tag = ID3(str(path))
                v = id3_tag.version
                if len(v) >= 2:
                    v_str = f"WAV-Embedded ID3v2.{v[1]}"  # Transforms (2, 3, 0) directly into "ID3v2.3"
                else:
                    v_str = "WAV-Embedded ID3v2"
                detected.add(v_str)
            except (ID3NoHeaderError, Exception):
                pass
        except Exception as e:
            corruptions.append(f"Corrupted WAV RIFF Sub-chunking: {e}")

    # --- THE FALLBACK CHECK TRIGGER ---
    formats_list = sorted(list(detected))
    if not formats_list and not corruptions:
        if check_ffprobe_tags(str(path)):
            formats_list.append("Stream-Only Container Metadata (Detected via ffprobe)")

    return formats_list, corruptions


def scan_directory(directory_path: str):
    """Iterates cleanly through your directory structure."""
    print(f"Scanning target directory: {directory_path}\n" + "=" * 60)
    supported_extensions = {'.mp3', '.flac', '.wma', '.asf', '.m4a', '.mp4', '.wav'}

    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in supported_extensions:
                try:
                    formats, corruptions = scan_base_encoding_formats(str(file_path))
                    print(f"\nFile: {file_path.name}")

                    if formats:
                        for fmt in formats:
                            print(f"  [+] Format: {fmt}")

                    if corruptions:
                        for error_msg in corruptions:
                            print(f"  [!] ALERT: {error_msg}")

                    if not formats and not corruptions:
                        print("  [-] Clean Untagged (Audio stream is healthy, no metadata blocks exist)")

                except Exception as e:
                    print(f"\n[CRITICAL ERROR] Failed to access/scan completely: {e}")


if __name__ == "__main__":
    # target_dir = "F:/Mine/FinalizedMusic"
    target_dir = "F:/Mine/SourceMusic"
    # target_dir = "F:/Mine/SourceMusic/Cher"
    # target_dir = "D:/MusicProcessing/tests/Music"
    # target_dir = "F:/iTunes/iTunesSource"

    if not os.path.isdir(target_dir):
        raise NotADirectoryError(f"Target path does not exist or is not a directory: '{target_dir}'")

    scan_directory(target_dir)
