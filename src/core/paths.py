'''
@module core.paths
@file core/paths.py
@author Gerald Manweiler

@brief Defines the core paths module.

@details Provides definitions for core paths used throughout the application.

@version 1.0.0
@date 2026-11-02

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Standard Modules
import os                                                   # for operating system dependent functionality

## @var SRC_PATH
# @brief The root source directory of the project.
# @details This path points to the top-level source directory containing the core, models, controllers, views, and other modules.
SRC_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

## @var GENERATED_PATH
# @brief Generated-files directory path.
# @details Provides a shared path without hard-coded directory values elsewhere in the codebase.
GENERATED_PATH = os.path.join(SRC_PATH, "generated_files")  # same location as today

## @var RESOURCES_PATH
# @brief Resources directory path.
# @details Provides a shared path for resource files without hard-coded directory values elsewhere in the codebase.
RESOURCES_PATH = os.path.join(SRC_PATH, "resources")        # unused until Milestone 8
