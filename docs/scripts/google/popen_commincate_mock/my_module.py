import subprocess


def run_and_get_output(command):
    """Runs a command and returns its output."""
    try:
        # Popen without `encoding` or `text=True` returns bytes
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        # The decode() call is where the error can occur
        return stdout.decode("utf-8")

    except UnicodeDecodeError as e:
        return f"Decoding error: {e}"
