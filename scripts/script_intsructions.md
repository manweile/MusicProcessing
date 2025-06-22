# How to run standalone scripts in a sibling directory
There are basically 3 options for running stand alone scripts in a sibling directory that do NOT have a ```if __name__ = "__main__":```

## Run script as a module
Useful for terminal execution of modules directly, especially when dealing with packages or when you want to avoid issues with relative imports.

No need to add code or modify PYTHONPATH.

- ```>cd D:\MusicProcessing```
- ```>python.exe -i -m <script dir>.<script name>```
- where script dir is location of script name
- do NOT need .py extension
- use period instead of backslash for pathing

## In code pathing
Great for one off scripts if you don't mind adding the code and don't want to modify your PYTHONPATH.

Is the in code version of permanently modifying PYTHONPATH.

Also allows script to be ran by VS Code python debugger.

- add at **top** of script:
```
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

## Modify PYTHONPATH
Modifying the PYTHONPATH is essentially duplicating what pip install <package> does.

### Ubuntu
- Open ~/.bashrc for editing
- Add to **bottom** of ~/.bashrc:
 - ```export PYTHONPATH="/home/gerald/MusicProcessing:$PYTHONPATH"```
- Save ~/.bashrc
- Verify
 - ```$ echo $PYTHONPATH```
 - ```    /home/gerald/MusicProcessing:```

### Windows
- Open System Properties:
  - - Press the Windows key + R, type sysdm.cpl, and press Enter
- Go to Environment Variables:
  - In the System Properties window, click the "Advanced" tab, then click "Environment Variables"
    - Edit or Create PYTHONPATH:
    - If PYTHONPATH already exists in User variables or System variables, select it and click "Edit"
    - If PYTHONPATH does not exist, click "New..." under User variables
  - Set the Value:
    - In the "Variable name" field, type PYTHONPATH
    - In the "Variable value" field, enter the directories you want to add to the Python path, separated by semicolons (;)
    - D:\MusicProcessing;
  - Apply Changes: Click "OK" on all dialog boxes to save the changes
- Verify:
  - from command prompt line: ```echo %PYTHONPATH%```
  - from Powershell: ```$env:Pythonpath```
