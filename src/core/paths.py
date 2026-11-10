'''
@module paths
@file paths.py
@author Gerald Manweiler

@brief Defines the core paths module.

@details Provides definitions for core paths used throughout the application.

@version 1.0.0
@date 2026-11-02

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import os                                                   # for operating system dependent functionality
import pathlib                                              # for filesystem paths

## @var PROJECT_ROOT
# @brief The project root directory.
# @details Finds the parent directory containing the application entry point, which is guaranteed to exist.
candidate_dirs = pathlib.Path(__file__).resolve().parents
for candidate_dir in candidate_dirs:
    main_file = candidate_dir.joinpath("main.py")
    if main_file.is_file():
        PROJECT_ROOT = candidate_dir
        break

## @var SRC_PATH
# @brief The root source directory of the project.
# @details This path points to the top-level source directory containing the core, models, controllers, views, and other modules.
SRC_PATH = os.path.join(PROJECT_ROOT, "src")

## @var GENERATED_PATH
# @brief Generated-files directory path.
# @details Provides a shared path without hard-coded directory values elsewhere in the codebase.
GENERATED_PATH = os.path.join(SRC_PATH, "generated_files")  # same location (src/generated_files) until Milestone 9 Resources and generated output

## @var RESOURCES_PATH
# @brief Resources directory path.
# @details Provides a shared path for resource files without hard-coded directory values elsewhere in the codebase.
RESOURCES_PATH = os.path.join(SRC_PATH, "resources")        # unused until Milestone 9 Resources and generated output
