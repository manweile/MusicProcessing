<!-- markdownlint-disable MD033 MD041 -->

# Environment

## Purpose

This project will use VS Code and ESP-IDF toolchain.

I use VS Code because it's the devil I know and like. I have used it professionally and privately for 10 years and counting.

- Visual Studio is overkill, extensions not as good
- Eclipse GUI is all around too finicky (set up, usage, etc.)

## Python Install

### Install System Prerequisites

- [Python](https://www.python.org/downloads/windows/)
- [Git for Windows](https://github.com/git-for-windows/git/releases/latest)

## VS Code Setup

### Required Extensions

- ipsum lorem

### LAUNCH json

launch.json ipsum lorem

### TASKS json

tasks.json is a configuration file used to automate repetitive development workflows and integrate external tools directly into the editor.

- Documenting
  - Create Doxygen Documentation: runs the Doxygen command to generate documentation based on the configuration specified in the Doxyfile
  - Open Doxygen Documentation: opens the generated Doxygen documentation in Firefox
  - Generate Program Flow Image: runs Graphviz 'dot' command on repository's flow.dot file, writes program_flow.png into same dot_files directory.
- Terminal
  - Open Windows Terminal PowerShell: opens a new instance of Windows Terminal (wt.exe) with a PowerShell session, starting in the workspace folder.

### Github Instructions

The instructions md files automatically configure and guide the behavior of GitHub Copilot.<br>
They act as persistent background rules that force the AI to follow your team's exact coding standards, frameworks,
and architecture decisions without you needing to type them into every chat prompt.

The global file is `copilot-instructions.md` and lives at `/.github`.<br>
It's behaviour is injected into every single prompt or inline request across the entire repository, regardless of what file you are editing.

The scoped files are at `/.github/instructions` and need an `applyTo` glob pattern file specifying when they apply.

### Github Workflows

GitHub workflow YAML files define automated processes for your code repository.<br>
They act as the "instruction manuals" for GitHub Actions, telling GitHub exactly when and
how to automatically build, test, package, or deploy your project.<br>
These files must be saved in the `.github/workflows/` directory of your repository to work.

## External Tools

### FFMPEG

ffmpeg and ffprobe ipsum lorem

### Doxygen

Doxygen is a free, open-source tool that builds organized project documentation straight from comments written inside source code.<br>
Source and documentation: [Doxygen](https://www.doxygen.nl)

### Graphviz

Graphviz is open source graph visualization software.<br>
Graph visualization is a way of representing structural information as diagrams of abstract graphs and networks.<br>
It has important applications in networking, bioinformatics, software engineering, database and web design, machine learning,
and in visual interfaces for other technical domains.<br>
Source and documentation: [Graphviz](https://graphviz.org/)
