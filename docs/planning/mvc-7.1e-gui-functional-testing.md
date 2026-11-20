# Milestone 7.1e: GUI Functional-Test Baseline

This plan is part of the [MVC refactoring plan](mvc.plan.prompt.md), Milestone 7.
Complete it after 7.1a–7.1d and before 7.1f or any Milestone 7 controller iterations.

## Goal

Establish reliable functional coverage of the current `MainFrame` before controller extraction changes GUI behavior.
The tests must exercise the wx GUI itself, not just instantiate the frame or test controllers in isolation.

## Work

- Use the model unit tests that correspond to each GUI workflow as the reference for choosing fixtures, setup, expected
  outputs, and meaningful error cases. For example, use `test_convert_file` and `test_convert_walk` in
  `tests/test_audio_metadata.py` as patterns for GUI file-conversion and directory-conversion tests, including their
  copied music fixtures and expected output paths. Apply the same approach to the other tabs using their matching model
  tests.
- Keep these tests focused on GUI functionality: drive the named controls as a user would and assert visible results
  and produced outputs. Do not add GUI tests for helper methods or private functions, or duplicate model-level logic
  tests through direct method calls.
- Preserve existing widget names and give every interactive or test-targeted widget an explicit, stable name unique
  across the GUI. Test that the required names are present and unique.
- Exercise all six currently displayed tabs through named wx controls and user events. Cover each tab's primary workflow,
  validation, busy behavior, dialogs, and generated outputs as applicable to the existing GUI.
- Use isolated fixture copies and generated-output paths, bounded waits for worker completion, and clean window teardown.
  Assert visible outcomes and generated files.
- Keep tests individually discoverable in VS Code Test Explorer and runnable as a separate functional suite.
- Support all required environments:
  - VS Code on Windows 10: run with the normal desktop display; do not require Xvfb or Linux-only commands.
  - VS Code on Ubuntu 26: run with the desktop display when available, or under Xvfb when headless.
  - GitHub Actions and GitHub Local Actions (GLA): run headlessly under Xvfb.
- Keep fixtures, generated-output isolation, dependency setup, executable discovery, and path handling portable across
  Windows and Linux. Tests must not depend on a particular checkout path, path separator, shell, or existing desktop
  session; ensure FFmpeg/ffprobe and wxPython are available in each environment.
- Update `.github/workflows/python-app.yml`: its current combined unittest-discovery command does not enforce the
  required order. Run model/unit tests first and the GUI functional suite only after they succeed, in separate
  processes/steps under `xvfb-run` on headless Linux. Preserve the workflow's `ACT`-specific generated-output isolation.
- Configure `.vscode/settings.json` so VS Code Test Explorer keeps the model/unit and GUI functional tests separately
  discoverable. Document and follow the two-group sequence: finish the model/unit group before running the GUI group;
  do not use a combined Run All if it cannot guarantee this ordering.
- Update `docs/md_files/Testing.md` with platform-appropriate commands and prerequisites: native execution on Windows,
  desktop or Xvfb execution on Ubuntu, and Xvfb execution in GitHub Actions and GLA.
- Verify the ordered test runs in VS Code on Windows 10 and Ubuntu 26, GitHub Actions, and GLA.

## Validation and Exit Criteria

- The model/unit suite completes successfully before the GUI functional suite starts; fixture cleanup is complete.
- GUI functional tests pass in VS Code on Windows 10 and Ubuntu 26, and headlessly in GitHub Actions and GLA.
- All six tabs' applicable primary workflows are exercised, with visible outcomes and generated outputs asserted.
- Required widget names are explicit, stable, present, and unique across the GUI.
- Do not begin 7.1f or the controller iterations if the baseline fails, model/unit execution fails, or fixture cleanup has
  not completed.
