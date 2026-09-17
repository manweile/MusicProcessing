---
applyTo: "**/*.py"
---

# Python Documentation Standards

- All new Python files require a file-level Doxygen block.

## Python

Always use [python doc strings](https://doxygen.nl/manual/docblocks.html#pythonblocks)
& doxygen [javadoc style](https://en.wikipedia.org/wiki/Javadoc) `@` [special commands](https://doxygen.nl/manual/commands.html).

- These Python rules apply only to `.py` files.

## Shared Python Rules

- Use paired triple single quotes `''' ... '''` for Doxygen blocks in Python.
- Use `#` for inline comments.
- After the file block, order declarations as follows:
  1. Imports
  2. Module Level Constants
  3. Module Level Variables
  4. Classes
  5. Functions
  - List items alphabetically within each group or subgroup unless a section below states otherwise.
  - Separate Import, Module Level Constants and Module Level Variables with a blank line.
  - Separate classes from preceding code with 2 blank lines.
  - Separate functions inside classes from preceding code with 2 blank lines.
  - In class and function definitions, the Doxygen blocks are immediately after the class or function definition line.
  - All python files end with a blank line.

## Shared Doxygen Rules

- Use a one-line `@brief`.
- Leave an empty line after `@brief`.
- Add a `@details` block.
- Use imperative voice in `@details`.
- Leave an empty line after the `@details` block.
- Follow the Details Block Formatting Rules.
- Use:
  - `@param name {type} description` for input parameters
  - `@return name {type} description` for return values
- Leave an empty line after `@param` and `@return` blocks.
- Omit `@param` entirely for functions with no parameters.
- Omit `@return` entirely for functions that return `None`.
- Use `@exception {type} description` for exceptions raised by the function.
- Omit `@exception` entirely for functions that do not raise any exceptions.

## Column Alignment Rules

- Inline comments are denoted by `#`.
- Use consistent column alignment for inline `#` comments.
- Place inline `#` comments aligned consistently, targeting column 61 where practical.
- Keep inline comments within column 150; shorten wording if necessary.
- Declarations must not extend past column 60; shorten wording if necessary.
- These rules apply to global constants and global variables.
- Break long parameter lists to continuation lines starting at column 61.

## Details Block Formatting Rules

- Apply these rules to every `@details` block in Python Doxygen comments, including:
  1. File-level documentation blocks
  2. Functions documentation blocks
- Write each `@details` line as a complete sentence ending with a period.
- Keep each `@details` line at or below column 150; shorten wording if necessary.
- If the shortest clear wording still exceeds column 150, break the line after, in this order of preference:
  1. a comma
  2. a semicolon
  3. a coordinating conjunction: "for", "and", "nor", "but", "or", "yet", or "so"
  4. a preposition: "in", "on", "at", "to", "from", "by", "with", "about", "as", "of", or "for"
- If a line is broken, do not append a `<br>` to the end of the line; instead, start the next line with a lowercase letter.
- Do not append a `<br>` to a single line `@details` block.
- Append a `<br>` for lines ending with a period, except for the final line of a multiline `@details` block.

## File Block Rules

- All files start with a Doxygen file header block.
- The start the first line of the file header must follow the per file type header block rule.
  1. Package Files Header Block rules for package files.
  2. Module Files Header Block rules for module files.
  3. Class Files Header Block rules for class files.
  4. Test Files Header Block rules for test files.
- Add `@author` Gerald Manweiler, followed by an empty line.
- Add `@brief`
  - `Package ...` in package files
  - `Defines the ... module` in module files
  - `Defines the ... class` in class files
  - `Defines the test ... class` in test files
- Add an empty line after `@brief`.
- Add a `@details` block.
  - Follow the Details Block Formatting Rules.
- Add `@version` using Semantic Versioning starting at 1.0.0, per semver.org in `MAJOR.MINOR.PATCH` format.
- Add `@date`, followed by an empty line.
- Add `@copyright` `@showdate "%Y"` GWN Software. All rights reserved.
- Leave one blank line after the file header block and before the first import.

## Package Files Header Block

- Package files are `__init__.py` files.
  - Their header blocks start with `@package ...` where `...` is the name of the package.
  - Their next line is `@file ...` where `...` is the name of the relative file path; eg: `@file src/__init__.py`

## Module Files Header Block

- Module files are `*.py` files that contain one or more class definitions with an `__init__` method, but no additional methods,
  and do not define a package.
  - Their header blocks start with `@module ...` where `...` is the name of the module.
  - Their next line is `@file ...` where `...` is the name of the file; eg: `@file module_file.py`

## Class Files Header Block

- Class files are `*.py` files that contain a class definition, an `__init__` method, and at least one additional method.
  - Their header blocks start with `@class ...` where `...` is the name of the class.
  - Their next line is `@file ...` where `...` is the name of the file; eg: `@file class_file.py`

## Test Files Header Block

- Test files are `test_class_file.py` files that contain test cases for the project.
  - Their header blocks start with `@class ...` where `...` is the name of the class.
  - Their next line is `@file ...` where `...` is the name of the file; eg: `@file test_class_file.py`

## Import Rules

- Never use wildcard imports (e.g., `from module import *`).
- Never use relative imports (e.g., `from .module import ...`).
- Always use 1 import per line, never combine multiple imports in a single statement.
- Always use absolute imports for local modules in package files.
- Group imports in this order:
  1. Python standard modules
  2. third party modules
  3. local modules
- List imports alphabetically within each subgroup.
- Precede each subgroup with:
  - `# Standard Modules`
  - `# Third Party Modules`
  - `# Local Modules`
- Within each subgroup, maintain alphabetical order and use consistent comment annotations.
- Within the `# Local Modules` subgroup, partition imports with semantic headings named `# Local Module <type>`,
  where `<type>` identifies the imported module member category, such as `Methods`, `Constants`, `Errors`, or `Classes`.
  - Apply these semantic headings to both `import ...` and `from ... import ...` statements.
  - Use the imported member name to determine its category and place it under the corresponding heading.
  - Order the semantic headings in this order:
    1. Methods
    2. Constants
    3. Errors
    4. Classes
- add an plain `#` inline comment that explains the purpose of the placeholder comment
  - The inline comment must never exceed column 150.
    - place the inline comment after the import statement starting on line 61 if there is room.
    - place the inline comment immediately before the import statement if the import statement exceeds column 61.
- For all subgroups, imports via `import` come first, followed by `from ... import ...` statements
  - Maintain consistent comment annotations and alphabetical order in `import` and `from ... import ...` statements.
- Leave a blank line after each subgroup.

### Package and Module Level Variables, Constants, and Lists

- Applies to package, class, and test files
- Have a Doxygen documentation block for all module level variables and constants.
- The Doxygen documentation block should include:
  - `##@var <variable_name>` line for specifying the name of the module level variable or constant.
  - `# @brief <description>` line for providing a brief summary of the variable or constant.
  - `# @details <details>` line for providing additional information about the variable or constant.
    - module level variables and constant can have multiple `@details` lines if needed.
      - Each `@details` line should be concise and relevant to the variable or constant it describes.
    - `__all__` export lists have a `@details <details>` line for each item, in alphabetical order.
      - Each `@details` line should explain how to import the item
      - Example:

      ```python
      ## @var __all__
      # @brief Exposes class for importing by other modules.
      # @details  In modules needing the class, add `from src.audio_info.audio_art import AudioArt`
      # @details  In modules needing the class, add `from src.audio_info.audio_metadata import AudioMetadata`
      # @details  In modules needing the class, add `from src.audio_info.audio_playlist import AudioPlaylist`
      # @details  In modules needing the class, add `from src.audio_info.audio_utilities import AudioUtilities`
      ```

## Package Files

- Package files have a `__all__` export list to specify the public API of the package.
- `__all__` export lists have 1 item per line.
  - Example:

  ```python
  __all__ = [
      "AudioArt",
      "AudioMetadata",
      "AudioPlaylist",
      "AudioUtilities",
  ]
  ```

## Garbage Collection

- All class files, test files, and the main.py file should properly manage garbage collection to avoid memory leaks.
  - Import the `gc` standard module.
  - place `gc.enable()` after last import statement, followed by a blank line.
- Module and package files do not need to explicitly manage garbage collection.

### Class File Logging Setup

- All class files with more than 1 method definition should include a logging setup section.
  - the logging setup is after the import statements.
- Test files do not include logging setup.

## Test Files (`test_*.py`)

- Files named `test_*.py` are implementation-only test sources, not public API.
- Test files are class files and should follow the same header and import rules as regular class files.
- Test files do not have logging enabled.
- Test files have a class level `setupClass` method for initializing test fixtures, with a `@classmethod` decorator.
- Test files have a class level `tearDownClass` method for cleaning up test fixtures, with a `@classmethod` decorator.
- Test files have a `tearDown` method for cleaning up individual test cases.
- Test files test cases are named `test_<functionality>`, where `<functionality>` describes the specific feature or behavior being tested.
- Test cases have a `@test` describing which describes the specific functionality being tested in their Doxygen documentation.
  - The `@test` line is placed after the blank line following the`@details` block, and is followed by a blank line.
- Test cases using mock objects have an appropriate `@patch` decorator for the mock in the test case.

### This Repo Rules

- Use `snake_case` for new file names, functions, variables, and module names.
- Use `PascalCase` for classes.
- USE `ALL_CAPS` for constants.
- When changing Python test behavior or requirements, validate the narrowest applicable path.
