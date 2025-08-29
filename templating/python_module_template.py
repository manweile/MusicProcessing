import os
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
# import ipsumlorem
# from ipsum import lorem

# third party modules
# import ipsumlorem
# from ipsum import lorem

# local module methods
from src import add_module_handler
# local module constants
# from src import IPSUM_LOREM
# from src.generated_files import GENERATED_FILES
# local module errors
# from src import IpsumLoremError
# local module classes
# from src.dolor import IpsumLorem

gc.enable()

# Configure logging
logger = logging.getLogger(__name__)
basename = os.path.basename(__file__)
add_module_handler(logger, basename, logging.DEBUG, propagate=True)

# instantiate classes here
# ipsum_lorem = IpsumLorem()

# instantiate module levels vars here
# IPSUM_LOREM = "ipsum lorem"


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

if __name__ == "__main__":
    '''
    @brief Top level script environment entry point.
    '''

    # @todo use argparse or some other cli param entry paradigm
    data = {
        "file_name": "my_module",
        "class_description": "my class",
        "class_name": "MyClass"
    }

    template = Template(template_string)
    output_content = template.substitute(data)

    path = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(path, f"{data['file_name']}.py")

    with open(file, "w") as new_file:
        new_file.write(output_content)
