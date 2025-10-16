import unittest

class CustomTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        print(f"PASS: {test._testMethodName}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        print(f"FAIL: {test._testMethodName} - {err[1]}")

    def addError(self, test, err):
        super().addError(test, err)
        print(f"ERROR: {test._testMethodName} - {err[1]}")

class CustomTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)

# Example Usage
class MyTests(unittest.TestCase):
    def test_success(self):
        self.assertTrue(True)

    def test_failure(self):
        self.assertEqual(1, 2)

    def test_error(self):
        raise ValueError("Something went wrong")

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MyTests))
    runner = CustomTestRunner(verbosity=1)
    runner.run(suite)