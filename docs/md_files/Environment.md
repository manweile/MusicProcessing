<!-- markdownlint-disable MD033 MD041 -->

# Project Environment {#project_environment}

## Purpose

The primary tools this project will use are VS Code and Python, Ffmpeg and Mutagen.

I use VS Code because it's the devil I know and like.<br>
I have used it professionally and privately since 2016.<br>
Python is a great compromise between ease of use and capability.<br>
Ffmpeg/Ffprobe/Mutagen are the troika this project uses for the heavy lifting.

## Monitors

I have an inverted T, four monitor configuration. All four monitors are 1920 by 1080 pixel resolution.<br>
The upper centre monitor is the primary display. The lower row monitors are secondary displays.<br>
The upper centre monitor is at 100% scaling. The lower row monitors are all at 125% scaling.<br>
The upper centre monitor is horizontally aligned with respect to the lower centre monitor.<br>

| Physical Position | Usage     | Scaling | Logical Dim | Home XY Coord  | Boundary (Left,Top) to (Right,Bot) |
| ----------------- | --------- | ------- | ----------- | -------------- | ---------------------------------- |
| Upper Centre      | Primary   | 100%    | 1920 x 1080 | (0, 0)         | (0, 0) to (+1920, +1080)           |
| Lower Left        | Secondary | 125%    | 1536 x 864  | (-1344, +1080) | (-1344, +1080) to (+192, +1944)    |
| Lower Centre      | Secondary | 125%    | 1536 x 864  | (+192, +1080)  | (+192, +1080) to (+1728, +1944)    |
| Lower Right       | Secondary | 125%    | 1536 x 864  | (+1728, +1080) | (+1728, +1080) to (+3264, +1944)   |

Configuration info is pertinent to the Python GUI Debugger launch.json task; I like the GUI to display in lower-left monitor when debugging.<br>
The main GUI app code is coupled to this configuration and the launch.json task using it; refer to both for details.

## Git For Windows

[Git for Windows](https://gitforwindows.org/) offers a lightweight set of tools, bringing the full feature set of the Git SCM to Windows.<br>
Provides appropriate user interfaces for experienced Git users and novices alike.

## Python

[Python](https://www.python.org/) a high-level, general-purpose, interpreted programming language.<br>
Renowned for its clear English like syntax and strict reliance on readability.<br>
You can find full documentation at the link.

### Required Python Modules

This project **requires**  the following Python Modules:

```text
# project external library dependencies
## dependency of tqdm
colorama>=0.4.6
## dependency of yaspin
termcolor>=2.3.0

# project external libraries
## open-source, cross-platform GUI toolkit for desktop applications with graphical user interfaces
wxpython>=4.2.3
# to read, write, and manipulate audio metadata across many file formats
mutagen>=1.47.0
# to sanitize and validate filenames and file paths across different operating systems
pathvalidate>=3.2.3
# to add customizable progress bars to loops, iterables, and long-running tasks
tqdm>=4.67.1
# to create animated loading spinners in the terminal
yaspin>=3.1.0
```

Save the required modules in `requirements.txt` at root level. The Github remote & local CI and  will need them.<br>
Technically, the dependencies do not need to be listed first; doing so is just future proofing in case one of them becomes a legacy package.<br>
The `>=` is also future proofing, but in this case for OS & Python version updates/upgrades.

Install individually via pip, eg:

```powershell
pip install mutagen==1.47.0
```

or

```powershell
python -m pip install mutagen==1.47.0
```

or en masse:

```powershell
pip install -r requirements.txt
```

## FFMPEG & FFPROBE

[FFmpeg](https://www.ffmpeg.org/about.html) is the leading free & open source multimedia framework.<br>
It is able to decode, encode, transcode, mux, demux, stream, filter and play pretty much anything that humans and machines have created.<br>
It supports the most obscure ancient formats up to the cutting edge.

FFmpeg compiles and runs across Linux, Mac OS X, Microsoft Windows, the BSDs, Solaris, etc.

I am currently using version 8.01 on both my Windows 10 and Ubuntu hardware.<br>
The CI is using version 8.1; it's easier for the workflow to acquire programmatically.

The mismatch does require cognizance in the metadata test suite.<br>
Version 8.1 and up has slightly different values in some situations. Refer to the metadata test suite test case doc header notes.

### FFMPEG

[FFMPEG](https://www.ffmpeg.org/ffmpeg.html) is the "Engine" — used to manipulate, edit, and convert media files.

### FFPROBE

[FFPROBE](https://www.ffmpeg.org/ffprobe.html) is the "Inspector" — used to look inside media files and gather technical data.

## Mutagen

[Mutagen](https://mutagen.readthedocs.io/en/latest/) Mutagen is a Python module to handle audio metadata.<br>
It supports ASF (wma), FLAC, MP4 (m4a), and MP3 audio files. All versions of ID3v2 are supported.<br>
It works with Python 3.10+ on Linux, Windows and macOS, and has no dependencies outside the Python standard library.

## VS Code

[VS Code](https://code.visualstudio.com/). Follow the links.

### Extensions

To export a list of extensions in use:

```powershell
code --list-extensions --show-versions > D:\MusicProcessing\docs\extensions\extensions.txt
```

To install from extensions.txt:

```powershell
Get-Content -Path "D:\MusicProcessing\docs\extensions\extensions.txt" | ForEach-Object { code --install-extension $_ --force }
```

**Caveat Emptor**
I make no promises about usability if you install the extensions as is, I can't know whats on *your* system after all.<br>
I also use VS Code extensions for C/C++ development, so there are extensions dependent on that in my list.

I am reasonably confident VS Code won't turn belly up on you, it's never happened to me when I have installed from an extensions list.

**Note** VS code needs to be in your system PATH.

The extensions I regard as required or essential:

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

### Launch json

Launch.json is a configuration file used to set up and customize debugging and execution environment details for your applications.<br>
Configures what happens when you press the F5 key or hit the "Run and Debug" button.<br>
It is located in the `.vscode`folder at the root of your project workspace.

By default, VS Code tries to automatically run the file you currently have open.<br>
However, many projects require specific parameters to execute correctly. You use launch.json when your application needs:

- A specific entry point (e.g., always starting from a main.py, no matter which file you are currently editing).
  - in CLI mode with requirement to enter subcommands & options
  - in GUI mode
- A currently open file

### Tasks json

Tasks.json is a configuration file used to automate repetitive development workflows and integrate external tools directly into the editor.<br>
Instead of manually opening a terminal and typing commands, you can trigger them with a single keyboard shortcut or from drop down menus.<br>
It is located in the `.vscode`folder at the root of your project workspace.

## Github Instructions

The instructions md files automatically configure and guide the behavior of GitHub Copilot.<br>
They act as persistent background rules that force the AI to follow your team's exact coding standards, frameworks,
and architecture decisions without you needing to type them into every chat prompt.

The global file is `copilot-instructions.md` and lives at `/.github`.<br>
It's behaviour is injected into every single prompt or inline request across the entire repository, regardless of what file you are editing.

The scoped files are at `/.github/instructions` and need an `applyTo` glob pattern file specifying when they apply.

## Github Workflows

GitHub workflow YAML files define automated processes for your code repository.<br>
They act as the "instruction manuals" for GitHub Actions, telling GitHub exactly when and
how to automatically build, test, package, or deploy your project.<br>
These files must be saved in the `.github/workflows/` directory of your repository to work.

## GitHub Local Actions

I regard GitHub Local Actions (GLA) as an essential tool.<br>
It allows you to quickly and efficiently run your workflows locally.<br>
This bypasses the tedium of committing and pushing changes every time you need to test a workflow.<br>
Furthermore, if the workflow needs debugging, you have better tools locally, and you haven't burned Github Action minutes.

GLA uses the nektos/act CLI tool to read your GitHub Actions from your `.github/workflows/*`.<br>
Once nektos/act has the execution path and dependencies, it uses the Docker API to run the necessary containers.

### GLA Requirements

- [GitHub Local Actions](https://marketplace.visualstudio.com/items?itemName=SanjulaGanepola.github-local-actions)
  - [GitHub Local Actions Docs](https://sanjulaganepola.github.io/github-local-actions-docs/)
- [nektos/act](https://github.com/nektos/act)
  - [nektos/act User Guide](https://nektosact.com/)
- [Docker](https://docs.docker.com/engine/)

I'm not going to go into *all* the ins and outs of installing nektos/act and Docker here.<br>
You can find the documentation by following the links.<br>
While it is tedious, it is not overly complex.

I am also not going into how to use both - thats a whole other kettle of fish and well beyond the scope of this document.

### Images and Runners

GLA **requires** a Ubuntu image; easiest way to get an image is via terminal cli: `docker pull <image>`<br>
e.g. `docker pull docker.gitea.com/runner-images:ubuntu-26.04`

Your choice of image is coupled to the workflow(s) that use it; considerations are:

- has all the tools you need (ie like node)
- compatible with python version you want
- compatible with ffmpeg version you want

I'm using Gitea instead of Catthehacker (GLA's default) because:

- Catthehacker is not updating as timely or accurately as Gitea
- Gitea ubuntu-26 is ~500Mb, and allows me to use github actions for checkout, cache, setup-python, and it works with GLA

Once you have the image, GLA can use it for the runner OS.<br>
This requires a `.actrc` file

- on Windows
  - `C:\Users\<User>\.actrc`
- on Ubuntu
  - `~/.actrc`

Add the image to the file: `docker pull docker.gitea.com/runner-images:ubuntu-26.04`

Map the runner label defined in `python-app.yml` ie `runs-on: ubuntu-26.04` to its matching local Docker image in GLA's **Runners** settings.<br>
Ensure the checkbox next to `ubuntu-26.04` is enabled so nektos/act uses the Ubuntu 26.04 container image specified in `.actrc` without prompting.

### Secrets (GITHUB_TOKEN)

GitHub token for local runs: GitHub Actions automatically provides `github.token` to workflows.<br>
GLA and nektos/act need to provide a `GITHUB_TOKEN` secret if the selected workflow or action needs to authenticate with GitHub APIs.

The artifact and workflow cleanup jobs use the token for deletion requests.<br>
Use a token with only the permissions those jobs need, store it in the extension’s Secrets settings, and do not commit it to the repository.

### Options

Configure the following flags in GLA's **Options** settings to test uncommitted changes and speed up local runs:

- **`artifact-server-path`**
  - on Windows: `C:\temp\act-artifacts`
  - on Ubuntu: `/tmp/act-artifacts`
  - Provides a local directory for `actions/cache` and artifact storage when running outside GitHub.
- **`bind`**:
  - `true`
  - Tells act to bind-mount the current worktree directly into the job container instead of copying it,
  allowing local runs to test uncommitted workflow or source changes.
  - *(Note: Set to `false` if you need container-isolated filesystem changes, such as symlinking temporary directories inside Linux.)*
- **`container-options`**
  - on Windows: `-v act-pip-cache:/root/.cache/pip`
  - on Ubuntu:  `-v act-pip-cache:/root/.cache/pip -v /opt/hostedtoolcache:/opt/hostedtoolcache`
  - Mounts persistent Docker volumes so Python toolchains and `pip` wheels (such as `wxPython`) survive across container resets.
- **`pull`**
  - `false`
  - Stops act from checking Docker Hub for newer runner images before every local execution.
- **`reuse`**
  - `true`
  - Keeps the job container alive between runs so system packages (`apt`), FFmpeg binaries, and Python dependencies do not reinstall from scratch.

Without `Detect act` and `bind`, the `python-app.yml` unit-test workflow would overwrite local changes with the commit selected by `github.sha`.<br>
On GitHub Actions, `ACT` is not set, so the normal checkout still runs.

Add this to `python-app.yml` as the very first step in the job:

```yml
    steps:
      # need to detect if running in act (local GitHub Actions runner) to conditionally skip certain steps
      - name: Detect act
        id: detect-act
        run: echo "is-act=ACT:-false" >> "GITHUB_OUTPUT"
```

Every task that should only execute remotely on GitHub—such as repository checkout or cloud cache steps—needs to check `detect-act`:

```yml
if: steps.detect-act.outputs.is-act == 'false'
```
