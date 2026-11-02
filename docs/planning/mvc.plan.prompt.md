## Plan: MusicProcessing MVC Refactor

Update this plan against the current repository state of the `gui` branch as of 2026-11-02. Treat this file as the
working implementation and sequencing prompt for refactoring the codebase into a Model-View-Controller layout, not as a
historical archive of earlier planning notes.

The refactor separates domain logic (models), user interaction (views), and coordination (controllers), and adds a
separate CLI layer. Keep `main.py` as a thin entry point. Keep the audio-processing behavior, command-line subcommands,
output file formats, and the Doxygen comment style already used across the project. Preserve the existing VS Code,
Doxygen, and CI scaffolding. Each milestone must leave the existing test suite passing.

**Outline Alignment**

Key goals of this plan:

- Models never import `wx`, `argparse`, `tqdm`, or `yaspin`, and never reference widgets.
- Controllers never read or write view widgets and never call private view methods. Views pass plain values in and
  receive results through a small view interface.
- Views and the CLI are interchangeable front ends over the same models and controllers.
- Progress and spinner display go through a `ProgressReporter` interface, so `AudioMetadata.create_album_dirs`
  and `SubprocessUtilities` display correctly in both CLI mode (`tqdm`, `yaspin`) and the not-yet-coded GUI (`wx.Gauge`).
- Shared infrastructure (constants, paths, errors, logging) lives in `src/core/` and depends on nothing else in `src`.
- Dependencies point inward: `views` and `cli` depend on `controllers`, `controllers` depend on `models`, and every
  layer may depend on `core`.

**Repository Snapshot**

1. Models, flat by area: `src/audio_info/` (`AudioArt`, `AudioMetadata`, `AudioPlaylist`, `AudioUtilities`),
   `src/audio_normalize/audio_normalization.py`, and `src/dir_processing/directory_processing.py`.
2. GUI: `src/gui/wx_app.py` (`MainFrame`, about 1,000 lines, builds every panel, validates input, runs worker threads)
   and `src/gui/handlers.py` (`EventHandlers`).
3. Coupling: `EventHandlers` reads widgets directly (`self.frame.convert_file_path.GetValue()`) and calls private
   frame methods (`_validate_dir`, `run_task`, `_show_generated_files_dialog`). Module-level model instances
   (`art`, `metadata`, `directory`, `normalization`, `playlist`) are created in `handlers.py`.
4. CLI: `main.py` holds `CustomHelpFormatter`, `CustomArgumentParser`, one wrapper function per subcommand, a
   `main(args)` if-chain dispatcher, `existing_file` and `existing_path` validators, and the parser construction under
   `if __name__ == "__main__"`. The `gui` subcommand is dispatched from the same `main`.
5. Infrastructure at `src/` root: `errors.py`, `level_filter.py`, `logging_config.py`, `subprocess_utils.py`.
6. `src/__init__.py` mixes package marker, re-exports (errors, logging helpers, `GENERATED_PATH`), and all constants
   (audio, directory, log, and `ARG_CLI_*` / `ARG_HELP_*` strings).
7. `src/generated_files/` mixes runtime output (`AlbumArt/*.jpg`, CSV, text results, `.m3u`) with static GUI assets
   (`icon_files/`, `licenses/`); its `__init__.py` exports `GENERATED_PATH`.
8. Progress display: `AudioMetadata.create_album_dirs` uses `tqdm` directly and `SubprocessUtilities` uses `yaspin`
   directly. Neither has a GUI equivalent yet.
9. Tests are flat under `tests/` (one module per model plus `test_gui.py` and `test_subprocess_utilities.py`).
   `test_gui.py` is a smoke test (`MainFrame` instantiation and `run_gui` callable). `tests/__init__.py` holds fixture
   paths and expected values; `tests/Music/` and `expected.*` hold fixture data.

**Target Structure**

```text
MusicProcessing/
├── main.py                           # Entry point: parses args, runs GUI or CLI
├── src/
│   ├── __init__.py                   # Empty (package marker only)
│   ├── core/                         # Shared infrastructure used by all layers
│   │   ├── __init__.py               # Re-exports: logging helpers, errors, GENERATED_PATH, ProgressReporter, NullProgress
│   │   ├── constants.py              # AUDIO_EXTS, CSV_DIR, LOG_EXT, UTF8, ... (no ARG_* or UI strings)
│   │   ├── paths.py                  # GENERATED_PATH, RESOURCES_PATH
│   │   ├── progress.py               # ProgressReporter protocol + NullProgress (default no-op)
│   │   ├── errors.py
│   │   ├── logging_config.py
│   │   └── level_filter.py
│   ├── models/                       # Domain logic; no wx, argparse, tqdm or yaspin imports
│   │   ├── __init__.py               # Re-exports: AudioArt, AudioMetadata, AudioPlaylist, AudioUtilities,
│   │   │                             #   AudioNormalization, DirectoryProcessing
│   │   ├── audio_art.py
│   │   ├── audio_metadata.py         # create_album_dirs(tld, progress=None)
│   │   ├── audio_playlist.py
│   │   ├── audio_utilities.py
│   │   ├── audio_normalization.py
│   │   ├── directory_processing.py
│   │   └── subprocess_utils.py       # run(cmd, progress=None); no yaspin import
│   ├── controllers/                  # Coordinate view input and model calls
│   │   ├── __init__.py
│   │   └── *_controller.py           # Accept a ProgressReporter from the view and pass it to models
│   ├── views/
│   │   ├── __init__.py               # Empty
│   │   └── wx/
│   │       ├── __init__.py           # Re-exports: run_gui
│   │       ├── app.py
│   │       ├── main_frame.py
│   │       ├── progress.py           # GaugeProgress (wx.Gauge, updates via wx.CallAfter)
│   │       └── panels/
│   │           ├── __init__.py
│   │           └── *_panel.py
│   ├── cli/
│   │   ├── __init__.py               # Re-exports: build_parser, run_cli_command
│   │   ├── constants.py              # ARG_CLI_*, ARG_HELP_* strings
│   │   ├── parser.py                 # CustomArgumentParser, subparsers, existing_file/path
│   │   ├── progress.py               # TqdmProgress, SpinnerProgress (only place tqdm/yaspin are imported)
│   │   └── commands.py               # clip_check_file, convert_file, ... + run_cli_command
│   └── resources/                    # Static view assets (icons, licenses); no __init__.py
├── output/                           # Runtime-generated files (git-ignored); no __init__.py
└── tests/                            # Fixture data and tests; mirrors src/ layers
```

**Execution Milestones**

1. Milestone 1: Baseline and safety net
  - Record the current passing state before moving anything.
  - Files: `tests/`, `.github/workflows/python-app.yml`
  - Work:
    - run the full suite and record any pre-existing failures RESULT: all tests pass, no skips
    - decide whether tests stay flat or move into `tests/models/`, `tests/controllers/`, `tests/cli/`, `tests/views/` DECISION: keep flat for now
    - run ci-pipeline locally to ensure integration with GitHub Actions RESULT: pipeline passes, including all tests and checks
    - merge gui branch into development RESULT: development branch contains latest GUI changes
    - create a new branch for the upcoming core extraction work RESULT: new branch exists and is based on the latest development
    - run the full suite and record any pre-existing failures
    - decide whether tests stay flat or move into `tests/models/`, `tests/controllers/`, `tests/cli/`, `tests/views/`
  - Exit criteria: a known-good baseline exists, and CI runs the suite.

2. Milestone 2: `core/` extraction
  - Objective: move shared constants, paths, errors, and logging infrastructure into `src/core/` while preserving current imports, logging behavior, generated-output locations, and the flat test layout. This milestone does not move GUI assets or generated output and does not empty `src/__init__.py`.
  - Files: new `src/core/__init__.py`, `src/core/constants.py`, `src/core/paths.py`, `src/core/errors.py`, `src/core/level_filter.py`, `src/core/logging_config.py`; compatibility modules `src/errors.py`, `src/level_filter.py`, `src/logging_config.py`, `src/generated_files/__init__.py`; `src/__init__.py`; production importers and existing `tests/*.py` that consume the moved symbols.
  - Constraints:
    - Keep all existing tests flat in `tests/`; update test imports in place. Do not create layer-specific test directories in this milestone.
    - Preserve every constant value, exception class identity, public logging function, log filename/location, generated path value/type, output format, and current behavior.
    - Keep `ARG_CLI_*` and `ARG_HELP_*` in their current compatibility location for this milestone. They are intentionally reserved for CLI parser/dispatch use, not dead constants; make `src/cli/constants.py` canonical and migrate them during Milestone 5 (CLI extraction), not Milestone 2.
    - Do not move `src/generated_files/AlbumArt`, CSV/text/M3U output, `icon_files/`, or `licenses/` yet. Asset/output separation is Milestone 8.
    - `src/core/` must not import through the `src` package root or depend on a compatibility shim. Internal core imports must be relative or point directly to another `src.core` module.
    - Do not configure logging from `src/core/__init__.py`. Preserve the existing package-root initialization until the later explicit startup/bootstrap change, and do not install duplicate handlers.

  - Atomic implementation sequence:

    1. **Capture the starting state and inspect references.**
       - Confirm the branch is based on the validated `development` baseline and run the project's full unit suite.
       - Search all Python files for `from src import`, `import src`, `GENERATED_PATH`, and `src.generated_files`. Also search all files for `generated_files`, `icon_files`, `licenses`, and `RESOURCES_PATH` before path/asset changes. On Windows PowerShell, run each grep command on one line; do not use Bash `\\` line continuations.
       - Record the existing generated path as the absolute directory containing `src/generated_files/__init__.py`; record that consumers currently include `main.py`, `src/audio_info/audio_art.py`, `src/audio_info/audio_playlist.py`, `src/dir_processing/directory_processing.py`, `src/gui/wx_app.py`, and existing test modules.
       - Record that the current root package configures logging at import time and creates CSV, log, and result directories under `GENERATED_PATH`. This behavior is part of the compatibility baseline.
       - Exit check: baseline tests pass and the import/path/logging inventory is understood before edits.

    2. **Create the new core package without side effects.**
       - Add `src/core/__init__.py` as a package marker only (or with a docstring and an explicit `__all__` only after the exports are stable). It must not import the root package, configure logging, or eagerly re-export modules in a way that creates a cycle.
       - Add `src/core/constants.py`; copy the existing Doxygen documentation and values without behavior changes. Move these non-CLI constants:
         - Application/audio types and extensions: `APP_NAME`, `ASF_TYPE`, `AUDIO_EXTS`, `AUDIO_FILES`, `FLAC_EXT`, `FLAC_TYPE`, `FOLDER_ART`, `M4A_EXT`, `MP3_EXT`, `MP3_TYPE`, `MP4_TYPE`, `MUSIC_TLD`, `WMA_EXT`.
         - Playlist constants: `M3U_EXT`, `PLAYLIST_EXTS`, `PLAYLIST_TYPES`.
         - Output-directory/file constants: `CSV_DIR`, `CSV_EXT`, `RESULT_DIR`, `RESULT_EXT`.
         - Logging/encoding constants: `ERROR_LOG_FORMAT`, `LOG_DIR`, `LOG_EXT`, `UTF8`.
         - Normalization targets: `ILT`, `LRA`, `TP`.
       - Do not move `ARG_CLI_EXT`, `ARG_CLI_FFPROBE`, `ARG_CLI_FILE`, `ARG_CLI_PLAYLIST`, `ARG_CLI_PATTERN`, `ARG_CLI_TLD`, `ARG_CLI_TYPE`, or `ARG_HELP_AUDIO`, `ARG_HELP_FFPROBE`, `ARG_HELP_FILE`, `ARG_HELP_NORMAL`, `ARG_HELP_PATTERN_MAN`, `ARG_HELP_PATTERN_OPT`, `ARG_HELP_PLAYLIST`, `ARG_HELP_TLD` in this milestone. Their canonical destination is `src/cli/constants.py` in Milestone 5.
       - Exit check: each copied constant compares equal to its current value; no caller has been changed yet.

    3. **Add canonical paths while preserving the old generated location.**
       - Add `src/core/paths.py` with `SRC_PATH`, `GENERATED_PATH`, and `RESOURCES_PATH`. Compute `SRC_PATH` from the location of `core/paths.py`; define `GENERATED_PATH` as `src/generated_files`, exactly matching the existing value. Keep its current string type unless a deliberate all-consumer migration is separately approved. Define `RESOURCES_PATH` as the future `src/resources` location, but do not use it to redirect assets in this milestone.
       - Change `src/generated_files/__init__.py` to re-export the canonical `GENERATED_PATH` from `src.core.paths`; remove its duplicate path definition. Preserve the package docstring and `__all__` as appropriate.
       - Keep `src/__init__.py` exporting `GENERATED_PATH` during compatibility; make it reference the canonical path.
       - Verify equality between the old computed path and the new constant (normalized with `os.path.abspath`/`os.path.normpath`) and verify the exported value type. Do not run a test that writes or deletes files outside the existing test output scope.
       - Exit check: imports from both `src.generated_files` and `src.core.paths` return the same path value, and all current output/asset paths remain unchanged.

    4. **Move errors and logging modules with compatibility shims.**
       - Move `src/errors.py`, `src/level_filter.py`, and `src/logging_config.py` implementations into `src/core/errors.py`, `src/core/level_filter.py`, and `src/core/logging_config.py` respectively. Use repository-standard moves (for example `git mv`) so history is retained.
       - Change imports inside the moved core modules to use only standard-library modules or direct/relative `src.core` imports. In particular, `core/logging_config.py` must import `LevelFilter` from `src.core.level_filter` (or `.level_filter`), never through `src.level_filter`.
       - Replace each old module with a compatibility re-export of its public names from the corresponding `src.core` module. Preserve exception class identity: `src.errors.MusicProcessingError is src.core.errors.MusicProcessingError` and equivalent for every exported exception.
       - Keep the existing logging API and initialization call in `src/__init__.py` unchanged for now. Do not move initialization into `core/__init__.py`; do not call `configure_package_logging` a second time.
       - Exit check: old and new import paths expose the same functions/classes, importing core modules does not recurse through old shims, and no duplicate logging handlers are added.

    5. **Add root-package compatibility exports.**
       - Update `src/__init__.py` to expose moved non-CLI constants, the canonical `GENERATED_PATH`, error classes, and logging functions from their new modules while preserving current public names and `__all__` behavior.
       - Retain the existing `ARG_CLI_*` and `ARG_HELP_*` definitions/exports at `src` until Milestone 5. Do not copy them into `core/constants.py`.
       - Preserve the existing `configure_package_logging(...)` call and its exact arguments/order, using the new core constants and path. Ensure it still executes once when the package initializes, creates the same three output subdirectories, and returns/configures the same package logger.
       - Keep `src/__init__.py` as a temporary compatibility facade through this milestone and subsequent migration work. It is not emptied here: CLI constants remain to be extracted in Milestone 5, and the root initializer is removed only in Milestone 9 after explicit startup logging and all import migrations are complete.
       - Exit check: existing `from src import NAME` imports continue to work and match the new canonical objects/values.

    6. **Migrate production imports in coherent, reviewable batches.**
       - Change constant imports in `main.py`, `src/audio_info/audio_art.py`, `src/audio_info/audio_metadata.py`, `src/audio_info/audio_playlist.py`, `src/audio_info/audio_utilities.py`, `src/audio_normalize/audio_normalization.py`, `src/dir_processing/directory_processing.py`, `src/gui/wx_app.py`, and `src/subprocess_utils.py` to `src.core.constants`.
       - Change production `GENERATED_PATH` imports in `main.py`, `audio_art.py`, `audio_playlist.py`, `directory_processing.py`, and `wx_app.py` to `src.core.paths`.
       - Change logging-helper imports to `src.core.logging_config` and exception imports to `src.core.errors` after confirming each destination module exists. Keep imports grouped and formatted using project conventions.
       - Do not change CLI argument constants in `main.py` until Milestone 5; they remain in the compatibility facade at this point.
       - After each coherent batch, run the focused relevant tests and then the full suite before proceeding. Keep the compatibility shims intact so unconverted callers remain valid.
       - Exit check: production code uses canonical core imports for moved symbols, with behavior and output paths unchanged.

    7. **Migrate tests in place and verify compatibility.**
       - Update existing flat files, not their locations: `tests/__init__.py`, `tests/test_audio_art.py`, `tests/test_audio_metadata.py`, `tests/test_audio_normalization.py`, `tests/test_audio_playlist.py`, `tests/test_audio_utilities.py`, `tests/test_directory_processing.py`, and `tests/test_subprocess_utilities.py` wherever they import moved symbols.
       - Use `src.core.constants`, `src.core.paths`, and `src.core.errors` for canonical imports. Preserve fixture names, contents, expected outputs, and test discovery paths.
       - Update any string-based mock/patch targets that refer to moved implementations. Search patch strings separately; plain import search does not find every string target.
       - Add focused compatibility assertions for old/new constant values, path identity/type, and exception class identity where they are not already covered. Do not add a test that relies on handler counts before identifying how the package logging initializer is isolated/reset in the existing test process.
       - Run each affected test module, then the full suite and the same local CI pipeline used for Milestone 1. Confirm no failures or skips and no change to generated-file expectations.
       - Exit check: flat tests pass using canonical imports; legacy import shims still pass compatibility checks.

    8. **Audit boundaries and close the milestone.**
       - Search again for imports from old locations and review each remaining hit. Remaining `from src import ARG_*` use is expected until Milestone 5; remaining imports of `src.errors`, `src.logging_config`, `src.level_filter`, or `src.generated_files` are allowed only as compatibility callers not yet migrated and must be listed explicitly.
       - Check the new `src/core/` files for imports from `src` root and old shims. They may import only standard-library modules and other core modules.
       - Confirm `GENERATED_PATH` is still the existing `src/generated_files` directory; confirm static assets and generated output have not been moved; confirm logging initializes once and writes to the existing locations.
       - Run the full unit suite and local CI pipeline. Record results in the branch/PR notes; do not edit unrelated planning sections as part of this milestone.
       - Exit check: core modules are independent of root exports, all compatibility behavior is preserved, and all tests/CI pass.

  - Validation:
    - Use the project's existing full test-suite and local CI commands; do not introduce a new test runner or reorganize test files.
    - Compare each migrated constant against its previous value, including exact string/list contents.
    - Assert `src.core.paths.GENERATED_PATH` resolves to the same existing directory and type as the prior `src.generated_files.GENERATED_PATH`.
    - Assert legacy and canonical imports of each exception resolve to the identical class object.
    - Verify package logging initializes once and still creates/uses the same generated CSV, log, and result directories.
    - Run the full unit suite and local CI pipeline after the complete milestone.
  - Exit criteria: all non-CLI shared constants, paths, errors, and logging implementations have canonical definitions in `src/core/`; `src/cli/constants.py` is deferred to Milestone 5; old imports remain compatible; core does not import from the `src` root or compatibility shims; `src/__init__.py` remains a compatibility facade and is explicitly not emptied until Milestone 9; the test suite remains flat and passes with no failures or skips; runtime outputs and static assets remain in their current locations.
3. Milestone 3: Progress interface
  - Add `core/progress.py` with `ProgressReporter` (`start(total, description)`, `advance(step)`, `finish()`) and a
    no-op `NullProgress`. `total=None` means indeterminate (spinner).
  - Files: `src/core/progress.py`, `tests/support.py`
  - Work:
    - add a recording `FakeProgress` to `tests/support.py`
    - unit-test `NullProgress` and `FakeProgress` semantics
  - Exit criteria: the interface exists and has tests; nothing else depends on it yet.

4. Milestone 4: Models move and decouple
  - Move model packages into `src/models/` and remove display dependencies.
  - Files: `src/audio_info/`, `src/audio_normalize/`, `src/dir_processing/`, `src/subprocess_utils.py`
  - Work:
    - `git mv` each module and leave temporary re-exports at the old paths
    - `AudioMetadata.create_album_dirs(tld, progress=None)` reports through `ProgressReporter` instead of `tqdm`
    - `SubprocessUtilities` reports spinner state through `ProgressReporter` (`start(None, ...)` and `finish()`) instead of `yaspin`
    - update `mock.patch` targets in tests to the new module paths
  - Validation: tests that patched `tqdm` or `yaspin` now assert on `FakeProgress` calls.
  - Exit criteria: `grep` finds no `wx`, `argparse`, `tqdm`, or `yaspin` import under `src/models/`.

5. Milestone 5: CLI extraction
  - Move command-line code out of `main.py`.
  - Files: `main.py`, new `src/cli/`
  - Work:
    - move `CustomHelpFormatter`, `CustomArgumentParser`, and the parser construction to `cli/parser.py` as `build_parser()`
    - move the per-subcommand wrapper functions to `cli/commands.py`
    - replace the `main(args)` if-chain with `run_cli_command(args)` returning an exit code (0 on success, 1 on error)
    - move `existing_file` and `existing_path` to `cli/parser.py`
    - add `cli/progress.py` with `TqdmProgress` and `SpinnerProgress` and pass them into model calls
    - `main(args)` runs the GUI for `gui`, otherwise returns `run_cli_command(args)`
    - the `__main__` block keeps `sys.exit(main(args))`
  - Validation: every subcommand's `--help` output is identical before and after; add `tests/cli/` tests for parser
    construction and dispatch.
  - Exit criteria: `main.py` contains only argument parsing wiring and the dispatch entry point.

6. Milestone 6: Controllers
  - Introduce controllers that own validation and model coordination.
  - Files: new `src/controllers/`
  - Work:
    - one controller per area (convert, metadata, normalization, art, playlist, directory) taking plain values and a view interface
    - a view interface (`show_message`, `show_error`, `show_generated_files`, `set_busy`) implemented by the wx view
    - move `_validate_dir`, `_validate_file`, and worker-thread orchestration (`run_task`, `worker`) out of `MainFrame`
    - construct model instances in one composition root instead of module-level globals in `handlers.py`
    - CLI commands call the same controllers where behavior overlaps
  - Validation: controller tests use a fake view and `NullProgress`; no `wx` import is needed.
  - Exit criteria: controllers contain no widget references.

7. Milestone 7: wx view split
  - Split `MainFrame` into frame plus panels and replace `EventHandlers`.
  - Files: `src/gui/wx_app.py`, `src/gui/handlers.py`, new `src/views/wx/`
  - Work:
    - one panel class per notebook tab (art, convert, normalize, playlist, metadata, directory)
    - panels bind events and forward plain values to controllers; they implement the view interface
    - add `views/wx/progress.py` with `GaugeProgress`, updating widgets only through `wx.CallAfter`, and a timer-driven `Pulse()` for indeterminate tasks
    - keep the existing worker-thread behavior so the UI stays responsive
    - remove `handlers.py`
  - Validation: `tests/test_gui.py` smoke tests updated to the new view classes; manual run of each tab.
  - Exit criteria: no controller or model references a widget; `run_gui` is re-exported from `views/wx/__init__.py`.

8. Milestone 8: Resources and generated output
  - Separate static assets from runtime output.
  - Files: `src/generated_files/`, `.gitignore`, `src/core/paths.py`
  - Work:
    - move `icon_files/` and `licenses/` to `src/resources/`
    - point `GENERATED_PATH` at `output/` (or a user data directory) and git-ignore it
    - decide whether the existing tracked `AlbumArt/*.jpg` and `test.m3u` are fixtures (move to `tests/`) or output (delete from tracking)
    - update every path reference, including the GUI icons and the "generated files" dialogs
  - Exit criteria: no tracked runtime output remains under `src/`.

9. Milestone 9: Cleanup and documentation
  - Remove the temporary re-exports and obsolete packages.
  - Files: old package locations, `Doxyfile`, `docs/md_files/`, `docs/dot_files/`, `README.md`, `.github/instructions/python.instructions.md`
  - Work:
    - delete old paths and the compatibility re-exports
    - update Doxygen input paths and regenerate `docs/dot_files` diagrams
    - update README and `docs/md_files/*` for the new layout
    - move test modules into mirrored folders if chosen in Milestone 1
  - Exit criteria: full suite and CI pass with only the new import paths.

**Test And Validation Status**

1. Existing: unit tests per model, a `SubprocessUtilities` test, and a GUI smoke test; fixture data in `tests/Music/`.
2. Fixtures (`tests/Music/`, `expected.*`, the CSV and M3U files) do not change.
3. Tests that change: import paths (`src.audio_info` to `src.models`, `src` constants to `src.core.constants`),
   `mock.patch` target strings, `tests/__init__.py` imports, `tests/support.py` (adds `FakeProgress`), and
   `test_gui.py` (rewritten for the view and controller split).
4. New tests: progress interface, CLI parser and dispatch, controllers (with a fake view), and reporter selection.
5. Run after every milestone: the full suite plus a manual smoke run of one CLI subcommand and the GUI.

**Repo Risks And Mismatches**

1. `src/__init__.py` imports from submodules that import back from `src`; moving constants and errors to `core/` removes
   the cycle, but the order of edits matters. Empty the root `__init__.py` last.
2. `SubprocessUtilities` spinner behavior assumes a terminal; verify output when run from a worker thread and from tests.
3. `wx.Gauge` and widgets must only be touched from the main thread. All `GaugeProgress` updates go through `wx.CallAfter`.
4. `docs/dot_files/*` and `doxygen.log` are generated artifacts; regenerate rather than hand-edit.
5. `docs/scripts/` contains standalone experiments that may import from `src`; check them before deleting old paths.
6. `docs/planning/TODO.txt` includes a GUI logging item (run_task output to both the display and a log file); the
   controller and view interface in Milestone 6 is the natural place to resolve it, but it is out of scope unless added here.

**Relevant Files**

- `main.py` - current CLI parser, dispatcher, and entry point.
- `src/__init__.py` - current constants and re-exports.
- `src/gui/wx_app.py` - `MainFrame`, panel construction, worker threads, dialogs.
- `src/gui/handlers.py` - `EventHandlers` and module-level model instances.
- `src/audio_info/audio_metadata.py` - `create_album_dirs` and its `tqdm` progress bar.
- `src/subprocess_utils.py` - `SubprocessUtilities` and its `yaspin` spinner.
- `src/errors.py`, `src/logging_config.py`, `src/level_filter.py` - shared infrastructure.
- `src/generated_files/` - runtime output plus static GUI assets.
- `tests/__init__.py`, `tests/support.py`, `tests/test_gui.py` - fixture paths, helpers, and GUI smoke tests.
- `.github/workflows/python-app.yml` - CI test workflow.
- `Doxyfile`, `docs/md_files/` - documentation that references the layout.

**Verification**

1. The full test suite passes at the end of every milestone.
2. `main.py <subcommand> --help` output matches the pre-refactor output for every subcommand.
3. No `wx`, `argparse`, `tqdm`, or `yaspin` import exists under `src/models/` or `src/controllers/`.
4. No controller references a widget attribute or a private view method.
5. `src/core/` imports nothing else from `src`.
6. `create_album_dirs` and the subprocess spinner display correctly in CLI mode and report through `ProgressReporter`
   (verified with `FakeProgress`); the GUI gauge is verified manually once Milestone 7 is complete.

**Decisions**

- Keep `main.py` as a thin entry point.
- Keep CLI subcommand names, arguments, and help text unchanged.
- Models report progress only through `ProgressReporter`; front ends supply the display.
- Keep one view interface implemented by the wx view so controllers stay GUI-agnostic.
- Keep temporary re-exports at old import paths until Milestone 9 so the suite stays green throughout.
- Keep static assets in the repository and runtime output out of the source tree.
- Keep the project's Doxygen comment style for all moved and new modules.

**Further Considerations**

1. Test layout: flat `tests/` works, but mirroring `src/` (`tests/models/`, `tests/controllers/`, `tests/cli/`,
   `tests/views/`) scales better. Decide in Milestone 1.
2. Output location: a repo-local `output/` is simplest; a per-user data directory is better for installed use.
   Decide in Milestone 8.
3. GUI logging (see `docs/planning/TODO.txt`) could be folded into the view interface by adding a `log` method that
   writes to both the display and the log file.
4. If this file later needs to serve as a status dashboard, add a milestone table with `not started`, `in progress`,
   and `complete` labels.
