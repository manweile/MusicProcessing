---
description: "Python coding standards for MusicProcessing: Doxygen docstrings, module layout, naming, logging, and error handling conventions."
applyTo: "**/*.py"
---
# Python Rules

## Documentation (Doxygen/Javadoc style)

- Use triple single quotes `''' ... '''` for all module, class, and function docstrings.
- Start every docstring with `@brief` (one line), followed by a blank line.
- Add `@details` for a longer description when necessary, in imperative voice, followed by a blank line.
- Document every parameter with `@param {type} name description`, explicitly stating the type even when a type hint is present.
- Document return values with `@return {type} name description`.
- Document raised errors with `@exception {type} description`.
- Module files start with a file-level docstring:

  ```python
  '''
  @file audio_art.py
  @brief Defines the audio art class.

  @author Gerald Manweiler
  @copyright @showdate "%Y" GWN Software. All rights reserved.
  '''
  ```

- Example function:

  ```python
  def get_area(radius):
      '''
      @brief Calculates the area of a circle.

      @details A detailed description if necessary.

      @param {float} radius The radius of the circle.
      @return {float} area The calculated area.

      @exception ExceptionType Description of exceptions raised.
      '''

      area = 3.14 * radius ** 2
      return area
  ```

- Document module-level variables/constants with `##` Doxygen comments directly above them:

  ```python
  ## @var logger
  # @brief the logger instance for module
  # @details sets the logger name to module name
  logger = logging.getLogger(__name__)
  ```

## Module Layout

Follow this import/setup order (see `templating/python_module_template.py` for the canonical template):

1. File docstring (`@file`, `@brief`, `@author`, `@copyright`).
2. `# standard modules` — stdlib imports.
3. `# third party modules` — e.g. `mutagen`.
4. `# local module methods` — e.g. `from src import add_module_handler`.
5. `# local module constants` — e.g. `from src import AUDIO_EXTS`.
6. `# local module errors` — e.g. `from src import PathInfoError`.
7. `# local module classes` — other project classes; use relative imports (`.`) only where needed to avoid circular imports.
8. `gc.enable()`.
9. Module logger setup:

   ```python
   logger = logging.getLogger(__name__)
   basename = os.path.basename(__file__)
   add_module_handler(logger, basename)
   ```

10. Module-level instances/constants, each documented with a `## @var` block.

## Naming & Structure

- Classes: `PascalCase`, declared with explicit parens, e.g. `class AudioArt():`.
- Functions/methods/variables: `snake_case`.
- Constants: `ALL_CAPS` (e.g. `FOLDER_ART`, `AUDIO_EXTS`).
- Private/internal methods use a double leading underscore (name-mangled), e.g. `__unpack_asf_image`.
- Use type hints on parameters and return types where practical, but still document `{type}` in the docstring per the Doxygen rules above.

## Errors

- Define custom exceptions in [errors.py](../../src/errors.py), subclassing `MusicProcessingException` (itself a subclass of `Exception`).
- Each custom exception takes a `message` default and calls `super().__init__(self.message)`.
- Catch specific exceptions before generic ones; log with `logger.error(..., exc_info=True)` or `logger.exception(..., stack_info=True)` before re-raising.

## Tests

- Test files live in `tests/`, named `test_<module>.py`, using `unittest.TestCase`.
- Mirror the module docstring/import layout shown above; import fixtures/constants from the `tests` package (e.g. `TESTS_PATH`, `TEST_MP3_ABBA`).
- Use `setUpClass`/`tearDownClass` for shared fixtures, documented with `@brief`/`@details`.
- Avoid top-level imports of GUI modules (e.g. `src.gui.wx_app`); import lazily inside test methods so headless CI can skip cleanly.
