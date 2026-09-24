# my_module.py
import logging

# Get the logger for this module
module_logger = logging.getLogger(__name__)

# Create a specific handler for this module's logs
module_file_handler = logging.FileHandler('module_specific.log')
module_file_handler.setLevel(logging.DEBUG)
module_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
module_file_handler.setFormatter(module_formatter)
module_logger.addHandler(module_file_handler)
# module_logger.propagate = False


def do_something():
    module_logger.debug("Debugging something in my_module.")
    module_logger.info("Info on something in my_module.")
    module_logger.warning("Warning on something in my_module.")
    # This message will also propagate to the root logger's handler (app.log)
    # unless module_logger.propagate = False