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
If file extension is not supplied, uses the preset audio types module list.
@param file_ext {str} The file extension want file paths for.
@param start_path {str} The starting point of the directory walk.
'''
```
#### Python doc strings and special commands
Since I hate using the exclamation point ```'''! ... '''``` so the special commands will work,
I set PYTHON_DOCSTRING = NO

#### Python Output
Since this project is in python, I set OPTIMIZE_OUTPUT_JAVA = YES

