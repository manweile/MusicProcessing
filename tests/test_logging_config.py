'''
@class TestLoggingConfig
@file test_logging_config.py
@author Gerald Manweiler

@brief Defines the test logging configuration class.

@details Verifies package and module logging setup, idempotency, and failure handling.

@version 1.0.0
@date 2026-11-08

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
from contextlib import ExitStack                               # for ordered test resource cleanup
import logging                                              # for inspecting logger handlers
import os                                                   # for file system operations
import tempfile                                             # for isolated generated directories
import unittest                                             # for direct test-suite execution
from unittest import TestCase                               # for test-case assertions
from unittest.mock import patch                             # for test configuration and failures

# Local Modules
from src.core import logging_config                         # for package and module logging configuration
from src.core.level_filter import LevelFilter               # for filtering records by exact logging level

# Local Module Methods
from tests.support import get_method_names                  # for direct test-suite construction


class TestLoggingConfig(TestCase):
    '''
    @brief Test case for logging configuration.

    @details Verifies package and module logging setup, idempotency, and failure handling.
    '''

    def setUp(self):
        '''
        @brief Set up the test environment.

        @details Removes existing handlers from the logger and stores the original logging configuration.

        @param self {TestLoggingConfig} The instance of the test class.
        '''

        # get the logger for the "src" package and store its original handlers and level
        self.logger = logging.getLogger("src")
        self.original_handlers = list(self.logger.handlers)
        self.original_level = self.logger.level

        # remove all handlers from the logger to start with a clean slate
        for handler in self.original_handlers:
            self.logger.removeHandler(handler)

        # store the original logging configuration attributes and reset them for the test
        self.original_config = {
            name: getattr(logging_config, name)
            for name in (
                "_encoding",
                "_generated_path",
                "_log_dir",
                "_log_ext",
                "_log_format",
                "_package_logging_configured",
            )
        }

        logging_config._encoding = None
        logging_config._generated_path = None
        logging_config._log_dir = None
        logging_config._log_ext = None
        logging_config._log_format = None
        logging_config._package_logging_configured = False


    def tearDown(self):
        '''
        @brief Tear down the test environment.

        @details Restores the original logger handlers, level, and logging configuration attributes.

        @param self {TestLoggingConfig} The instance of the test class.
        '''

        # remove all handlers from the logger to clean up after the test
        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)
            handler.close()

        # restore the original handlers to the logger
        for handler in self.original_handlers:
            self.logger.addHandler(handler)

        # restore the original logging level to the logger
        self.logger.setLevel(self.original_level)

        # restore the original logging configuration attributes
        for name, value in self.original_config.items():
            setattr(logging_config, name, value)


    def _patch_bootstrap_paths(self, generated_path):
        '''
        @brief Patch the bootstrap paths for the logging configuration.

        @param generated_path {str} The generated path to use for the bootstrap.

        @return {unittest.mock._patch.multiple} The patch context manager for the bootstrap paths.
        '''

        return patch.multiple(
            logging_config,
            GENERATED_PATH=generated_path,
            CSV_DIR="csv_files",
            LOG_DIR="log_files",
            RESULT_DIR="result_files",
            LOG_EXT=".log",
            UTF8="utf-8",
            ERROR_LOG_FORMAT="%(levelname)s:%(message)s",
        )


    def _close_logger_handlers(self):
        '''
        @brief Close handlers created by a logging configuration test.

        @details Remove and close the logger handlers before temporary log files are deleted.

        @param self {TestLoggingConfig} The instance of the test class.
        '''

        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)
            handler.close()


    def test_configure_then_bootstrap_does_not_add_handlers(self):
        '''
        @brief Test that configuring the logger and then bootstrapping does not add additional handlers.

        @details Ensure after configuring logging, subsequent calls to bootstrap_logging do not add extra handlers to the logger.

        @param self {TestLoggingConfig} The instance of the test class.
        '''

        # create a temporary directory for the generated path and patch the bootstrap paths with it
        with ExitStack() as stack:
            generated_path = stack.enter_context(tempfile.TemporaryDirectory())
            stack.callback(self._close_logger_handlers)

            # patch the bootstrap paths for the logging configuration with the generated path
            with self._patch_bootstrap_paths(generated_path):
                logger = logging_config.configure_logging(
                    generated_path,
                    "csv_files",
                    "log_files",
                    "result_files",
                    ".log",
                    "utf-8",
                    "%(levelname)s:%(message)s",
                )

                # ensure the logger is configured and store its handlers after configuration
                self.assertTrue(logging_config._package_logging_configured)
                handlers_after_configuration = list(logger.handlers)
                self.assertEqual(len(handlers_after_configuration), 5)

                # bootstrap the package logging and ensure no additional handlers are added
                self.assertIs(logging_config.bootstrap_logging(), logger)
                self.assertIs(logging_config.bootstrap_logging(), logger)
                self.assertEqual(logger.handlers, handlers_after_configuration)


    def test_bootstrap_configures_once_when_not_configured(self):
        '''
        @brief Test that bootstrapping the logger configures it once when not already configured.

        @details Ensures that the bootstrap_package_logging function sets up the logger correctly and does not add extra handlers on subsequent calls.

        @param self {TestLoggingConfig} The instance of the test class.
        '''

        # create a temporary directory for the generated path and patch the bootstrap paths with it
        with ExitStack() as stack:
            generated_path = stack.enter_context(tempfile.TemporaryDirectory())
            stack.callback(self._close_logger_handlers)

            # bootstrap the logging configuration using the generated path
            with self._patch_bootstrap_paths(generated_path):
                logger = logging_config.bootstrap_logging()

                # the expected log levels and their corresponding numeric values
                expected_levels = {
                    "debug": logging.DEBUG,
                    "info": logging.INFO,
                    "warning": logging.WARNING,
                    "error": logging.ERROR,
                    "critical": logging.CRITICAL,
                }

                self.assertEqual(len(logger.handlers), len(expected_levels))

                # Verify that each expected log level has a corresponding handler with the correct configuration
                for name, level in expected_levels.items():
                    expected_path = os.path.abspath(
                        os.path.join(generated_path, "log_files", f"{name}.log")
                    )

                    # Collect all handlers that match the expected path for this log level
                    matching_handlers = []
                    for handler in logger.handlers:
                        if handler.baseFilename == expected_path:
                            matching_handlers.append(handler)

                    # Ensure exactly one handler matches the expected path for this log level
                    self.assertEqual(len(matching_handlers), 1)
                    handler = matching_handlers[0]
                    self.assertEqual(handler.formatter._fmt, logging_config.ERROR_LOG_FORMAT)

                    # debug level should have no filters, other levels should have a LevelFilter
                    if level == logging.DEBUG:
                        self.assertEqual(handler.filters, [])
                    else:
                        # Ensure the handler has exactly one filter and it is a LevelFilter with the correct bounds
                        self.assertEqual(len(handler.filters), 1)
                        # Retrieve the LevelFilter from the handler's filters list
                        level_filter = handler.filters[0]
                        # Verify that the retrieved filter is indeed a LevelFilter instance, and has the correct low and high bounds
                        self.assertIsInstance(level_filter, LevelFilter)
                        self.assertEqual(level_filter._low, level)
                        self.assertEqual(level_filter._high, level)

                # Test adding a module handler to a specific module logger and verify its configuration
                module_logger = logging.getLogger(f"{__name__}.bootstrap_test")
                original_handlers = list(module_logger.handlers)

                # try block to ensure module handler is properly cleaned up after the test
                try:
                    logging_config.add_module_handler(module_logger, "bootstrap_test.py")

                    # Identify new handlers added to the module logger after adding the module handler
                    new_handlers = []
                    for handler in module_logger.handlers:
                        if handler not in original_handlers:
                            new_handlers.append(handler)

                    # Ensure exactly one new handler was added
                    self.assertEqual(len(new_handlers), 1)

                    module_handler = new_handlers[0]
                    expected_module_path = os.path.abspath(os.path.join(generated_path, "log_files", "bootstrap_test.log"))

                    # Verify that the module handler's base filename matches the expected module path
                    self.assertEqual(module_handler.baseFilename, expected_module_path)
                    self.assertTrue(os.path.isfile(expected_module_path))
                    self.assertEqual(module_handler.formatter._fmt, logging_config.ERROR_LOG_FORMAT)
                    self.assertEqual(module_handler.encoding, "utf-8")
                finally:
                    # Clean up any new handlers added to the module logger to avoid side effects on other tests
                    for handler in list(module_logger.handlers):
                        if handler not in original_handlers:
                            module_logger.removeHandler(handler)
                            handler.close()

                # ensure the logger is configured and has the expected number of handlers
                self.assertTrue(logging_config._package_logging_configured)
                self.assertEqual(len(logger.handlers), 5)

                # ensure the expected directories are created within the generated path
                for directory in ("csv_files", "log_files", "result_files"):
                    self.assertTrue(os.path.isdir(os.path.join(generated_path, directory)))

                # ensure the expected log files are created for each log level
                for level in ("debug", "info", "warning", "error", "critical"):
                    log_path = os.path.join(generated_path, "log_files", f"{level}.log")
                    self.assertTrue(os.path.isfile(log_path))

                # store the handlers after the first call to bootstrap_package_logging
                handlers_after_first_call = list(logger.handlers)

                # call bootstrap_package_logging again and ensure no new handlers are added
                self.assertIs(logging_config.bootstrap_logging(), logger)
                self.assertEqual(logger.handlers, handlers_after_first_call)


    def test_bootstrap_failure_propagates_without_setting_configured_flag(self):
        '''
        @brief Test that a failure during bootstrap does not set the configured flag.

        @details Ensures that if an OSError occurs while creating a handler, the _package_logging_configured flag remains False and no handlers are left attached to the logger.

        @param self {TestLoggingConfig} The instance of the test class.
        '''

        # create a temporary directory for the generated path and patch the bootstrap paths with it
        with tempfile.TemporaryDirectory() as generated_path:
            with self._patch_bootstrap_paths(generated_path):
                real_file_handler = logging_config.FileHandler
                created_handlers = []

                # need to simulate a failure after creating the first handler
                def create_one_handler_then_fail(*args, **kwargs):
                    '''
                    @brief Create a handler and simulate failure on subsequent calls.

                    @details The first call creates a real FileHandler, while subsequent calls raise an OSError to simulate failure.

                    @param args Arguments passed to the FileHandler constructor.
                    @param kwargs Keyword arguments passed to the FileHandler constructor.

                    @return The created FileHandler on the first call.
                    '''

                    if created_handlers:
                        raise OSError("simulated handler creation failure")

                    handler = real_file_handler(*args, **kwargs)
                    created_handlers.append(handler)
                    return handler

                # patch logging_config FileHandler to simulate failure after the first handler is created
                patched_object = patch.object(logging_config, "FileHandler", side_effect=create_one_handler_then_fail)
                with patched_object:
                    # attempt to bootstrap logging, expecting an OSError after the first handler is created
                    with self.assertRaisesRegex(OSError, "simulated handler creation failure"):
                        logging_config.bootstrap_logging()

                # Ensure that the package logging configuration flag is reset after the failure.
                self.assertFalse(logging_config._package_logging_configured)
                # Ensure that no handlers remain attached to the package logger after the failure.
                self.assertEqual(self.logger.handlers, [])
                # Ensure that only the first handler was created before the failure occurred.
                self.assertEqual(len(created_handlers), 1)
                # Ensure that the first handler was properly closed after the failure.
                self.assertIsNone(created_handlers[0].stream)


if __name__ == "__main__":
    '''
    @brief Run the TestLoggingConfig test suite directly.

    @details Collects test methods, adds them to a suite, and executes the suite with a text runner.

    @note This test module can be run directly with `python tests/test_logging_config.py`.

    @test Execution of the test suite.
    '''

    methods = get_method_names(TestLoggingConfig)

    suite = unittest.TestSuite()
    for name in methods:
        suite.addTest(TestLoggingConfig(name))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
