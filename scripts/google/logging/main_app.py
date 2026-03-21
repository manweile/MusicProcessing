# main_app.py
import logging
import scripts.google.templating.my_module as my_module

# Configure the root logger to log to a general file
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Get the logger for the main application
app_logger = logging.getLogger(__name__)
app_logger.info("Application started.")

my_module.do_something()
