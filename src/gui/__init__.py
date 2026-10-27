'''
@package src.gui
@file src/gui/__init__.py
@author Gerald Manweiler

@brief Package for MusicProcessing GUI.

@details Contains the wxPython-based graphical user interface components for the MusicProcessing application.

@version 1.0.0
@date 2024-06-05

@copyright @showdate "%Y" GWN Software. All rights reserved.
'''

# Local Module Methods
from src.gui.wx_app import run_gui

## var __all__
# @brief Exposes class for importing by other modules.
# @details In modules needing the class, add `from src.gui import run_gui`
__all__ = [
    "run_gui"
]
