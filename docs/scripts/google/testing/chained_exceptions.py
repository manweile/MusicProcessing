import unittest
from unittest import TestCase


class MyError(Exception):
    pass


class AnotherError(Exception):
    pass


def function_that_raises_chained_exception():
    try:
        raise MyError("Original error")
    except MyError as e:
        raise AnotherError("Chained error") from e


class TestChainedExceptions(TestCase):
    def test_chained_exception(self):
        with self.assertRaises(AnotherError) as cm:
            function_that_raises_chained_exception()

        # Verify the __cause__ attribute for chained exceptions
        self.assertIsInstance(cm.exception.__cause__, MyError)
        self.assertEqual(str(cm.exception.__cause__), "Original error")


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestChainedExceptions('test_chained_exception'))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)