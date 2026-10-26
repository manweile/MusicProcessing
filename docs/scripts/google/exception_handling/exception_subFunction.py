# search string: python find what excpetion subfuncxtion throws and re-raise it


def sub_function():
    """A sub-function that might raise an exception."""
    # Simulate an error
    raise ValueError("Something went wrong in the sub-function!")


def main_function():
    """Calls the sub-function and re-raises any exception caught."""
    try:
        sub_function()
    except ValueError as e:
        print(f"Caught a ValueError: {e}")
        # Re-raise the caught exception
        raise TypeError(f"Chained {type(e).__name__} ") from e
    except Exception as e:
        print(f"Caught an unexpected exception: {type(e).__name__}: {e}")
        # Re-raise the caught exception
        raise


if __name__ == "__main__":
    try:
        main_function()
    except Exception as e:
        print(f"Exception propagated to the main execution: {type(e).__name__}: {e}")
