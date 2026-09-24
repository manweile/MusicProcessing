import logging
from unittest import TestCase


class MyTest(TestCase):
    def setUp(self):
        self.logger = logging.getLogger('my_logger')
        # Assuming a StreamHandler is attached to this logger
        self.original_handlers = self.logger.handlers[:]
        for handler in self.original_handlers:
            if isinstance(handler, logging.StreamHandler):
                self.logger.removeHandler(handler)

    def tearDown(self):
        # Restore original handlers
        self.logger.handlers = self.original_handlers

    def test_function_with_logging(self):
        # Call the function that produces logging output
        # tested_function()
        pass
