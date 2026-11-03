## Plan: MusicProcessing MVC Refactor

Update this plan against the current repository state of the `gui` branch as of 2026-11-02.<br>
Treat this file as the working implementation and sequencing prompt for refactoring the codebase into a Model-View-Controller layout;<br>
not as a historical archive of earlier planning notes.

Separate domain logic (models), user interaction (views), coordination (controllers), and add a separate CLI layer,
keeping `main.py` as a thin entry point.<br>
Retain audio-processing behavior, command-line subcommands, output file formats, and Doxygen comment style already in use.<br>
Preserve the existing VS Code, Doxygen, and CI scaffolding.<br>
Each milestone must leave the existing test suite passing.

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

**Incremental Migration And Compatibility**

- Keep the existing `main.py` CLI and `src/gui/` GUI operational while their replacements are being built. Do not
  remove, disable, or redirect either entry point merely because replacement modules exist.
- Migrate in small steps behind the existing entry points. The existing CLI commands and GUI remain the usable
  baseline while models, controllers, and replacement views are added; avoid requiring a branch switch to use them.
- Switch an entry point only after its replacement meets the parity checks below. Until then, preserve the old path
  and use compatibility adapters or re-exports where needed. Prefer having both paths call the same migrated
  implementation over maintaining duplicate business logic.
- After a successful cutover, keep the old entry point as a thin adapter for any remaining callers. Remove obsolete
  implementation only after its callers and compatibility requirements have been checked.
- This is a staged migration, not a requirement to keep two complete implementations indefinitely: retire old
  implementations after their replacement is verified and the cutover is complete.
- CLI parity means unchanged subcommand names, arguments, validation, help output, exit behavior, and observable
  processing/output behavior. GUI parity means successful startup and manual verification of every existing tab's
  primary workflow, validation, progress/busy behavior, dialogs, and generated outputs.

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
7. `src/generated_files/` mixes runtime output (CSV, text results, `.m3u`) with static GUI assets
   (`icon_files/`, `licenses/`) and user-supplied `AlbumArt/*.jpg` (read by `set_album_art`); its `__init__.py` exports `GENERATED_PATH`.
8. Progress display: `AudioMetadata.create_album_dirs` uses `tqdm` directly and `SubprocessUtilities` uses `yaspin`
   directly. Neither has a GUI equivalent yet.
9. Tests are flat under `tests/` (one module per model plus `test_gui.py` and `test_subprocess_utilities.py`).
   `test_gui.py` is a smoke test (`MainFrame` instantiation and `run_gui` callable). `tests/__init__.py` holds fixture
   paths and expected values; `tests/Music/` and `expected.*` hold fixture data.

**Target Structure**

```text
MusicProcessing/
├── output/                           # New, runtime-generated files (git-ignored); no __init__.py
│   ├── csv_files/                    # Runtime-generated CSV files; no __init__.py
│   ├── log_files/                    # Runtime-generated log files; no __init__.py
│   └── result_files/                 # Runtime-generated result files; no __init__.py
│
├── src/
│   ├── cli/                          # New, command-line interface layer
│   │   ├── __init__.py               # Re-exports: build_parser, run_cli_command
│   │   ├── constants.py              # ARG_CLI_*, ARG_HELP_* strings
│   │   ├── parser.py                 # CustomArgumentParser, subparsers, existing_file/path
│   │   ├── progress.py               # TqdmProgress, SpinnerProgress (only place tqdm/yaspin are imported)
│   │   └── commands.py               # clip_check_file, convert_file, ... + run_cli_command
│   │
│   ├── controllers/                  # New, coordinates view input and model calls
│   │   ├── __init__.py
│   │   └── *_controller.py           # Accept a ProgressReporter from the view and pass it to models
│   │
│   ├── core/                         # New, shared infrastructure used by all layers
│   │   ├── __init__.py               # Re-exports: logging helpers, errors, GENERATED_PATH, ProgressReporter, NullProgress
│   │   ├── constants.py              # AUDIO_EXTS, CSV_DIR, LOG_EXT, UTF8, ... (no ARG_* or UI strings)
│   │   ├── errors.py
│   │   ├── logging_config.py
│   │   ├── level_filter.py
│   │   ├── paths.py                  # GENERATED_PATH, RESOURCES_PATH
│   │   ├── progress.py               # ProgressReporter protocol + NullProgress (default no-op)
│   │   └── subprocess_utils.py       # run(cmd, progress=None); no yaspin import
│   │
│   ├── models/                       # New, domain logic; no wx, argparse, tqdm or yaspin imports
│   │   ├── __init__.py               # Re-exports: AudioArt, AudioMetadata, AudioPlaylist, AudioUtilities,
│   │   │                             #   AudioNormalization, DirectoryProcessing
│   │   ├── audio_art.py
│   │   ├── audio_metadata.py         # create_album_dirs(tld, progress=None)
│   │   ├── audio_playlist.py
│   │   ├── audio_utilities.py
│   │   ├── audio_normalization.py
│   │   ├── directory_processing.py
│   │
│   ├── resources/                    # New, static view assets (icons, licenses); no __init__.py
│   │   ├── AlbumArt/                 # User-supplied album art jpegs (read by set_album_art); git-ignored, not fixtures; no __init__.py
│   │   ├── icon_files/               # Icon files; no __init__.py`
│   │   └── licenses/                 # License files; no __init__.py
│   │
│   ├── views/                        # New, user interface layer
│   │   ├── __init__.py               # Empty
│   │   └── wx/
│   │       ├── __init__.py           # Re-exports: run_gui
│   │       ├── app.py
│   │       ├── main_frame.py
│   │       ├── progress.py           # GaugeProgress (wx.Gauge, updates via wx.CallAfter)
│   │       └── panels/
│   │           ├── __init__.py
│   │           └── *_panel.py
│   │
│   └── __init__.py                   # Empty (package marker only)
│
├── tests/                            # Fixture data and tests; mirrors src/ layers
│
└── main.py                           # Entry point: parses args, runs GUI or CLI
```

**Execution Milestones**

1. Milestone 1: Baseline and safety net
  - Record the current passing state before moving anything. COMPLETED
  - Files: `tests/`, `.github/workflows/python-app.yml`
  - Work:
    - run the full suite and record any pre-existing failures RESULT: all tests pass, no skips
    - decide whether tests stay flat or move into `tests/models/`, `tests/controllers/`, `tests/cli/`, `tests/views/` DECISION: keep flat for now
    - run ci-pipeline locally to ensure integration with GitHub Actions RESULT: pipeline passes, including all tests and checks
    - run the full suite COMPLETED
    - run ci locally COMPLETED
    - merge gui branch into development COMPLETED
    - create a new branch for the upcoming core extraction work COMPLETED
  - Exit criteria: a known-good baseline exists, and CI runs the suite.

COMPLETED

2. Milestone 2: update directory structure
  - add new structure per Target Structure outlined above COMPLETED
  - add empty `__init__.py` files where needed to mark packages COMPLETED

COMPLETED

3. Milestone 3: `core/` extraction
  - Move shared infrastructure out of the `src/` root.
  - Files:
    - `src/__init__.py`
    - `src/errors.py`
    - `src/logging_config.py`
    - `src/level_filter.py`
    - `src/generated_files/__init__.py`
  - Work:
    - split constants: audio, directory, log, and encoding constants go to `core/constants.py` COMPLETED
    - `ARG_CLI_*` and `ARG_HELP_*` go to `cli/constants.py` (Milestone 5) COMPLETED
    - move `GENERATED_PATH` to `core/paths.py` and add `RESOURCES_PATH`
    - keep temporary re-exports in the old locations so imports continue to resolve
    - empty `src/__init__.py` last, to avoid circular imports

    **Step 0**: Preparation COMPLETED

    On feature/mvc-refactoring, run the full suite once to confirm the baseline. COMPLETED<br>
    Find where each name is used, so the split follows real usage: COMPLETED<br>
    grep -rnE "from src import|import src" --include=*.py .<br>
    Check ARG_* and APP_NAME especially, since main.py and the GUI may use them.

    **Step 1** Confirm baseline and inventory COMPLETED

    Step 0 records a completed full-suite baseline.<br>
    Before changing imports, confirm that result applies to the current checkout.<br>
    If code has changed since the suite ran, or the result is uncertain,
    run the repository's existing full-suite command and record whether it passes.<br>
    This establishes what later migration test runs must preserve.

    Treat `docs/planning/search.txt` as a snapshot, not as a live inventory.<br>
    Refresh the searches below if the source has changed since that file was generated:

    ```bash
    grep -RInE --include="*.py" "from src import|from src\\.generated_files|GENERATED_PATH" .
    grep -RInE --exclude-dir=.git "generated_files|icon_files|licenses|RESOURCES_PATH" .
    ```

    The first search in `search.txt` already includes `from src.generated_files` and `GENERATED_PATH`;<br>
    it does not need to be rediscovered. Read those matches as different kinds of evidence:

    - `from src import NAME` identifies callers of the current compatibility surface.
      - Classify each `NAME` as a constant, error, or logging helper so it can later move to the correct core module.
    - `from src.generated_files import GENERATED_PATH` identifies callers of the old path export.
      - Record production and test callers separately, along with their uses of the path.
      - Do not confuse these with `from src import` imports
      - Retaining exports from `src` alone does not migrate imports from `src.generated_files`.
    - A `GENERATED_PATH` match may be a definition or a use rather than an import.
      - Check its surrounding code, and keep track of the definition separately from the callers.
      - The initial `src.core.paths` definition must still resolve to the existing `src/generated_files` directory so this migration does not change output locations.
    - The second, broader search also finds documentation, ignore rules, asset references, and comments.
      - These are useful for distinguishing runtime-generated files from static resources, but they are not all Python imports
      to change in this step.

    Use the inventory to plan small, reviewable migration batches:<br>
    migrate production imports by destination module, then update the related tests and any string-based mock patch targets.<br>
    Keep each test module in `tests/`; do not reorganize or move tests as part of this work.<br>
    Leave all imports unchanged during this inventory step.

    Before proceeding, the baseline result is known, each old import has been classified, and path references have
    been distinguished from other generated-file and asset references.<br>
    The actual definition and compatibility exports come next; import migrations happen only after those are in place.

    **Step 2** Add the destination modules COMPLETED

    Create src/core/ and src/cli/, with lightweight __init__.py files. COMPLETED<br>
    Add: src/core/constants.py COMPLETED
      - for the application, audio, directory, logging, encoding, and normalization constants currently in src/__init__.py:
        - APP_NAME, ASF_TYPE, AUDIO_EXTS, AUDIO_FILES, CSV_DIR, CSV_EXT, ERROR_LOG_FORMAT, FLAC_EXT, FLAC_TYPE
        - FOLDER_ART, ILT, LRA, LOG_DIR, LOG_EXT, LRA, M3U_EXT, M4A_EXT, MP3_EXT, MP3_TYPE, MP4_TYPE, MUSIC_TLD
        - PLAYLIST_EXTS, PLAYLIST_TYPES, RESULT_DIR, RESULT_EXT, TP, UTF8, WMA_EXT

    Add: src/cli/constants.py COMPLETED
      -  for all ARG_CLI_* and ARG_HELP_* constants. Keep them; they’re planned CLI API, not unused constants.

    Add: src/core/paths.py COMPLETED
      - for GENERATED_PATH and RESOURCES_PATH.
        - Initially, GENERATED_PATH must resolve to the existing src/generated_files directory.
        - Set RESOURCES_PATH to the planned static-assets directory, src/resources, and use it when the assets move.

    At this stage, add the new definitions without changing existing imports.

    **Step 3** Preserve compatibility from src

    Change src/__init__.py to import and re-export the new constants and paths, while preserving existing exports for errors and logging helpers.<br>
    Use explicit imports and maintain an accurate __all__; avoid wildcard imports.

    This gives callers both the old paths (for example, from src import AUDIO_EXTS);<br>
    and the new paths (for example, from src.core.constants import AUDIO_EXTS) during migration.<br>
    Keep the existing logging initialization behavior for now.

    **Step 4** Migrate imports in small batches

    Update production imports to use the new modules:

        Constants → src.core.constants
        Logging helpers → src.core.logging_config (once that module is moved)
        Errors → src.core.errors (once moved)
        GENERATED_PATH → src.core.paths

    Then update the corresponding test imports, including tests/__init__.py, and any string-based mock patch targets.<br>
    Run the tests after each batch. The src re-exports remain in place so unmigrated code continues to work.

    **Step 5** Wire in the CLI constants

    When extracting the CLI, use ARG_CLI_* in parser argument definitions and when reading the corresponding parsed fields in main(args);<br>
    for example, getattr(args, ARG_CLI_FILE). Use ARG_HELP_* for the related help text.

    These constants describe argument field names and help text, not subcommand names.<br>
    Keep subcommand names such as "gui" and "convert-file" separate unless you introduce constants for them explicitly.

    **Step 6** Move logging and error infrastructure

    Move errors.py, logging_config.py, and level_filter.py into core/<br>
    update their imports and leave compatibility re-exports at their old locations until callers are migrated.<br>
    Keep core/__init__.py free of logging setup side effects to avoid introducing import cycles.

    Before emptying src/__init__.py:
    - Preserve current package-level logging initialization
      - use an explicit, one-time startup/bootstrap call from the application entry point.
    - Verify logging still initializes for both CLI and GUI startup.

    **Step 7** Empty src/__init__.py last

    Once repository imports no longer rely on from src import ..., the old error/logging modules, or the old generated-files path export:

        Remove the compatibility re-exports and old module shims.
        Make src/__init__.py empty apart from its package docstring.
        Run the full test suite, check CLI help, and smoke-test GUI startup and logging.

    That order keeps compatibility while the imports move, and avoids breaking startup logging when the package-root side effect is removed.

  - Validation: the full suite passes with both old and new import paths.
  - Exit criteria: `core/` imports nothing else from `src`.

4. Milestone 4: Progress interface
  - Add `core/progress.py` with `ProgressReporter` (`start(total, description)`, `advance(step)`, `finish()`) and a no-op `NullProgress`.
  - `total=None` means indeterminate (spinner).
  - Files: `src/core/progress.py`, `tests/support.py`
  - Work:
    - add a recording `FakeProgress` to `tests/support.py`
    - unit-test `NullProgress` and `FakeProgress` semantics
  - Exit criteria: the interface exists and has tests; nothing else depends on it yet.

5. Milestone 5: Models move and decouple
  - Move model packages into `src/models/` and remove display dependencies.
  - Files: `src/audio_info/`, `src/audio_normalize/`, `src/dir_processing/`
  - Work:
    - `git mv` each module and leave temporary re-exports at the old paths
    - `AudioMetadata.create_album_dirs(tld, progress=None)` reports through `ProgressReporter` instead of `tqdm`
    - update `mock.patch` targets in tests to the new module paths
    - re-assess models that log warnings. Some will have to become exceptions, others may be downgraded to info, or removed entirely
  - Validation: tests that patched `tqdm` or `yaspin` now assert on `FakeProgress` calls.
  - Exit criteria: `grep` finds no `wx`, `argparse`, `tqdm`, or `yaspin` import under `src/models/`.

6. Milestone 6: CLI extraction
  - Move command-line code out of `main.py`.
  - Files: `main.py`, new `src/cli/`
  - Work:
    - keep the existing `main.py` invocation operational throughout extraction;
      - first make the new parser and command layer callable alongside it, then have `main.py` delegate only after CLI parity is verified
    - use the constants defined in `src/cli/constants.py`
    - move `CustomHelpFormatter`, `CustomArgumentParser`, and the parser construction to `cli/parser.py` as `build_parser()`
    - move the per-subcommand wrapper functions to `cli/commands.py`
    - replace the `main(args)` if-chain with `run_cli_command(args)` returning an exit code (0 on success, 1 on error)
    - move `existing_file` and `existing_path` to `cli/parser.py`
    - add `cli/progress.py` with `TqdmProgress` and `SpinnerProgress` and pass them into model calls
    - `main(args)` runs the GUI for `gui`, otherwise returns `run_cli_command(args)`
    - the `__main__` block keeps `sys.exit(main(args))`
  - Validation:
    - capture baseline help and behavior before extraction
    - compare every subcommand's `--help` output
    - exercise each command's validation, exit behavior, and representative output against the baseline.
    - Keep the old implementation available until these checks pass, then switch `main.py` to the new layer and retain it as the thin entry point.
  - Exit criteria: `main.py` contains only argument parsing wiring and the dispatch entry point.

7. Milestone 7: Controllers
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

8. Milestone 8: wx view split
  - Split `MainFrame` into frame plus panels and replace `EventHandlers`.
  - Files: `src/gui/wx_app.py`, `src/gui/handlers.py`, new `src/views/wx/`
  - Work:
    - keep `src/gui/` launchable while the replacement view is developed
    - do not remove `handlers.py` or redirect `run_gui` until the replacement passes GUI parity checks
    - one panel class per notebook tab (art, convert, normalize, playlist, metadata, directory)
    - panels bind events and forward plain values to controllers; they implement the view interface
    - add `views/wx/progress.py` with `GaugeProgress`
      - updating widgets only through `wx.CallAfter`
      - a timer-driven `Pulse()` for indeterminate tasks
    - keep the existing worker-thread behavior so the UI stays responsive
    - after parity is verified
      - switch `run_gui` to the replacement view and retain a compatibility adapter if existing callers still import `src/gui/`
      - remove `handlers.py` only when no callers depend on it
  - Validation:
    - keep the existing GUI smoke test passing during development
    - add/update tests for the replacement
    - then manually verify startup and each tab's primary workflow, validation, progress, dialogs, and generated outputs before cutover.
  - Exit criteria:
    - the replacement GUI passes parity checks
    - no controller or model references a widget
    - `run_gui` is re-exported from `views/wx/__init__.py`
    - the old GUI implementation is retired only after cutover.

9. Milestone 9: Resources and generated output
  - Separate static assets from runtime output.
  - Files: `src/generated_files/`, `.gitignore`, `src/core/paths.py`
  - Work:
    - move `icon_files/` and `licenses/` to `src/resources/`
    - move `AlbumArt/` to `src/resources/AlbumArt/`; these jpegs are user-supplied resources consumed by `set_album_art`, not
      fixtures, and are NOT tracked. Update `set_album_art` and every path reference to the new location
    - consolidate to a single master `.gitignore` at the repo root:
      - merge the rules from `src/generated_files/.gitignore` (`Music/**/*.*`, `test.m3u`, `AlbumArt/*.*`) and
        `docs/excel_files/.gitignore` (`~$*.xlsx`, `.~lock.*.xlsx#`) into root rules with full paths
      - add `src/resources/AlbumArt/*.jpg` (the directory always exists and always holds at least one usable jpg, so no `.gitkeep`), `output/`,
        `doxygen.log` and the existing generated-output entries under their new paths
      - delete the nested `.gitignore` files once their rules are in the root file
      - run `git rm -r --cached` on anything already tracked that is now ignored, and confirm with `git status` and
        `git check-ignore -v` on sample paths
    - point `GENERATED_PATH` at `output/` (or a user data directory) and git-ignore it
    - update every path reference, including the GUI icons and the "generated files" dialogs
  - Exit criteria: no tracked runtime output or `AlbumArt` jpegs remain under `src/`; exactly one `.gitignore` exists (at the root).

10. Milestone 10: Test and validation
  - take test layout from flat to mirrored folders as decided in Milestone 1
  - Files: test modules and supporting fixtures
  - Work:
    - create mirrored folder structure for tests
    - move existing test modules into the mirrored structure as needed
    - update import paths in the test modules to reflect the new structure
    - update any supporting fixtures or helper modules to match the mirrored layout
    - ensure test discovery works with the new structure
  - Validation:
    - run the full test suite
    - perform manual validation of the CLI and GUI workflows
  - Exit criteria: all tests pass and manual validation confirms expected behavior.

11. Milestone 11: Cleanup and documentation
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

1. `src/__init__.py` imports from submodules that import back from `src`
  1. moving constants and errors to `core/` removes the cycle, but the order of edits matters. Empty the root `__init__.py` last.
2. `SubprocessUtilities` yaspin spinner behavior assumes a terminal, and does NOT work with any wxPython GUI context.
  1. verify output when run from a worker thread and from tests.
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
- `src/core/subprocess_utils.py` - `SubprocessUtilities` and its `yaspin` spinner.
- `src/errors.py`, `src/logging_config.py`, `src/level_filter.py` - shared infrastructure.
- `src/generated_files/` - runtime output plus static GUI assets.
- `tests/__init__.py`, `tests/support.py`, `tests/test_gui.py` - fixture paths, helpers, and GUI smoke tests.
- `.github/workflows/python-app.yml` - CI test workflow.
- `Doxyfile`, `docs/md_files/` - documentation that references the layout.

**Verification**

1. The full test suite passes at the end of every milestone.
2. `main.py <subcommand> --help` output matches the pre-refactor output for every subcommand.
3. Before CLI cutover, the replacement matches the baseline CLI arguments, validation, exit behavior, and
   representative command outputs; `main.py` remains usable until then.
4. Before GUI cutover, the replacement starts and each existing tab's primary workflow, validation, progress,
   dialogs, and generated outputs are manually verified; `src/gui/` remains usable until then.
5. No `wx`, `argparse`, `tqdm`, or `yaspin` import exists under `src/models/` or `src/controllers/`.
6. No controller references a widget attribute or a private view method.
7. `src/core/` imports nothing else from `src`.
8. `create_album_dirs` and the subprocess spinner display correctly in CLI mode and report through `ProgressReporter`
   (verified with `FakeProgress`); the GUI gauge is verified manually once Milestone 7 is complete.

**Decisions**

- A single root `.gitignore` is the only ignore file; no nested `.gitignore` files.
- `AlbumArt/*.jpg` are user-supplied resources, git-ignored and not treated as test fixtures.
- Keep `main.py` as a thin entry point.
- Keep CLI subcommand names, arguments, and help text unchanged.
- Models report progress only through `ProgressReporter`; front ends supply the display.
- Keep one view interface implemented by the wx view so controllers stay GUI-agnostic.
- Keep temporary re-exports at old import paths until Milestone 9 so the suite stays green throughout.
- Keep static assets in the repository and runtime output out of the source tree.
- Keep the project's Doxygen comment style for all moved and new modules.

**Further Considerations**

1. Test layout: flat `tests/` works, but mirroring `src/` (`tests/models/`, `tests/controllers/`, `tests/cli/`,
   `tests/views/`) scales better. Decide in Milestone 1. DECISION: flat for now. Mirror in Milestone 10.
2. Output location: a repo-local `output/` is simplest; a per-user data directory is better for installed use.
   Decide in Milestone 8.
3. GUI logging (see `docs/planning/TODO.txt`) could be folded into the view interface by adding a `log` method that
   writes to both the display and the log file.
4. If this file later needs to serve as a status dashboard, add a milestone table with `not started`, `in progress`,
   and `complete` labels.