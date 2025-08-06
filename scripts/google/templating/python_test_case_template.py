from string import Template

template_string = """
\'\'\'
@file ${file_name}.py
@brief Defines the ${file_brief} class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
\'\'\'

# standard modules
import gc
import logging
import os
import unittest

# third party modules
# import ipsumlorem

# local modules
from src import ERROR_LOG_FORMAT, LOG_DIR, LOG_EXT, UTF8          # logging constants
from src.generated_files import GENERATED_FILES

gc.enable()

# Configure logging
basename = os.path.basename(__file__)
stem = os.path.splitext(basename)[0]
file = stem + LOG_EXT
log_filename = os.path.join(GENERATED_FILES, LOG_DIR, file)
# override the default logging level WARN to lowest level so we can log all levels
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=ERROR_LOG_FORMAT, filemode="a", encoding=UTF8)

# create logger for module and restrict to module
# use raise in exception handling if we need send something inter-module
logger = logging.getLogger(__name__)
logger.propagate = False

# instantiate module levels vars here


# instantiate classes here



class ${class_name}(unittest.TestCase):
    \'\'\'
    @brief Tests ${class_brief} class functions.
    \'\'\'

    def test_my_function(self):
        \'\'\'
        @brief Tests ipsum lorem
        \'\'\'

        pass


if __name__ == \"__main__\":
    unittest.main(verbosity=${verbosity})

"""

data = {
    "file_name": "test_my_module",
    "file_brief": "test my module",
    "class_name": "TestMyClass",
    "class_brief": "MyClass",
    "verbosity": 2

}

template = Template(template_string)
output_content = template.substitute(data)

with open(f"{data['file_name']}.py", "w") as f:
    f.write(output_content)