import subprocess
from tqdm import tqdm
import time

def run_command_with_progress(command):
    """Runs a shell command and displays progress using tqdm."""

    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    with tqdm(desc=f"Running: {command}", unit=" line", leave=True) as pbar:
        while True:
            line = process.stdout.readline()
            if not line:
                if process.poll() is not None:
                    break
                time.sleep(0.1)  # Avoid busy-waiting
                continue
            pbar.update(1)
            # Optionally process the output line here
            # print(line.strip())  # Example: Print each line

    # Capture remaining output/errors after process completion
    stdout, stderr = process.communicate()

    if process.returncode != 0:
      print(f"Error: Command '{command}' failed with return code {process.returncode}")
      if stderr:
          print(f"Stderr:\n{stderr}")

    return process.returncode, stdout

if __name__ == "__main__":
    commands = [
        "ls -l /usr/bin",  # Example: List files in /usr/bin
        "find / -name '*.txt'", # Example: Find text files (may take long)
    ]

    for cmd in commands:
        return_code, stdout = run_command_with_progress(cmd)
        if return_code == 0:
          print(f"Command '{cmd}' executed successfully.")
          #print(f"Stdout:\n{stdout}") # Uncomment if you want to print the full output