import unittest

import pytest


class TestExample(unittest.TestCase):
    def test_case_1(self):
        """
        Objective:
            This test is designed to verify the functionality of test case 1

        Approvals:
            - The first step is executed successfully
            - The second step is executed successfully

        Test steps:
            1. Perform the first step
            2. Verify that The first verification step
            3. Perform the second step
            4. Verify that The second verification step
            5. Verify that invalid
        """

    def test_case_2(self):
        """
        Objective:
            This test is designed to verify the functionality of test case 2

        Approvals:
            - The precondition is met
            - The test step is executed successfully

        Preconditions:
            1. The system is in a stable state

        Test steps:
            1. Perform the test step
            2. Verify that The verification step
        """


class TestExample2:
    def test_case_11(self):
        """
        Objective:
            This test is designed to verify the functionality of test case 1

        Approvals:
            - The first step is executed successfully
            - The second step is executed successfully

        Test steps:
            1. Perform the first step
            2. Verify that The first verification step
            3. Perform the second step
            4. Verify that The second verification step
            5. Verify that invalid
        """

    def test_case_22(self):
        """
        Objective:
            This test is designed to verify the functionality of test case 2

        Approvals:
            - The precondition is met
            - The test step is executed successfully

        Preconditions:
            1. The system is in a stable state

        Test steps:
            1. Perform the test step
            2. Verify that The verification step
        """

    def my_function_test():
        pass

    @pytest.fixture
    def my_fixture(self):
        pass


def test_case_example():
    """
    Objective:
        This test is designed to verify the functionality of test case example

    Approvals:
        - first acceptance criterion
        - second acceptance criterion
        - third acceptance criterion

    Preconditions:
        1. first precondition
        2. second precondition

    Data-driven-test:
        - first driven-data-test
        - second driven-data-test

    Test steps:
        1. test step
        2. Verify that verification step corresponding to any acceptance criterion
        3. test step
        7. Verify that verification step corresponding to any acceptance criterion.
        5. Verify step
        2. Verify that verification step corresponding to to any acceptance criterion
    """
