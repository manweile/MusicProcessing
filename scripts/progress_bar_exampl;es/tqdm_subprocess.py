import sys
import subprocess

from tqdm import tqdm


def create_test_bash_script():
    """
    Create a bash script that generates numbers 1 to 1000000
    This is just for illustration purpose to simulate a long running bash command
    """
    with open('hello', 'w') as bash_file:
        bash_file.write('''\
    #!/bin/bash
    # Tested using bash version 4.1.5
    for ((i=1;i<=1000000;i++));
    do
        # your-unix-command-here
        echo $i
    done
    ''')


def run_task(cmd):

    try:
        # create a default tqdm progress bar object, unit='B' definnes a String that will be used to define the unit of each iteration in our case bytes
        with tqdm(unit='B', unit_scale=True, miniters=1, desc="run_task={}".format(cmd)) as t:
            process = subprocess.Popen(cmd, shell=True, bufsize=1, universal_newlines=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)

            # print subprocess output line-by-line as soon as its stdout buffer is flushed in Python 3:
            for line in process.stdout:
                # Update the progress, since we do not have a predefined iterator
                # tqdm doesnt know before hand when to end and cant generate a progress bar
                # hence elapsed time will be shown, this is good enough as we know
                # something is in progress
                t.update()
                # forces stdout to "flush" the buffer
                sys.stdout.flush()

            process.stdout.close()

            return_code = process.wait()

            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, cmd)

    except subprocess.CalledProcessError as e:
        sys.stderr.write(
            "common::run_command() : [ERROR]: output = %s, error code = %s\n"
            % (e.output, e.returncode))


create_test_bash_script()

run_task('chmod 755 hello && ./hello')

# run_task('xx*3238') # this will fail not a valid command