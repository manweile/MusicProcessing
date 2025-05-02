# Doxygen usage in Music Process Project
## Documentation Structure
### Custom Pages
The easiest way to have a main page is to create a separate file for [custom pages](https://www.doxygen.nl/manual/additional.html#custom_pages).

Doxygen requires this custom page source file type to be:
- .dox
- .txt
  - files to have comments in C/C++ style
- .md
  - files to have comments files as Markdown

### Documenting the Code
I prefer using [python doc strings](https://doxygen.nl/manual/docblocks.html#pythonblocks) & doxygen [javadoc style](https://en.wikipedia.org/wiki/Javadoc) "at sign" [special commands](https://doxygen.nl/manual/commands.html).
Eg.
```
'''
@brief Wrapper for function that generates a csv containing full file path for an extension
@details If start_path is not supplied, uses the class top level directory path.
@details If file extension is not supplied, uses the preset audio types module list.
@param file_ext {str} The file extension want file paths for.
@param start_path {str} The starting point of the directory walk.
'''
```
#### Use of @details special command
If you do supply another details command for the next line, then both lines will be concatenated until another command is encountered.
as in:
```
If start_path is not supplied, uses the class top level directory path. If file extension is not supplied, uses the preset audio types module list.
```
vs.
```
If start_path is not supplied, uses the class top level directory path.
If file extension is not supplied, uses the preset audio types module list.
```
#### Use of @var special command
I strongly suspect the @var special command is slightly buggy.
In any case, it is very particular in how you use it.

- DO NOT USE IT IN PYTHON DOC STRINGS!!!
  - you not will not get ANY html output
- must use a double hash mark followed by singles for subsequent special commands
- your variable must be an immutable type for the typedef to be output in the html
- you must use @brief to get a brief description in the variables html output
- you must use @details to get detailed description in the variable documentation html output

Eg.
```
'''
@var __all__
@brief Exposes variable for importing by other modules.
@details  In modules needing the directory, add `from src.generated_files import generated_files`
'''
```
will not produce ANY html output, but this will:
```
## @var __all__
# @brief Exposes variable for importing by other modules.
# @details  In modules needing the directory, add `from src.generated_files import generated_files`
```
##### Weakly typed vs immutable variables
Weakly typed variables  will NOT get the typedef listed in the html output, but immutable typed variables will.
Eg.
```
## @var generated_files
# @brief Path to where files created by the project are stored.
# @details Getting the directory name for importing means will not need a hard coded "magic spell" else where in codebase.
generated_files = os.path.dirname(os.path.abspath(__file__))
```
results in:
```
  generated_files = ""
  Path to where files created by the project are stored.
```
whereas:
```
## @var generated_files
# @brief Path to where files created by the project are stored.
# @details Getting the directory name for importing means will not need a hard coded "magic spell" else where in codebase.
generated_files = ""
generated_files = os.path.dirname(os.path.abspath(__file__))
```
results in:
```
str generated_files = ""
    Path to where files created by the project are stored.
```
#### Python doc strings and special commands
Since I hate using the exclamation point ```'''! ... '''``` to allow special commands functionality, I set PYTHON_DOCSTRING = NO

#### Python Output
Since this project is in python, I set OPTIMIZE_OUTPUT_JAVA = YES