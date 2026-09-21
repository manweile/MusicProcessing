---
applyTo: "README.md,documents/**/*.md"
description: "Use when creating or editing repository documentation outside GitHub customization files."
---

# Markdown Instructions

- All files start with `<!-- markdownlint-disable MD033 -->`
- Follow Line Length Rules below.
- Use ASCII unless the source document already requires a specific non-ASCII character.
- Preserve the existing document hierarchy: one `#` title, `##` major sections, and `###` subsections.
- Keep headings concise, descriptive, and in the existing document's capitalization style.
- Use language-tagged fenced code blocks for commands, configuration, source code, and structured data.
- Use inline code for commands, configuration keys, file paths, component names, and identifiers.
- Use forward slashes in repository paths.
- Keep procedures actionable and ordered with numbered lists when steps must be followed in sequence.
- Use `-` bullet lists for unordered information and concise operational guidance.
- Use tables only when they improve comparison or scanning, such as hardware specifications or configuration values.
- Keep documentation claims evidence-based.
  - Distinguish implemented behavior, planned work, and generated output.
- Treat `./html/` as generated Doxygen output.
  - Do not manually edit it or cite it as authoritative source.
- Prefer extending the existing document structure over creating duplicate documentation for the same workflow.
- When cross-referencing another repository document, use its accurate relative path and update related guidance when a workflow changes.
- After editing Markdown, check links, code-fence balance, heading structure, and line length.

## Line Length Rules

- Keep every Markdown line at or below 150 columns; shorten wording if necessary.
  - Does not apply to:
    1. tables
    2. code fences
    4. links
    5. lists
- If the shortest clear wording still exceeds column 150, break the line after, in this order of preference:
  1. a comma
  2. a semicolon
  3. a coordinating conjunction: "for", "and", "nor", "but", "or", "yet", or "so"
  4. a preposition: "in", "on", "at", "to", "from", "by", "with", "about", "as", "of", or "for"
- If a line is broken, do not append a `<br>` to the end of the line
  - instead start the next line with a lowercase letter
