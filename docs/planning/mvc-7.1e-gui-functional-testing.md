# Milestone 7.1e: GUI Functional-Test Baseline

This plan is part of the [MVC refactoring plan](mvc.plan.prompt.md), Milestone 7.
Complete it after 7.1a–7.1d and before 7.1f or any Milestone 7 controller iterations.

## Goal

Establish reliable functional coverage of the current `MainFrame` before controller extraction changes GUI behavior.
The tests must exercise the wx GUI itself, not just instantiate the frame or test controllers in isolation.

## Work

- Preserve existing widget names and give every interactive or test-targeted widget an explicit, stable name unique
  across the GUI. Test that the required names are present and unique.
- Exercise all six currently displayed tabs through named wx controls and user events. Cover each tab's primary workflow,
  validation, busy behavior, dialogs, and generated outputs as applicable to the existing GUI.
- Use isolated fixture copies and generated-output paths, bounded waits for worker completion, and clean window teardown.
  Assert visible outcomes and generated files.
- Keep tests individually discoverable in VS Code Test Explorer and runnable as a separate functional suite.
- Configure GitHub Actions and GitHub Local Actions (GLA) to run model/unit tests first, then the GUI functional suite
  in a separate process under `xvfb-run`. Neither suite may run concurrently or include the other.
- Document and follow the equivalent two-group sequence in Test Explorer: finish model/unit tests before running GUI
  tests. Do not use a combined Run All if it cannot guarantee this ordering.
- Preserve the workflow's `ACT`-specific generated-output isolation.
- Verify the ordered test runs in Test Explorer, GitHub Actions, and GLA.

## Validation and Exit Criteria

- The model/unit suite completes successfully before the GUI functional suite starts; fixture cleanup is complete.
- GUI functional tests pass in Test Explorer and in headless GitHub Actions and GLA.
- All six tabs' applicable primary workflows are exercised, with visible outcomes and generated outputs asserted.
- Required widget names are explicit, stable, present, and unique across the GUI.
- Do not begin 7.1f or the controller iterations if the baseline fails, model/unit execution fails, or fixture cleanup has
  not completed.
