import subprocess
import time
from yaspin import yaspin
from yaspin.spinners import Spinners

def run_with_spinner(command, text="Processing..."):
    with yaspin(Spinners.dots, text=text) as sp:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while process.poll() is None:
            time.sleep(0.1)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            sp.fail("Failed!")
            print(stderr.decode())
        else:
            sp.ok("Done!")
            print(stdout.decode())
        return process.returncode

if __name__ == "__main__":
    command_to_run = "ls -l /usr/bin"
    run_with_spinner(command_to_run, text="Listing files...")

    command_that_fails = "false"
    run_with_spinner(command_that_fails, text="Trying to fail...")