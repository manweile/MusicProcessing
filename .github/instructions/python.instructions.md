---
applyTo: "**/*.py"
---

# Python Documentation Standards

- All new normal source Python files require a file-level Doxygen block.
- The following Python files do not require a file-level Doxygen block:
  - stub/demo scripts
  - Migration utilities
  - one-off developer tools
  - generated code

## Python

Always use [python doc strings](https://doxygen.nl/manual/docblocks.html#pythonblocks)
& doxygen [javadoc style](https://en.wikipedia.org/wiki/Javadoc) `@` [special commands](https://doxygen.nl/manual/commands.html).

- These Python rules apply only to `.py` files.
- Use paired triple single quotes `''' ... '''` for Python docstrings that are formatted as Doxygen documentation blocks.
  - These docstrings are both valid Python docstrings and the required Doxygen documentation format for this repository.
- Use `#` for inline comments.

## Shared Python Rules

- After the file block, order declarations as follows:
  1. Imports
  2. Module Level Constants
  3. Module Level Variables
  4. Classes
    1. Class function definitions
  5. Functions
  - List items alphabetically within each group or subgroup unless a section below states otherwise.
  - Separate Import, Module Level Constants and Module Level Variables with a blank line.
  - Separate classes from preceding code with 2 blank lines.
  - Separate functions inside classes from preceding code with 2 blank lines.
  - Separate functions outside classes from preceding code with 2 blank lines.
  - In class and function definitions, the Doxygen documentation block is placed immediately after the definition line as the Python docstring.
  - All python files end with a blank line.

## Shared Doxygen Rules

- Use a one-line `@brief`, terminated by a period.
- Leave an empty line after `@brief`.
- Add a `@details` block.
- Follow the Details Block Formatting Rules.
- Use:
  - `@param name {type} description` for input parameters, terminated by a period.
  - `@return name {type} description` when the function returns a specifically named value, terminated by a period.
  - `@return {type} description` when the function returns an unnamed value or expression, terminated by a period.
- Leave an empty line after `@param` and `@return` blocks.
- Omit `@param` entirely for functions with no parameters.
- Omit `@return` entirely for functions that return `None`.
- Use `@exception {type} description` for exceptions raised by the function, terminated by a period.
- Omit `@exception` entirely for functions that do not raise any exceptions.
- All Doxygen documentation blocks in class definitions are followed by 1 blank line.
- All Doxygen documentation blocks in function definitions inside classes are followed by 1 blank line.
- All Doxygen documentation blocks in functions definitions outside of classes are followed by 1 blank line.

## Column Length Rules

- All text in Python source files, including code, comments, and Doxygen documentation, must not exceed column 150.
- Inline comments are denoted by `#` and do not have a period at the end
- For imports:
  - follow the Import Rules for placement of purpose comments.
- For long parameter lists:
  - break parameters across continuation lines using standard Python indentation.
  - align continuation lines with the opening delimiter or use a hanging indent of 4 spaces.

## Details Block Formatting Rules

- Apply these rules to every `@details` block in Python Doxygen comments, including:
  1. File-level documentation blocks
  2. Class documentation blocks
  3. Functions documentation blocks
  4. Standalone functions documentation blocks
- Write each `@details` line as a concise & clear complete sentence ending with a period.
- Keep each `@details` line at or below column 150; shorten wording if necessary.
- If the shortest clear wording still exceeds column 150, break the line after, in this order of preference:
  1. a comma
  2. a semicolon
  3. a coordinating conjunction: "for", "and", "nor", "but", "or", "yet", or "so"
  4. a preposition: "in", "on", "at", "to", "from", "by", "with", "about", "as", "of", or "for"
- If a line is broken, do not append a `<br>` to the end of the line; instead, start the next line with a lowercase letter.
- Do not append a `<br>` to a single line `@details` block.
- Append a `<br>` for lines ending with a period, except for the final line of a multiline `@details` block.
- Leave an empty line after the last line of a `@details` block.

## File Block Rules

- All files start with a Doxygen file header block.
- The first line of the file header must follow the per file type header block rule.
  1. Package Files Header Block rules for package files.
  2. Module Files Header Block rules for module files.
  3. Class Files Header Block rules for class files.
  4. Test Files Header Block rules for test files.
  5. Main Files Header Block rules for the main file.
- Add `@author` Gerald Manweiler, followed by an empty line.
- Add `@brief`
  - `Package ...` in package files
  - `Defines the ... module` in module files
  - `Defines the ... class` in class files
  - `Defines the test ... class` in test files
  - terminate `@brief ...` with a period.
- Add an empty line after `@brief`.
- Add a `@details` block.
  - Follow the Details Block Formatting Rules.
- Add `@version` using Semantic Versioning starting at 1.0.0, per semver.org in `MAJOR.MINOR.PATCH` format.
- Add `@date`, followed by an empty line.
- Add `@copyright` `@showdate "%Y"` GWN Software. All rights reserved.
- Leave one blank line after the file header block and before the first import.

## Package Files Header Block

- Package files are `__init__.py` Python files whose primary purpose is to define a package.
- Their header blocks start with `@package ...` where `...` is the name of the package.
- Their next line is `@file ...` where `...` is the name of the relative file path; eg: `@file src/__init__.py`

## Module Files Header Block

- Module files are non-`__init__.py` Python files whose primary purpose is to define module-level functionality such as helper
  functions, constants, lightweight data containers, or support logic.
- Their header blocks start with `@module ...` where `...` is the module name.
- Their next line is `@file ...` where `...` is the file name - but not the relative file path; eg: `@file module_file.py`

## Class Files Header Block

- Class files are Python files whose primary purpose is to define one main behavioral class.
- Their header blocks start with `@class ...` where `...` is the primary class name.
- Their next line is `@file ...` where `...` is the file name - but not the relative file path; eg: `@file class_file.py`

## Test Files Header Block

- Test files are `test_*.py` Python files whose primary purpose is to define unit tests for the project.
- Their header blocks start with `@class ...` where `...` is the name of the primary test class.
- Their next line is `@file ...` where `...` is the file name - but not the relative file path; eg: `@file test_class_file.py`

## Main File Header Block

- Main files are Python files that serve as the entry point of the application.
- Main files are Python files that serve as the entry point of the application.
- Their header blocks start with `@main ...` where `...` is the name of the main file.
- Their next line is `@file ...` where `...` is the file name - but not the relative file path; eg: `@file main_file.py`

## Import Rules

- Never use wildcard imports (e.g., `from module import *`).
- Never use relative imports (e.g., `from .module import ...`).
- Always use 1 import per line, never combine multiple imports in a single statement.
- Always use absolute imports for local modules in package files.
- all imports have an `# ...` comment where `...` explains the purpose of the import statement.
- The entire import statement plus same line comment must never exceed column 150.
  - use the shortest possible comment that clearly conveys the purpose of the import.
  - if the import statement does not exceed column 61, and the comment is less than 90 characters
    - place the comment after the import statement on the same line, starting at column 61.
  - if the import statement does not exceed column 61, but the comment is 90 characters or more
    - place the comment immediately before the import statement.
  - if the import statement exceeds column 61
    - place the comment immediately before the import statement.
- Group imports in this order:
  1. Python standard modules - the modules installed with Python itself.
  2. third party modules - the modules installed via package managers like pip.
  3. local modules by usage category type- the modules defined within the project itself.
- List imports alphabetically within each subgroup and use consistent comment annotations.
- For all subgroups, imports via `import` come first, followed by `from ... import ...` statements
  - Maintain consistent comment annotations and alphabetical order in `import` and `from ... import ...` statements.
- Leave a blank line after each subgroup.
- Precede each subgroup with:
  - `# Standard Modules`
  - `# Third Party Modules`
  - `# Local Modules <type>`, where `<type>` is one of the following:
    1. `Methods` - functions and procedures defined within the module, Eg. `Local Module Methods` for methods.
    2. `Constants` - constant values defined within the module, Eg. `Local Module Constants` for constants.
    3. `Errors` - custom error classes defined within the module, Eg. `Local Module Errors` for errors.
    4. `Classes` - classes defined within the module, Eg. `Local Module Classes` for classes.

### Module Level Variables and Constants

- Have a Doxygen documentation block for all module level variables and constants.
- In files that contain a class and module level variables or constants, the last module level variable or constant is followed by 2 blank lines.
- The module level variables and constants always follow the logging set up.
- The Doxygen documentation block should include:
  - `## @var <variable_name>` line for specifying the name of the module level variable or constant.
  - `# @brief <description>` line for providing a brief summary of the variable or constant.
  - `# @details <details>` line for providing additional information about the variable or constant.
  - Only module level variables and constants can have multiple `@details` lines if needed.
    - File-level, classes, class functions, and standalone functions documentation blocks can only have a single `@details` line.
  - Each `@details` line should be:
   - be atomically granular
   - be concise
   - be relevant to the variable or constant it describes
   - have a maximum of 150 characters per line
- The final subgroup should be followed by 2 blank lines before the class definition or the next section.
- Module level variables and constants have subgroups with this ordering:
  1. Variables that call functions
  2. Constant literals
  3. Constant Sets
  4. Constant Lists
- within each subgroup, items should be listed in alphabetical order:
- Example:

  ```python
  ## @var directory
  # @brief Directory processing instance.
  # @details Provides directory processing functionality.
  directory = DirectoryProcessing()

  ## @var normalization
  # @brief Audio normalization instance.
  # @details Provides audio normalization functionality.
  normalization = AudioNormalization()

  ## @var subprocess_utils
  # @brief Subprocess utilities instance.
  # @details Provides subprocess utility functionality.
  subprocess_utils = SubprocessUtilities()

  ## @var TPOS
  # @brief ID3 disc-of-set tag.
  # @details Sets TPOS metadata.
  TPOS = "TPOS"

  ## @var TYER
  # @brief ID3 release-year tag.
  # @details Sets TYER metadata.
  TYER = "TYER"

  ## @var MP3_TIME_KEYS
  # @brief ID3 time keys.
  # @details Sets TYER metadata.
  # @details 'TYER' is the preferred key for ID3 time metadata.
  MP3_TIME_KEYS = {
      'TYER',
      'TORY',
      'TDRC',
      'TDOR',
      'TXXX=originalyear'
  }

  ## @var M4A_TIME_KEYS
  # @brief MP4 (m4a) time keys.
  # @details Sets TYER metadata.<br>
  # @details'\xa9day' is the preferred key for MP4 time metadata.
  M4A_TIME_KEYS = {
      '\xa9day',
      '----:com.apple.iTunes:originalyear'
  }


  ```

## Package Files

- Package files are Python files whose primary purpose is to define a package.
- Package files are Python files that expose public names for import by other modules.
- Follow Module Level Variables and Constants rules for placement of purpose comments.
- They may contain import statements for standard, third-party, and local modules.
- Package files have an `__all__` export list to specify which members are accessible when the package is imported.
- The `__all__` export list is always last item in the file.
- `__all__` export lists have a `@details <details>` line for each item, in alphabetical order.
  - Each `@details` line for an `__all__` item should explain how to import the item
  - have a maximum of 150 characters per line
  - Example:

  ```python
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

## Module Files

- Module files are Python files that define the functionality of a specific module within the package.
- Module files are Python files whose primary purpose is to define module-level functionality such as:
  - helper functions, constants, lightweight data containers, or support logic.
- They may contain import statements for standard, third-party, and local modules.
- They may contain module-level variables and constants.
- Follow Module Level Variables and Constants rules for placement of purpose comments.
- They may contain classes and function definitions relevant to the module's purpose.
- They may contain stand alone functions relevant to the module's purpose.

## Class Files

- Class files are Python files whose primary purpose is to define one main behavioral class.
- Class files reside in the `src` directory and its sub-directories, and follow the naming convention `<class_name>.py`.
- They may contain import statements for standard, third-party, and local modules.
- They may contain module level variables and constants.
- Follow Module Level Variables and Constants rules for placement of purpose comments.
- They follow the Class File Garbage Collection rules as described above.
- They follow the Class File Logging Setup rules as described below.
- They contain the class definition and its methods.
- Class files documentation blocks may include code examples using the `@code{.text}` and `@endcode` tags to illustrate command-line usage.

### Class File Garbage Collection

- All class files, excepting test files, must enable garbage collection.
- The class file must import the standard module `gc`.
- The garbage collection setup is placed after the import statements and before any other module-level code.
- The garbage collection setup calls `gc.enable()`.
- The garbage collection enable call is followed by a blank line.
- Example:

```python
import gc                                                   # for garbage collection management
# ... other import statements for standard, third-party, and local modules

gc.enable()

```

### Class File Logging Setup

- All class files, excepting test files, must include a logging setup section.
- The class file must import the standard modules `logging` and `os` modules.
- The class file must import the local module method `add_module_handler`.
- The logging setup is placed after the garbage collection.
- The logging setup defines a module logger named with `__name__`.
- The logging setup defines the module file basename for the logger file handler.
- The logging setup calls `add_module_handler(logger, basename)`.
- The logging setup section is followed by a blank line.
- Example:

```python
## @var logger
# @brief Logger instance for the module.
# @details Set the logger name to the module name.
logger = logging.getLogger(__name__)

## @var basename
# @brief Base name for the logger file handler log file.
# @details Get the module file name from the current file path.
basename = os.path.basename(__file__)

add_module_handler(logger, basename)

```

## Test Files

- Test files are Python files whose primary purpose is to define unit tests for the project.
- Test files are Python files that contain test cases for the classes defined in the project.
- Files named `test_*.py` are implementation-only test sources, not public API.
- test files reside in the `tests` directory and follow the naming convention `test_*.py`.
- Test files are class files and should follow the same header and import rules as regular class files.
- Follow Module Level Variables and Constants rules for placement of purpose comments.
- Test files do not follow the Class File Logging Setup rules.
- Test files documentation blocks may include code examples using the `@code{.text}` and `@endcode` tags to illustrate command-line usage.
- Test files may have a class level `setUpClass` method for initializing test fixtures, with a `@classmethod` decorator.
- Test files may have a class level `tearDownClass` method for cleaning up test fixtures, with a `@classmethod` decorator.
- Test files may have a `tearDown` method for cleaning up individual test cases.
- Test cases are named `test_<functionality>`, where `<functionality>` describes the specific feature or behavior being tested.
- Test cases have an additional tag `@test` in their Doxygen documentation.
  - The `@test` line is placed after the blank line following the`@details` block, and is followed by a blank line.
  - The `@test` tag describes if this is a happy path, edge case, error case, or corner case.
- Test cases using mock objects have an appropriate `@patch` decorator for the mock in the test case.
- It contains the `if __name__ == "__main__":` block to execute the test functionality.
- The `if __name__ == "__main__":` block follows Shared Doxygen rules for function documentation.

## Main File

- The main file is the Python file that serves as the entry point of the application.
- Follow Module Level Variables and Constants rules for placement of purpose comments.
- There is only one main file in the project.
- It contains the `if __name__ == "__main__":` block to execute the main functionality.
- The `if __name__ == "__main__":` block follows Shared Doxygen rules for function documentation.
- It may contain import statements for standard, third-party modules, and local modules.
- It may contain a `__all__` export list to specify the public API of the main file.

### Main File Logging Setup

- The `main.py` file must include a logging setup section.
  - The main file must import the standard modules `logging` and `os` modules.
  - The main file must import the following local modules:
    - `ERROR_LOG_FORMAT`, `LOG_EXT`, `GENERATED_PATH`, `LOG_DIR`, and `UTF8` from the appropriate local module.
  - The logging setup is placed after the import statements.
  - The logging setup defines the log file name from the current file name.
  - The logging setup appends `LOG_EXT` to the file stem.
  - The logging setup creates the log file path with `GENERATED_PATH`, `LOG_DIR`, and the log file name.
  - The logging setup calls `logging.basicConfig(...)` to configure file logging.
  - The logging setup sets the logging level to `logging.DEBUG`.
  - The logging setup uses `ERROR_LOG_FORMAT` for the logging format.
  - The logging setup uses append mode with `filemode="a"`.
  - The logging setup uses `UTF8` for the file encoding.
  - The logging setup defines a module logger with `logging.getLogger(__name__)`.

  ```python
  # Configure logging
  basename = os.path.basename(__file__)
  stem = os.path.splitext(basename)[0]
  file = stem + LOG_EXT
  log_filename = os.path.join(GENERATED_PATH, LOG_DIR, file)

  # override the default logging level WARN to lowest level so we can log all levels
  logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=ERROR_LOG_FORMAT, filemode="a", encoding=UTF8)
  logger = logging.getLogger(__name__)

  ```

### Casing Rules

- Use `snake_case` for public file names, methods, variables, and module names.
- Use single-leading-underscore `snake_case` for non-public helper methods.
- Use double-leading-underscore `snake_case`
  - only for class methods that intentionally rely on Python name mangling to avoid accidental override or external access.
- Use leading-underscore `snake_case` for non-public module, class, and instance members; for example, `_private_variable` or `_private_method`.
- Use `PascalCase` for classes.
- USE `ALL_CAPS` for constants.
