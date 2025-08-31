import pytest


def test_valid_case():
    """Objective:
        Ensure addition works as expected.

    Approvals:
        - The sum is correct

    Preconditions:
        1. Both numbers are integers

    Test steps:
        1. Add two numbers
        2. Verify that the sum is correct
    """
    assert 2 + 2 == 4

def test_also_valid():
    """Objective:
        Ensure subtraction works as expected.

    Approvals:
        - The difference is correct

    Preconditions:
        1. Both numbers are integers

    Test steps:
        1. Subtract two numbers
        2. Verify that the difference is correct
    """
    assert 5 - 3 == 2
