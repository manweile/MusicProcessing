<!-- markdownlint-disable MD033 -->

# Plan: Update Artist Genre Metadata

Add a reusable `AudioMetadata` operation and a `main.py` CLI command that reads:

- a comma-delimited UTF-8 artist-to-genre mapping
- finds immediate artist directories beneath a supplied music root
- recursively updates every supported audio file below each matched artist
- reports skipped/unreadable files without stopping the whole run.
- Reuse existing per-format tag-key mappings and Mutagen conventions
- replace every existing genre value with the one CSV value.

## Steps

1. Add a public `AudioMetadata` method in `src/audio_info/audio_metadata.py` accepting a music root and CSV path.
    1. Validate both before any writes; use the artist directory basename, not embedded metadata, as the lookup key.
2. Add helpers for CSV ingestion and per-file genre assignment.
    1. Parse UTF-8 comma-delimited input with exact header `artist name,artist genre`
    2. Reject invalid headers, blanks, duplicates, and non-alphabetical artist rows.
    3. Keep matching exact and case-sensitive.
3. Sort and inspect only direct subdirectories of the root as artist folders.
    1. For matched artists, recursively process only `.flac`, `.mp3`, `.m4a`, and `.wma` files.
    2. Skip and report artists missing from the CSV.
4. Reuse `FLAC_KEYS`, `MP3_KEYS`, `M4A_KEYS`, and `WMA_KEYS` for genre keys.
    1. Replace/create:
      - FLAC: `GENRE`
      - MP3: `TCON`, saved using the project’s ID3v2.3 behavior
      - M4A: `\xa9gen`
      - WMA: `WM/Genre` with the appropriate ASF value type
    2. All prior tag states, including absent, empty, single, and multi-value, become exactly one CSV genre.
5. Handle failures per file:
    1. log and collect failures while continuing the remaining work.
    2. Expose a run summary containing updated files, skipped artist folders, unsupported files, and failures.
6. Add a `main.py` subcommand following `CustomArgumentParser` and current dispatch conventions.
    1. Require the music root and CSV path, invoke the method, print a concise summary, and use nonzero exit status for invalid input or file failures.
7. Extend `tests/test_audio_metadata.py` using copied temporary fixtures, never modifying checked-in audio.
    1. Populate `tests/Music/artist_genre_test.csv` or generate an equivalent temporary CSV with the approved comma-delimited format.
8. Test all four formats and all required tag conditions:
    1. the 4 accepted audio types: `.flac`, `.mp3`, `.m4a`, and `.wma`.
    2. one audio file per artist with missing, empty, single-value, and multi-value genre.
      1. the genre conditions should be 1 condition each; ie. missing could be on wma, empty on mp3, single-value on m4a, and multi-value on flac.
            2. Before updating, verify the empty-genre fixture has a whitespace-only genre value.
        3. Verify each results in precisely one mapped genre after saving and reloading.
9. Test exact matching, unmatched artist reporting, recursive album processing, malformed CSV, duplicate rows, unsorted rows, and
   missing paths.
    1. Add a CLI smoke test if current command tests provide a suitable pattern.
10. Document the command, required inputs, exact CSV header, and case-sensitive artist-directory match in the existing command
    documentation location.

## Relevant Files

- `src/audio_info/audio_metadata.py` - New workflow; reuse existing genre tag mappings.
- `src/dir_processing/directory_processing.py` - Reference existing directory and CSV conventions.
- `main.py` - Parser and command routing.
- `tests/test_audio_metadata.py` - Isolated behavior and metadata assertions.
- `tests/Music/test.csv` - Test mapping fixture if retained.
- `README.md` or current CLI documentation - User-facing command reference.

## Verification

1. Run focused genre-update tests, confirming direct Mutagen reads show one expected genre per file.
2. Run CLI smoke coverage with valid input and with an unmatched artist folder.
3. Verify invalid header, duplicate, unsorted, blank, missing-root, and missing-CSV cases do not modify audio.
4. Run `python -m unittest tests.test_audio_metadata`.
5. Run the project test command and regenerate Doxygen if public documentation changes.

## Decisions

- CSV is comma-delimited UTF-8.
- Header is exactly `artist name,artist genre`.
- Matching is exact and case-sensitive.
- Unmatched artist folders are skipped and reported.
- The initial implementation includes both API and CLI.
- No fuzzy matching, dry-run mode, genre inference, or extra formats are included.
