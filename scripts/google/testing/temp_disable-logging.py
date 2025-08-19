import logging
import unittest


class MyTest(unittest.TestCase):
    def test_function_with_logging(self):
        # Store original logging level
        original_level = logging.getLogger().getEffectiveLevel()
        # Disable logging during the test
        logging.disable(logging.CRITICAL)

        # Call the function that produces logging output
        # tested_function()

        # Re-enable logging after the test
        logging.disable(original_level)