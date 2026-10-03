<!-- markdownlint-disable MD033 -->

# API Documentation {#api_documentation}

API documentation provides a single source of truth and can give you rick extraction & visualization features.

## Purpose

I started using Doxygen in university, found I like it and continue to use it privately.<br>
I don't have as much experience with GraphViz, but really like it for complex projects.

## Doxygen

Doxygen is a free, open-source tool that builds organized project documentation straight from comments written inside source code.<br>
Source and documentation: [Doxygen](https://www.doxygen.nl)

## Graphviz

Graphviz is open source graph visualization software.<br>
Graph visualization is a way of representing structural information as diagrams of abstract graphs and networks.<br>
It has important applications in networking, bioinformatics, software engineering, database and web design, machine learning,
and in visual interfaces for other technical domains.<br>
Source and documentation: [Graphviz](https://graphviz.org/)

## Download

Windows installer: [Doxygen Download Page](https://www.doxygen.nl/download.html) to install Doxygen on your system.<br>
Windows installer: [Graphviz](https://graphviz.org/download/) if you want Doxygen to generate class hierarchy
and collaboration diagrams using the HAVE_DOT option.

## Install Steps

Doxygen:

- Run the setup file and follow the on-screen prompts in the installation wizard.
- Check the option to add Doxygen to your system PATH environment variable during setup so you can run it from any command prompt.

GraphViz:

- Run the installer
- add the bin folder to your system PATH environment variable

Run these commands from a Windows PowerShell terminal at the repository root to confirm that Doxygen and Graphviz Dot are available on `PATH`:

```powershell
PS D:/MusicProcessing> doxygen --version
PS D:/MusicProcessing> dot -V
```

## GraphViz Configuration

Nothing really, just add the executable to your PATH variable.

## Doxygen Configuration

First of all, add the executable to your PATH variable.<br>
Create a template configuration file from the repository root by running `doxygen -g`.<br>
Note that values that contain spaces should be placed between quotes (" ").<br>
Note that pathing uses `/`, since it will work on both Windows and Linux, and on Windows, you will not have to escape backslashes.

Modify the following defaults in the `Doxyfile` that was created in the repository root.

### Project Related Configuration Options

```text
# Text that appears at top of every generated html page, in header area.
PROJECT_NAME           = "Music Processing Project"

# Note: Using Semantic Versioning starting at 1.0.0, per semver.org in `MAJOR.MINOR.PATCH` format.
# Appears to right of project name in generated html header area.
PROJECT_NUMBER         = 1.0.0

# Short, one-sentence description of your software project, appears underneath project name in header area.
PROJECT_BRIEF          = "Python Project for Audio file collections Metadata"

# Where generated html will created.
# Since html is default output, directory /html would be created if necessary.
OUTPUT_DIRECTORY       = D:/MusicProcessing

# Includes brief member descriptions after the members that are listed in the file and class documentation (similar to Javadoc).
BRIEF_MEMBER_DESC      = NO

# Also don't want brief description of a member or function prepended before the detailed description.
# Brief descriptions will be completely suppressed if BRIEF_MEMBER_DESC is no & HIDE_UNDOC_MEMBERS is no (which is default value).
REPEAT_BRIEF           = NO

# Hides long, ugly, or sensitive folder paths from your final documentation.
# Requires that the tag FULL_PATH_NAMES is set to YES (which is default value).
STRIP_FROM_PATH        = D:/MusicProcessing/docs

# By default Python docstrings are displayed as preformatted text and Doxygen's special commands cannot be used
# and the contents of the docstring documentation blocks are not shown as Doxygen documentation.
# This project does NOT use python docstrings.
PYTHON_DOCSTRING       = NO

# Set to YES if your project consists of Java or Python sources only.
# Doxygen will then generate output that is more tailored for that language.
# For instance, namespaces will be presented as packages, qualified scopes will look different, etc.
OPTIMIZE_OUTPUT_JAVA   = YES

# Selects extra parsers (c is default) to use depending on the extension of the files parsed.
# This project is using markdown files.
EXTENSION_MAPPING      = md=md

# This is only relevant in cases where backticks are used.
# If enabled, Doxygen treats text in comments as Markdown formatted, and where Doxygen's native markup format conflicts with that of Markdown.
# In Doxygen, native markup style allows a single quote to end a text fragment started with a backtick, and then treat it as a piece of quoted text.
# In Markdown, such text fragment is treated as verbatim and only ends when a second matching backtick is found.
# Doxygen's native markup format requires double quotes to be escaped when they appear in a backtick section, Markdown does not.
# Requires that the tag MARKDOWN_SUPPORT is set to YES (the default value).
MARKDOWN_STRICT        = NO

# Specifies the algorithm used to generate identifiers for the Markdown headings.
# Requires that the tag MARKDOWN_SUPPORT is set to YES (the default value).
# GITHUB uses the lower case version of title with any whitespace replaced by '-' and punctuation characters removed.
# This project needs GITHUB for internal link compatibility in the markdown files, so links work in both environments.
MARKDOWN_ID_STYLE      = GITHUB
```

### Build Related Configuration Options

```text
# All private members of a class will be included in the documentation.
EXTRACT_PRIVATE        = YES

# Documented private virtual methods of a class will be included in the documentation.
EXTRACT_PRIV_VIRTUAL   = YES

# All members with package or internal scope will be included in the documentation.
EXTRACT_PACKAGE        = YES

# All static members of a file will be included in the documentation.
EXTRACT_STATIC         = YES

# All anonymous namespaces members will be extracted and appear in the documentation.
# Anonymous namespaces will be called 'anonymous_namespace{file}', where file is base name of script containing the anonymous namespace.
EXTRACT_ANON_NSPACES   = YES

# Doxygen will hide all undocumented members inside documented classes or files.
# This option requires EXTRACT_ALL to be NO (the default value) to have effect.
HIDE_UNDOC_MEMBERS     = YES

# Doxygen will sort the brief descriptions of file, namespace and class members alphabetically by member name.
SORT_BRIEF_DOCS        = YES

# Doxygen will sort the (brief and detailed) documentation of class members so that constructors and destructors are listed first.
# Requires SORT_BRIEF_DOCS and SORT_MEMBER_DOCS set to yes (which is their default values)
SORT_MEMBERS_CTORS_1ST = YES

# List is created by putting \test commands in the documentation.
# This will also cause duplicate entries when yes, as @test is present in the test files;
# Possibly a bug?
GENERATE_TESTLIST      = NO

# Set tag to NO to disable the list of files generated at the bottom of the documentation of classes and structs.
# Because we are using md files for sub-pages, need this to be NO, else get get an empty md_file directory page in html output.
SHOW_USED_FILES        = NO
```

### Warning and Progress Message Configuration Options

```text
# May not need WARN_NO_PARAMDOC & WARN_IF_UNDOC_ENUM_VAL set; if EXTRACT_ALL is yes, both of these are disabled

# Get warnings for functions that are documented, but have no documentation for their parameters or return value.
WARN_NO_PARAMDOC       = YES

# warn about undocumented enumeration values.
WARN_IF_UNDOC_ENUM_VAL = YES

# Sets how to handle warnings, primarily used in continuous integration pipelines to stop bad/incomplete documentation being merged.
# FAIL_ON_WARNINGS_PRINT is best used with WARN_LOGFILE set.
# FAIL_ON_WARNINGS_PRINT will continue running and at the end of the process will return a non-zero status,
# warning messages will be shown at end of the run in terminal and in the defined file (old entries will be overwritten).
WARN_AS_ERROR          = FAIL_ON_WARNINGS_PRINT

# Specifies a file to which warning and error messages should be written.
# In case the file specified cannot be opened for writing the warning and error messages are written to standard error.
WARN_LOGFILE           = D:/MusicProcessing/doxygen.log
```

### Input Files Configuration Options

```text
# Specifies the files and/or directories that contain documented source files, and if the input contains directories, can use FILE_PATTERNS.
# Need src and tests directories & main.py for API documentation, md files to supply landing page content.
# This project displays documented py files, and uses md files.
INPUT                  = D:/MusicProcessing/src \
                         D:/MusicProcessing/tests \
                         D:/MusicProcessing/main.py \
                         D:/MusicProcessing/README.md \
                         D:/MusicProcessing/docs/md_files/Environment.md \
                         D:/MusicProcessing/docs/md_files/Examples.md \
                         D:/MusicProcessing/docs/md_files/Documentation.md \
                         D:/MusicProcessing/docs/md_files/Testing.md \
                         D:/MusicProcessing/docs/md_files/Workflow.md

# The default file patterns list is much longer, just trimming it down to what the project actually uses so there is no oops.
FILE_PATTERNS          = *.py \
                         *.md

# Specify whether or not subdirectories should be searched for input files as well, oF course we want everything
RECURSIVE              = YES

# If INPUT tag contains directories, use to specify one or more wildcard patterns to exclude certain files from those directories.
# The github instructions md files are not part of documentation.
EXCLUDE_PATTERNS       = */instructions/*.md

# Refers to the name of a markdown file that is part of the input, its contents will be placed on the main page (index.html).
# Project is on Github, and I want to reuse README.md as introduction page in generated html.
USE_MDFILE_AS_MAINPAGE = D:/MusicProcessing/README.md
```

### HTML Output Configuration Options

I don't like how the default Doxygen css configures:

- authour, version, date and copyright alignment - want them in compact horizontal rows
- image alignment - want all images aligned to left
- documentation only directories - if they don't contain listed sources, want them hidden

You can use the list as a Copilot prompt to create the file.<br>
Create the css file in the repository root. Specify the css file location in `Doxyfile`.

```text
# Specify additional user-defined cascading style sheets that are included after the standard style sheets created by Doxygen.
# Requires that the tag GENERATE_HTML is set to YES (the default value).
HTML_EXTRA_STYLESHEET  = D:/MusicProcessing/doxygen-custom.css

# Full control over the layout of the generated HTML pages may require disabling the index.
# Set to YES turns off the condensed index (tabs) at top of each HTML page.
# Tabs in index contain same information as navigation tree.
# Requires that the tags GENERATE_HTML and GENERATE_TREEVIEW are set to YES (their default values).
DISABLE_INDEX          = YES

# Sets the side bar to extend to the full height of the window.
# Setting this to YES gives a layout similar to https://docs.readthedocs.io site.
# Gives more room for contents, but less room for the project logo, title, and description.
# Requires that the tags GENERATE_HTML and GENERATE_TREEVIEW are set to YES (their default values).
FULL_SIDEBAR           = YES

# Will show the specified enumeration values besides the enumeration mnemonics.
SHOW_ENUM_VALUES       = YES
```

### laTeX Output Configuration Options

```text
# I don't use LaTex
GENERATE_LATEX         = NO
```

### Diagram Generator Tools Configuration Options

Doxygen will give you nice graph images in the html automatically with theses settings:

```text
# Doxygen will assume the dot tool (Graphviz) is installed & available from the path.
# I do want those nice interactive images.
HAVE_DOT               = YES

# Specifies the number of dot invocations Doxygen is allowed to run in parallel. 10 works well for my cpu.
# Requires that the tag HAVE_DOT is set to YES.
DOT_NUM_THREADS        = 10

# Generates a call dependency graph for every global function or class method.
# Requires that the tag HAVE_DOT is set to YES.
CALL_GRAPH             = YES

# Generates a caller dependency graph for every global function or class method.
# Requires that the tag HAVE_DOT is set to YES.
CALLER_GRAPH           = YES

# Set the image format of the images generated by dot. I prefer svg.
# Requires that the tag HAVE_DOT is set to YES.
DOT_IMAGE_FORMAT       = svg

# If DOT_IMAGE_FORMAT is set to svg, enables generation of interactive SVG images that allow zooming and panning.
# Requires that the tag HAVE_DOT is set to YES.
INTERACTIVE_SVG        = YES

# Specify the path where the dot tool can be found.
# Requires that the tag HAVE_DOT is set to YES.
DOT_PATH               = "C:/Program Files/Graphviz/bin"

# Set the maximum number of nodes that will be shown in the graph.
# With 100, I have not seen any truncation.
# Requires that the tag HAVE_DOT is set to YES.
DOT_GRAPH_MAX_NODES    = 100
```

#### External Dot Files

If you want to use the `@dotfile` tag to specify an interactive image in the documentation, you need to create an external dot file.

A reusable Copilot prompt is:

```text
Inspect main.py, looking at the top level script environment entry point `if name == "main":`, and the module entry function `main(args)`.
Create a dot file named flow.dot in the /docs/dot_files directory.
Review every edge and node against the current python implementation.
The draft is a starting point, not a source of truth.
Render the graph with Graphviz and inspect the result for missing paths, incorrect ordering, clipped labels, or an unreadable layout.
```

Once you are satisfied with the dot file, png and svg images,
add `@dotfile flow.dot "Application startup and task flow"` to the main function documentation block.<br>
Doxygen will use the dot file to generate your image that is embedded in the html output.<br>
Precede the main definition with `## @name Application Entry Point`, followed by `# @{` and succeed it with `## @}`.<br>
This will apply a custom label to the function so it is not buried with the rest of the main.py functions.

```python
## @name Application Entry Point
# @{
def main(args):
    '''
    @brief Module entry point.

    @details Takes command line arguments and executes per arguments.

    @dotfile flow.dot "Application startup and task flow"

    @param args {argparse.Namespace} Arguments for execution.

    @exception {NotImplementedError} Indicates a subcommand has not been implemented.
    @exception {Exception} Handles unforeseen errors.
    '''

   ...

## @}
```

Then set the following:

```text
# Specify one or more directories that contain dot files that are included in the documentation (see the \dotfile command).
# Requires that the tag HAVE_DOT is set to YES.
DOTFILE_DIRS           = D:/MusicProcessing/docs/dot_files
```

## List configuration Changes

Run `doxygen -x Doxyfile` to list the configuration changes from Doxygen defaults.

## Custom Pages

The easiest way to have a main page is to create a separate file for [custom pages](https://www.doxygen.nl/manual/additional.html#custom_pages).

Doxygen requires this custom page source file type to be one of dox, txt (files to have comments in C/C++ style),
and md (files to have comments files as Markdown)

This is NOT what I want.<br>
What I do want is:

- have my markdown files supply content for the Doxygen landing page
- have my markdown files still readable as markdown on Github

The secret, according to Google, is using invisible HTML comments or standard Markdown headers that both systems process elegantly.

### Steps

1. in root README.md, as first line, `<!-- @mainpage Music Processing Project -->`. Lets Doxygen know this is the homepage.
2. to link the sub-pages, add `* [MD Title](relpath/to/markdown.md) <!-- @subpage md_title -->` to create a list.
   1. add as many as you have sub-pages you want in Doxygen output.
   2. the `* [MD Title](path/to/markdown.md)` is standard markdown hyperlink to enable native file navigation on GitHub
   3. the `<!-- @subpage md_title -->` is embedded Doxygen `@subpage` command enclosed in HTML comment to structure the hosted sidebar tree hierarchy.
   4. GitHub renders the visible link text while ignoring the HTML comment,
   whereas the Doxygen compiler parses the comment tags to nest the target page hierarchically
3. For every sub-page markdown, as the first line, add matching Doxygen ID: `<!-- @page md_title MD Title -->`
   1. where `md_title` matches the `@subpage` ID and `MD Title` matches the `[MD Title]` hyperlink title from the sub-page link in README.md footer.
4. Finalize Doxyfile Settings
   1. Include README.md and sub-page markdown files in INPUT TAG
   2. Point Doxygen to your README as the base index: `USE_MDFILE_AS_MAINPAGE = PATH/TO/README.md`
   3. Ensure native markdown layout parsing is on: `MARKDOWN_SUPPORT       = YES`
5.

## Documenting the Code

I prefer using [python doc strings](https://doxygen.nl/manual/docblocks.html#pythonblocks) &<br>
doxygen [javadoc style](https://en.wikipedia.org/wiki/Javadoc) `@` [special commands](https://doxygen.nl/manual/commands.html).<br>

### Package File Example

```python
'''
@package src.audio_info
@file src/audio_info/__init__.py
@author Gerald Manweiler

@brief Package for audio information processing.

@details Exposes audio-information classes through a single package interface.

@version 1.0.0
@date 2026-09-21

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Local Module Classes
from src.audio_info.audio_art import AudioArt               # Exposes audio artwork operations.
from src.audio_info.audio_metadata import AudioMetadata     # Exposes audio metadata operations.
from src.audio_info.audio_playlist import AudioPlaylist     # Exposes audio playlist operations.
from src.audio_info.audio_utilities import AudioUtilities   # Exposes audio utility operations.

## @var __all__
# @brief Exposes class for importing by other modules.
# @details  In modules needing the class, add `from src.audio_info.audio_art import AudioArt`
# @details  In modules needing the class, add `from src.audio_info.audio_metadata import AudioMetadata`
# @details  In modules needing the class, add `from src.audio_info.audio_playlist import AudioPlaylist`
# @details  In modules needing the class, add `from src.audio_info.audio_utilities import AudioUtilities`
__all__ = [
    "AudioArt",
    "AudioMetadata",
    "AudioPlaylist",
    "AudioUtilities"
]
```

### Module File Example

```python
'''
@module errors
@file errors.py
@author Gerald Manweiler

@brief Defines the errors module

@details Defines the custom exceptions used in the MusicProcessing module.

@note This implementation does not require garbage collection or logging functionality.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''


class MusicProcessingException(Exception):
    '''
    @brief Base class for any MusicProcessing Exception

    @details Base class for all custom exceptions in the MusicProcessing module.
    '''

    def __init__(self, message="A MusicProcessingException occurred"):
        '''
        @brief Initializes the MusicProcessingException class.

        @details Initializes the MusicProcessingException with the provided error message.

        @param message {str} The error message.
        '''

        # logic ...
```

### Class File Example

```python
'''
@class AudioPlaylist
@file audio_playlist.py
@author Gerald Manweiler

@brief Defines the audio playlist class.

@details Defines methods for reading and updating M3U playlists for the MusicProcessing project.

@version 1.0.0
@date 2026-09-22

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# import statements ...

# module level variables & constants

## @var logger
# @brief Logger instance for the module.
# @details Sets the logger name to the current module name.
logger = logging.getLogger(__name__)

# ...

## @var directory
# @brief Directory processing instance.
# @details Provides directory processing functionality.
directory = DirectoryProcessing()

## @var DELIMITER
# @brief M3U field delimiter.
# @details Separates duration and file name values in EXTINF playlist entries.
DELIMITER = ","


class AudioPlaylist():
    '''
    @brief Defines the audio playlist processing class.

    @details Provides methods that update M3U playlist entries for the project's music collection.
    '''

    def __init__(self) -> None:
        '''
        @brief Initializes the AudioPlaylist class.

        @details Initializes an AudioPlaylist instance without instance-specific state.
        '''

        pass


    def get_audio_name(self, line: str) -> str:
        '''
        @brief Gets an audio file name from an EXTINF line.

        @details Converts WMA and M4A file extensions to MP3.<br>
        @details Parses EXTINF entries in the form `#EXTINF:N,<name>.<ext>`, where N is a song duration, -1, or 0.<br>
        @details Supports MP3, M4A, and WMA file extensions.

        @param line {str} Line of text read from an M3U file containing an EXTINF tag.
        @return audio {str} Audio file name with extension.

        @exception PlaylistError Indicates an error occurred in playlist class.
        @exception Exception A common baseclass exception to handle unforeseen errors.
        '''

        # logic ...
```

### Main File Example

```python
#!/usr/bin/env python3
'''
@file main.py
@author Gerald Manweiler

@brief Music Processing project executable script.

@details Run this script with appropriate input arguments to process audio files.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# imports ...

# module level variables & constants ...

# custom class(s) ...

# standalone defs ...

## @name Application Entry Point
# @{
def main(args) -> int:
    '''
    @brief Module entry point.

    @details Takes command line arguments and executes per arguments.

    @dotfile flow.dot "Application startup and task flow"

    @param args {argparse.Namespace} Arguments for execution.

    @return exit_code {int} Process exit code for the requested subcommand.

    @exception {NotImplementedError} Indicates a subcommand has not been implemented.
    @exception {Exception} Handles unforeseen errors.
    '''

    # logic ...

  ## @}


  if __name__ == "__main__":
    '''
    @brief Top level script environment entry point.

    @details Sets up argument parsing and subcommand handling.

    @note Any input file paths that contain spaces must be enclosed in quotes.

    @exception {Exception} Handles unforeseen errors.
    '''

    # logic ...
```
