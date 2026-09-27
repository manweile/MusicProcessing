# my_module.py
def _helper_function():
    """A private helper function."""
    return "original_helper_value"


def main_function():
    """The function to be tested, which calls the helper."""
    return f"Main function output: {_helper_function()}"
