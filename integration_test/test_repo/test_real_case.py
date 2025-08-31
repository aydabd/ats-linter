def add(a, b):
    return a + b


def test_add_success():
    """Objective:
        Ensure addition works as expected.

    Approvals:
        - The sum is correct

    Test steps:
        1. Add two numbers
        2. Verify that the sum is correct
    """
    assert add(2, 3) == 5


def test_add_pass():
    """Objective:
        Ensure addition works for equal numbers.

    Approvals:
        - The sum is correct

    Test steps:
        1. Add two equal numbers
        2. Verify that the sum is correct
    """
    assert add(2, 2) == 4
