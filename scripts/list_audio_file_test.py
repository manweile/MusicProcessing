'''
permanent no code fix for Ubuntu:
    Open ~/.bashrc for editing
    Set the value:
        add following to end of ~/.bashrc
        export PYTHONPATH="/home/gerald/MusicProcessing:$PYTHONPATH"
    Apply Changes: Save ~/.bashrc
    VerifY: from command line: $ echo $PYTHONPATH
        /home/gerald/MusicProcessing:

permanent no code fix for Windows:
    Open System Properties:
        Press the Windows key + R, type sysdm.cpl, and press Enter.
    Go to Environment Variables:
    In the System Properties window, click the "Advanced" tab, then click "Environment Variables."
    Edit or Create PYTHONPATH:
        If PYTHONPATH already exists in User variables or System variables, select it and click "Edit."
        If PYTHONPATH does not exist, click "New..." under User variables.
    Set the Value:
        In the "Variable name" field, type PYTHONPATH.
        In the "Variable value" field, enter the directories you want to add to the Python path, separated by semicolons (;).
        D:\MusicProcessing;
    Apply Changes: Click "OK" on all dialog boxes to save the changes.
    Verify:
        from command prompt line: echo %PYTHONPATH%
        from Powershell: $env:Pythonpath

in code fix: must be first three lines of script
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
'''

# standard modules
import platform

# local modules
from src.dir_processing import DirectoryProcessing

if platform.system() == "Linux":
    dir_processing = DirectoryProcessing(r"/media/gerald/Music/Music")
elif platform.system() == "Windows":
    dir_processing = DirectoryProcessing(r"H:\Music")

dir_processing.get_audio_file_list()