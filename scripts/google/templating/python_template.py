from string import Template

template_string = """
\'\'\'
@file ${file_name}.py
@brief Defines the ${class_description} class.

@author Gerald Manweiler
@copyright @showdate "%Y" GWN Software. All rights reserved.
\'\'\'

# standard modules
import gc
import logging
import os

# third party modules
# import ipsumlorem

# local modules
from src import FILE_LOG_FORMAT, LOG_DIR, LOG_EXT, UTF8          # logging modules
from src.generated_files import GENERATED_FILES

gc.enable()

# Configure logging
basename = os.path.basename(__file__)
stem = os.path.splitext(basename)[0]
file = stem + LOG_EXT
log_filename = os.path.join(GENERATED_FILES, LOG_DIR, file)

logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=FILE_LOG_FORMAT, filemode="a", encoding=UTF8)
logger = logging.getLogger(__name__)
# override the default logging level WARN to lowest level so we can log all level messages
logger.setLevel(logging.DEBUG)


class ${class_name}():
    \'\'\'
    @brief Defines the base ${class_description} processing used by project.
    \'\'\'

    def __init__(self):
        \'\'\'
        @brief Initialize the ${class_name} class.

        @details A basic class implementation with no instantiation parameters.

        @return ${class_name} {instance} An instance of the class.
        \'\'\'

        pass
"""

data = {
    "file_name": "my_module",
    "class_description": "my class",
    "class_name": "MyClass"
}

template = Template(template_string)
output_content = template.substitute(data)

with open(f"{data['file_name']}.py", "w") as f:
    f.write(output_content)