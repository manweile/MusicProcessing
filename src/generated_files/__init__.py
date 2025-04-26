'''!
@todo package documentation
'''

import os

# want the directory so don't have to have a "magic spell" else where in code
script_directory = os.path.dirname(os.path.abspath(__file__))

__all__ = ['script_directory']