<!-- markdownlint-disable MD033 -->

# Plan: Accept optional target directory for convert_file

Add an optional `target_dir` parameter to `convert_file` (and propagate to `convert_walk`) so callers can override the export root.<br>
Implement a small, backward-compatible extension to `directory.path_info` to accept an export root, validate `target_dir`,
update call sites and tests, and document the change.

Steps

1. Update `AudioMetadata.convert_file` signature to accept `target_dir: str | None = None`
and validate the value (must be a directory path or creatable path). depends on step 2
2. Extend `directory.path_info` to accept an optional `export_root: str | None = None`.
   1. If `export_root` is provided, build the export path under that root instead of `GENERATED_PATH`.
   2. Keep default behavior when `export_root` is `None` (no behavioral change). blocks step 3
3. In `convert_file`, pass `target_dir` through to `directory.path_info(file_path, export_root=target_dir)` to obtain `export_path`.
   1. If `directory.path_info` returns `None`, raise `PathInfoError` as before.
4. Keep existing `directory.make_dir(os.path.dirname(export_path))` call (it will create directories under the provided `target_dir` when given).
5. Update `convert_walk` to accept the same optional `target_dir` parameter and propagate it when calling `self.convert_file(...)`
so batch conversions can export to a custom root. parallel with step 6
6. Update any CLI or programmatic call sites that should support a custom export root (e.g., `main.py` entry points)
to accept and forward an optional `--target-dir`/`target_dir` argument.
   1. Make the CLI option optional and documented.
7. Add unit tests:
   - Test `convert_file` with a temporary `target_dir` to ensure exported mp3 appears under the given root and metadata/cover art are applied.
   - Test `convert_walk` with `target_dir` to ensure all files are exported under the target root.
   - Keep existing tests unchanged and re-run them to verify backward compatibility.
8. Update the `convert_file` docstring to document the new `target_dir` parameter and expected behavior
(validation, created directories, absolute vs relative paths).
9. Run full unit tests and a quick manual conversion in the workspace against a small sample to validate behavior.

## Relevant files

- src/audio_info/audio_metadata.py — modify `convert_file` signature, add validation and call site changes;
  - update `convert_walk` to accept/propagate `target_dir`.
- src/dir_processing/directory_processing.py — extend `path_info` to accept `export_root` and preserve existing return semantics.
- main.py — add optional CLI argument(s) to expose `target_dir` (if CLI integration desired).
- tests/test_audio_metadata.py — add tests for explicit `target_dir` behavior and adjust fixtures if necessary.
- Any helper modules used by `path_info` (constants): `src/__init__.py` (references to `GENERATED_PATH`, `MUSIC_TLD`, `MP3_EXT`).

## Verification

1. Run unit tests: ensure all existing tests pass and new tests for `target_dir` succeed.
2. Run `convert_file` manually (small sample):
   1. verify output file exists under provided `target_dir`, metadata and album art present, and ID3v2.3 tags preserved.
3. Run `convert_walk` with `target_dir` exports all files under the given root and preserves relative artist/album structure.
4. Confirm no behavior change when `target_dir` is omitted.

## Decisions / assumptions

- Parameter name: `target_dir` (clear and explicit).
- Backward compatibility: keep `directory.path_info` default behavior when `export_root` is `None` to avoid breaking existing callers.
- Validation: If `target_dir` points to an existing file (not a directory), raise `PathInfoError`.
  - If path is relative, resolve it against the current working directory.
  - Create directories as needed using current `directory.make_dir` behavior.

## Further Considerations

1. CLI UX: add `--target-dir` optional flag to CLI; consider allowing relative paths and expanding `~` on POSIX.
   1. Document behavior in README and docstrings.
2. Permissions: if `target_dir` is on a different drive or requires elevated permissions, conversions may fail with `OSError`
   1. add clear error messaging in logs.
3. Tests: use `tmp_path` or `tmpdir` fixtures to avoid polluting repository
   1. ensure cleanup after tests.

If you want, I can now add unit tests and adjust `main.py` to accept the `--target-dir` flag.
