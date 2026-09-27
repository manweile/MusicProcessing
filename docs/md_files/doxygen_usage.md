<!-- markdownlint-disable MD033 -->

# Doxygen

## Purpose

I started using Doxygen in university, found I like it and continue to use it privately.

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

## Doxygen Configuration

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
# Doxygen will assume all entities in documentation are documented, even if no documentation was available.
# This will also disable the warnings about undocumented members that are normally produced when WARNINGS is set to YES.
EXTRACT_ALL            = YES

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

# Doxygen will sort the brief descriptions of file, namespace and class members alphabetically by member name.
SORT_BRIEF_DOCS        = YES

# Doxygen will sort the (brief and detailed) documentation of class members so that constructors and destructors are listed first.
# Requires SORT_BRIEF_DOCS and SORT_MEMBER_DOCS set to yes (which is their default values)
SORT_MEMBERS_CTORS_1ST = YES

# List is created by putting \test commands in the documentation.
# This will also cause duplicate entries when yes, as @test is present in the test files;
# Possibly a bug?
GENERATE_TESTLIST      = NO
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
# Need src & tests directories for API documentation, md files to supply html content and links to work, and the dox file for custom landing page.
# This project displays documented py files, and uses md files via the dox file.
INPUT                  = D:/MusicProcessing/src \
                         D:/MusicProcessing/tests \
                         D:/MusicProcessing/main.py \
                         D:/MusicProcessing/index.dox

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
# Requires that the tag GENERATE_HTML is set to YES (default).
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

Doxygen requires this custom page source file type to be:

- .dox
- .txt
  - files to have comments in C/C++ style
- .md
  - files to have comments files as Markdown

## Documenting the Code

I prefer using [python doc strings](https://doxygen.nl/manual/docblocks.html#pythonblocks) &<br>
doxygen [javadoc style](https://en.wikipedia.org/wiki/Javadoc) `@` [special commands](https://doxygen.nl/manual/commands.html).<br>
Eg.

```python
'''
@brief Wrapper for function that generates a csv containing full file path for an extension

@details If start_path is not supplied, uses the class top level directory path.<br>
If file extension is not supplied, uses the preset audio types module list.

@param file_ext {str} The file extension want file paths for.
@param start_path {str} The starting point of the directory walk.
'''
```

See the [Python Instructions markdown](../../.github/instructions/python.instructions.md) for more details.
