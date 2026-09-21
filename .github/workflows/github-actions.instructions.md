---
applyTo: ".github/workflows/**/*.yml, .github/workflows/**/*.yaml"
---

# GitHub Actions Workflow Rules

## Column Alignment Rules

- Use consistent column alignment for inline `# ...` comments and wrapped YAML values.
- Place inline `# ...` comments at column 61 where practical.
- Keep inline comments within column 150; shorten wording if necessary.
- Inline comments are not terminated by any punctuation; they are free-form text.
- YAML content before an inline comment must not extend past column 60; shorten wording or restructure the entry if necessary.
- Apply this decision table:
  1. If the YAML entry fits through column 60, place the inline `# ...` comment at column 61.
  2. If the YAML entry extends past column 60, place the `# ...` comment directly above the entry at the same indentation level.
- Indent wrapped YAML values according to the surrounding mapping or sequence structure.

## Details Block Formatting Rules

- Apply these rules to every `@details` block in GitHub Actions Doxygen-style comments.
- Write each `@details` line as a complete sentence ending with a period.
- Keep each `@details` line at or below column 150; shorten wording if necessary.
- If the shortest clear wording still exceeds 150 columns, break the line after, in this order of preference:
  1. a comma
  2. a semicolon
  3. a coordinating conjunction: "for", "and", "nor", "but", "or", "yet", or "so"
- Add a comment-only `#` line after the final `@details` line.

## File-Level Rules

- All new GitHub Actions workflow files require a file-level Doxygen-style documentation block using YAML comments.
- Start the file header with `# @file` on line 1.
- Add `# @author Gerald Manweiler`, followed by a `#` comment line.
- Add a one-line `# @brief`, followed by a `#` comment line.
- Add a `# @details` block that describes the workflow triggers and purpose.
- Follow the Details Block Formatting Rules.
- Add `# @version` using Semantic Versioning 2.0.0 per semver.org in `MAJOR.MINOR.PATCH` format.
- Add `# @date`, followed by a `#` comment line.
- Add `# @copyright Copyright (c) year Gerald Manweiler`.
- Leave one blank line after the file header block and before the workflow `name` key.

Example:

```yaml
# @file clean-storage.yml
# @author Gerald Manweiler
#
# @brief Auto Clean Actions Storage workflow for GitHub Actions.
#
# @details Trigger this workflow daily at midnight or through manual dispatch.
# Delete workflow runs older than three days while retaining at least three recent runs for each workflow.
#
# @version 1.0.0
# @date 2026-08-24
#
# @copyright Copyright (c) 2026 Gerald Manweiler

name: Auto Clean Actions Storage
```

- Keep workflow changes minimal and preserve each workflow's existing purpose.
- Treat `ci-pipeline.yml` as the continuous integration orchestrator.
- Treat `python-app.yml` as the active unit test pipeline.
- Treat `workflow-cleanup.yml` as the GitHub Actions workflow-run cleanup job.
- Treat `artifact-cleanup.yml` as the GitHub Actions artifact cleanup job.
- Preserve artifact uploads and failure-log collection used for CI diagnosis.
- Do not expose secrets, credentials, or private logs in artifacts.
- Keep least-privilege workflow permissions. Add write permissions only when a step requires them.
- Do not silently broaden trigger branches, schedules, permissions, or artifact retention.
- Explain and validate every trigger, schedule, retention, or permission change.
- Keep storage cleanup conservative. Do not reduce retention or the minimum retained run count without explicit approval.
- Before changing CI claims or workflow behavior, verify the workflow file directly rather than relying on planning documents.
- After editing workflows, validate YAML syntax and review triggers, permissions, action versions, cache keys, artifact paths, and shell quoting.
