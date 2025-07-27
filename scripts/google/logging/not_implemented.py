# google ai search line python how to log argparse invalid command to log instead of console
import argparse
import inspect
import logging
import os
import sys


# Configure logging
dirpath = os.path.dirname(os.path.abspath(__file__))
basename = os.path.basename(__file__)
stem = os.path.splitext(basename)[0]
file = stem + ".log"
filename = os.path.join(dirpath, file)
# format = '\n%(asctime)s - %(levelname)s - %(message)s'
format = '\n%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s'
logging.basicConfig(filename=filename, level=logging.DEBUG, format=format, filemode="a", encoding="utf-8")
logger = logging.getLogger(__name__)


class CustomArgumentParser(argparse.ArgumentParser):
    def _print_message(self, message, file=None):
        # Check if the message is intended for stderr
        if file is sys.stderr:
            logger.error(f"Argparse Error: {message.strip()}")
        else:
            super()._print_message(message, file)


def some_function_that_has_warning():
    frame = inspect.currentframe()
    def_name = frame.f_code.co_name
    file_path = __file__
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    file_def = file_name + "." + def_name

    logger.warning(f"A warning has occurred in {file_def}")


def some_function_that_might_not_be_implemented():
    raise NotImplementedError()


def some_function_that_has_exception():
    raise Exception()


def main(args):
    """The main function of the application."""
    logger.info("Starting main application.")

    if args.subcommand == "error":
        some_function_that_might_not_be_implemented()
    elif args.subcommand == "exception":
        some_function_that_has_exception()
    elif args.subcommand == "warning":
        some_function_that_has_warning()

    logger.info("Main application finished successfully.")


if __name__ == "__main__":
    try:
        parser = CustomArgumentParser(description='Test Logger with args')
        subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

        warning_parser = subparsers.add_parser("warning")
        error_parser = subparsers.add_parser("error")
        exception_parser = subparsers.add_parser("exception")


        args = parser.parse_args()
        main(args)
    except NotImplementedError:
        logger.error("NotImplementedError", exc_info=True)
    except Exception:
        logger.exception("Exception", stack_info=True)
