<!-- @page project_environment Project Environment -->
<!-- markdownlint-disable MD033 MD041 -->

# Project Environment

## Purpose

This project will use VS Code and Python, Ffmpeg and Mutagen.

I use VS Code because it's the devil I know and like. I have used it professionally and privately for 10 years and counting.<br>
Python is a great compromise between ease of use and capability. I have also used it professionally and privately for 10 years and counting.<br>
Ffmpeg/Ffprobe/Mutagen are the troika this project uses for the heavy lifting.

## Git For Windows

[Git for Windows](https://gitforwindows.org/) offers a lightweight, native set of tools, bringing the full feature set of the Git SCM to Windows.<br>
Provides appropriate user interfaces for experienced Git users and novices alike.

## Python

[Python](https://www.python.org/) a high-level, general-purpose, interpreted programming language.<br>
Renowned for its clear English like syntax and strict reliance on readability.<br>
You can find full documentation at the link.

### Required Python Modules

This project **requires**  the following Python Modules:

#### external library dependencies

- colorama==0.4.6                                           # dependency of tqdm
- termcolor===2.3.0                                         # dependency of yaspin

##### required project external libraries

- mutagen==1.47.0                                           # to read, write, and manipulate audio metadata across many file formats
- pathvalidate==3.2.3                                       # to sanitize and validate filenames and file paths across different operating systems
- tqdm==4.67.1                                              # to add customizable progress bars to loops, iterables, and long-running tasks
- yaspin==3.1.0                                             # to create animated loading spinners in the terminal

Install all of them via pip, eg:

```powershell
pip install mutagen==1.47.0
```

or

```powershell
python -m pip install mutagen==1.47.0
```

Save the required modules in `requirements.txt` at root level. The Github CI will need them.

## FFMPEG & FFPROBE

[FFmpeg](https://www.ffmpeg.org/about.html) is the leading free & open source multimedia framework.<br>
It is able to decode, encode, transcode, mux, demux, stream, filter and play pretty much anything that humans and machines have created.<br>
It supports the most obscure ancient formats up to the cutting edge.<br>
FFmpeg compiles and runs across Linux, Mac OS X, Microsoft Windows, the BSDs, Solaris, etc.

### FFMPEG

The "Engine" — used to manipulate, edit, and convert media files.

### FFPROBE

The "Inspector" — used to look inside media files and gather technical data.

## VS Code Setup

[VS Code](https://code.visualstudio.com/). Follow the links.

### Extensions

To export a list of extensions in use:

```powershell
code --list-extensions --show-versions > D:\MusicProcessing\docs\extensions\extensions.txt
```

The ones I regard as required or essential:

- pretty much anything Python related by Microsoft
- pretty much anything Github related from Github
- Doxygen & GraphViz related
- various file type viewers/support
  - Word doc/ODT
  - Markdown
  - Pdf's
  - Spreadsheets
  - YAML
- Test Adapters & Explorer UI's

The heuristic I use for selection is:

- does it meet my needs
- how many downloads does it have
- is it currently supported

### LAUNCH json

Launch.json is a configuration file used to set up and customize debugging and execution environment details for your applications.<br>
It is located in the `.vscode`folder at the root of your project workspace.<br>
Configures how to run, debug, or interact with your code when you press the F5 key or hit the "Run and Debug" button.<br>
By default, VS Code tries to automatically run the file you currently have open.<br>
However, many projects require specific parameters to execute correctly. You use launch.json when your application needs:

- A specific entry point (e.g., always starting from a main.py, no matter which file you are currently editing).
  - with or without command-line arguments passed into the program.
- A currently open file

### TASKS json

Tasks.json is a configuration file used to automate repetitive development workflows and integrate external tools directly into the editor.<br>
It is located in the `.vscode`folder at the root of your project workspace.<br>
Instead of manually opening a terminal and re-typing commands, you can trigger them with a single keyboard shortcut or from drop down menus.

- Running Tests: Executing test suites like pytest and automatically updating local coverage reports.
- Debugging Glue: paired with launch.json (via the preLaunchTask setting) to automatically build your app right before the debugger launches.

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

### Github Local Actions

I regard  Github local Actions as an essential external tool.<br>
It allows you to quickly and efficiently run your workflows locally,
bypassing the hassle of committing and pushing changes every time you need to test a workflow<br>

#### Requirements

- [Github Local Actions](https://marketplace.visualstudio.com/items?itemName=SanjulaGanepola.github-local-actions)
- [nektos/act](https://github.com/nektos/act)
- [Docker](https://docs.docker.com/engine/)

I'm not going to go into the ins and out of installing nektos/act and Docker here; you can find the documentation by following the links.
