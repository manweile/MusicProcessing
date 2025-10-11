# test_my_module.py
import unittest
from unittest.mock import patch
from my_module import main_function


class TestMainFunction(unittest.TestCase):
    @patch('my_module._helper_function')
    def test_main_function_with_mocked_helper(self, mock_helper):
        # Configure the mock to return a specific value
        mock_helper.return_value = "mocked_helper_value"

        # Call the function being tested
        result = main_function()

        # Assert the expected outcome
        self.assertEqual(result, "Main function output: mocked_helper_value")
        # Optionally, assert that the mock was called
        mock_helper.assert_called_once()


if __name__ == '__main__':
    unittest.main()
