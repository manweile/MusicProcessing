<!-- markdownlint-disable MD033 -->

# Run Scripts in docs/scripts

This guide describes three ways to make project modules importable when running a script in `docs/scripts`.<br>
Scripts with an `if __name__ == "__main__":` guard can be run directly or with `python -m`.<br>
The guard controls execution, while these approaches control whether project imports resolve.

Scripts without the guard can also be run directly or with `python -m`, but their top-level statements run when imported.<br>

## Run script as a module

Use this method when the script can be addressed as a Python module.<br>
Running from the project root adds that directory to Python's import lookup for the current process,
so no code changes or `PYTHONPATH` configuration are needed.

1. Open a terminal in the project root:

    ```powershell
    Set-Location D:\MusicProcessing
    ```

2. Run the script with its dotted module path:

    ```powershell
    python -m package.module
    ```

   Replace `package.module` with the script path from the project root, omitting `.py` and replacing directory separators with periods.<br>
   Each parent directory must be importable as a package or namespace package; the final component names the module.

3. Add `-i` after `python` only when an interactive Python prompt should remain open after the script finishes.

## Add project root to sys.path

Useful for a one-off script that must be run directly, when running it as a module is not practical.<br>
This changes the import path only for the current Python process and also works when launching the script through the VS Code debugger.

1. Add the following near the top of the script:

    ```python
    from pathlib import Path
    import sys

    project_root = next(
        parent for parent in Path(__file__).resolve().parents if (parent / "src").is_dir()
    )
    sys.path.insert(0, str(project_root))
    ```

    The code searches upward through the repository tree until it finds the project directory containing `src`.

## Modify PYTHONPATH

Modifying the PYTHONPATH adds source directories to import lookup,
allowing Python to import modules and packages from those directories regardless of the script’s working directory.<br>
This is convenient for running scripts from nested or sibling directories that need to import project modules,
such as src without changing each script or its working directory.

### Ubuntu

1. Open ~/.bashrc for editing
2. Add to **bottom** of ~/.bashrc:

    ```bash
    export PYTHONPATH="/home/gerald/MusicProcessing${PYTHONPATH:+:$PYTHONPATH}"
    ```

3. Save ~/.bashrc
4. reload ~/.bashrc or open a new terminal and verify the setting:

    ```bash
    echo "$PYTHONPATH"
    ```

### Windows

1. Press `Windows+R`, enter `sysdm.cpl`, and press Enter.
2. Select **Advanced** > **Environment Variables**.
3. Under **User variables**, create or edit `PYTHONPATH`.
4. Set the value to the project directories, separated by semicolons:

    ```text
    D:\MusicProcessing;F:\Yadda;G:\BlahBlah
    ```

    Do not add a trailing semicolon.<br>
    It creates an empty path entry, which can cause Python to search the current directory and unexpectedly import a shadowing module.

5. Click OK in each dialog, then open a new terminal window to verify the setting:

    - In Command Prompt:

        ```cmd
        echo %PYTHONPATH%
        ```

    - In PowerShell:

        ```powershell
        $env:PYTHONPATH
        ```
