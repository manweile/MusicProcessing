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

# third party modules
# import ipsumlorem

# local modules
# import ipsumlorem

gc.enable()


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