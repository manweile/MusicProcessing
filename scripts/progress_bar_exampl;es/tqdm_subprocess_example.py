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
      print(f"Exception: Command '{command}' failed with return code {process.returncode}")
      if stderr:
          print(f"Stderr:\n{stderr}")

    return process.returncode, stdout, stderr

if __name__ == "__main__":
    commands = [
        "ls -l /usr/bin",  # Example: List files in /usr/bin
        "ls -l /",
        "find /usr -name '*.txt'", # Example: Find text files (may take long)
    ]

    for cmd in commands:
        return_code, stdout, stderr = run_command_with_progress(cmd)
        if return_code == 0:
          print(f"Command '{cmd}' executed successfully.")
          print(f"Stdout:\n{stdout}") # Uncomment if you want to print the full output
          print(f"Stderr:\n{stderr}")

# test 2
# input_path = Path(out_f.name)
# input_file_name = input_path.name

# with tqdm(desc=f"Running ffmpeg subprocess to convert{input_file_name}") as pbar:
#     with open(os.devnull, 'rb') as devnull:
#         p = subprocess.Popen(conversion_command, stdin=devnull, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#     #  when get here, p.stderr.readlines() has binary data with \r\n in it
#     # stderr_count = p.stderr.readlines().len()
#     for line in p.stderr:
#         pbar.update(1)

# read stdin / write stdout
# with open(os.devnull, 'rb') as devnull:
#     p = subprocess.Popen(conversion_command, stdin=devnull, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# test 1
# # my addition adding progress bar
# input_path = Path(out_f.name)
# input_file_name = input_path.name

#
#     while True:
#         line = p.stderr.readline()
#         if not line:
#             if p.poll() is not None:
#                 break
#             # time.sleep(0.1)
#             continue
#         pbar.update(1)