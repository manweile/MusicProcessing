'''
@module logging_config
@file logging_config.py
@author Gerald Manweiler

@brief Defines the logging configuration module.

@details Configure package and module file logging.

@note This implementation does not require garbage collection or or logging functionality.

@version 1.0.0
@date 2026-09-16

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import logging                                              # for creating package loggers
import os                                                   # for creating logging directories
from logging import DEBUG                                   # for configuring the lowest logging level
from logging import FileHandler                             # for writing log records to files
from logging import Formatter                               # for formatting log records

# Local Module Classes
from src.level_filter import LevelFilter                    # for filtering records by exact logging level

## @var _encoding
# @brief Configured file encoding.
# @details Store the encoding used by module-specific file handlers.
_encoding = None

## @var _generated_path
# @brief Configured generated-files directory path.
# @details Store the base directory for generated log files.
_generated_path = None

## @var _log_dir
# @brief Configured log directory name.
# @details Store the directory name used for log files.
_log_dir = None

## @var _log_ext
# @brief Configured log-file extension.
# @details Store the extension used for log files.
_log_ext = None

## @var _log_format
# @brief Configured log-record format.
# @details Store the format used by module-specific file handlers.
_log_format = None


def configure_package_logging(generated_path, csv_dir, log_dir, result_dir, log_ext, encoding, log_format):
    '''
    @brief Configure package-level file logging.

    @details Create generated directories and attach level-specific file handlers to the package logger.

    @param generated_path {str} Base directory for generated project files.
    @param csv_dir {str} Directory name for generated CSV files.
    @param log_dir {str} Directory name for generated log files.
    @param result_dir {str} Directory name for generated result files.
    @param log_ext {str} File extension for log files.
    @param encoding {str} Text encoding for log files.
    @param log_format {str} Format string for log records.
    @return logger {Logger} Configured package logger.
    '''

    global _generated_path, _log_dir, _log_ext, _encoding, _log_format
    _generated_path = generated_path
    _log_dir = log_dir
    _log_ext = log_ext
    _encoding = encoding
    _log_format = log_format

    for generated_dir in (csv_dir, log_dir, result_dir):
        os.makedirs(os.path.join(generated_path, generated_dir), exist_ok=True)

    logger = logging.getLogger("src")
    logger.setLevel(DEBUG)

    log_path = os.path.join(generated_path, log_dir)

    for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        log_file = f"{level.lower()}{log_ext}"
        handler = FileHandler(os.path.join(log_path, log_file), mode="a", encoding=encoding)
        handler.setFormatter(Formatter(log_format))

        if level != "DEBUG":
            handler_level = getattr(logging, level)
            handler.addFilter(LevelFilter(handler_level, handler_level))

        logger.addHandler(handler)

    return logger


def add_module_handler(logger, basename, level=DEBUG, format=None, propagate=True):
    '''
    @brief Add a file handler to a module logger.

    @details Configure a module logger to write records to its corresponding generated log file.

    @param logger {Logger} Logger instance for a module.
    @param basename {str} Module filename used to construct the log filename.
    @param level {int} Logging level for the logger and file handler.
    @param format {str} Optional format string for log records.
    @param propagate {bool} Whether records propagate to the package logger.

    @exception {RuntimeError} Raised when package logging has not been configured.
    '''

    if _generated_path is None:
        raise RuntimeError("Package logging must be configured before adding module handlers.")

    logger.setLevel(level)

    stem = os.path.splitext(basename)[0]
    log_file = stem + _log_ext
    log_path = os.path.join(_generated_path, _log_dir, log_file)

    handler = FileHandler(log_path, encoding=_encoding)
    handler.setFormatter(Formatter(format or _log_format))
    handler.setLevel(level)

    logger.addHandler(handler)
    logger.propagate = propagate
