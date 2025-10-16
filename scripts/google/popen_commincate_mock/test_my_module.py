import unittest
from unittest.mock import patch, Mock
from my_module import run_and_get_output


# Define a function to use as a side_effect
def mock_communicate_with_error():
    """Simulates a communicate() call that fails during decoding."""
    # A byte string that is invalid UTF-8
    invalid_utf8_bytes = b'hello \x99\xae world'

    # communicate() returns (stdout, stderr) tuples.
    # To cause a decode error later, return undecoded bytes.
    return (invalid_utf8_bytes, b'')


class TestMyModule(unittest.TestCase):
    @patch("subprocess.Popen")
    def test_run_and_get_output_decoding_error(self, mock_popen):
        """Test the path where a UnicodeDecodeError is handled."""

        # Create a mock instance for the Popen object
        mock_process_instance = Mock()

        # Set up the mock `communicate` method on the mock Popen instance
        mock_process_instance.communicate.side_effect = \
            lambda: mock_communicate_with_error()

        # Configure the mock Popen to return our mock instance
        mock_popen.return_value = mock_process_instance

        # Call the function being tested
        result = run_and_get_output(["some_command_that_produces_invalid_utf8"])

        # Verify that the expected error message was returned
        self.assertIn("Decoding error", result)
        self.assertIn("codec can't decode byte 0x99", result)


if __name__ == "__main__":
    unittest.main()
