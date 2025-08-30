from ats_linter.description import (
    SECTION_VERIFY,
    TestDescription,
    TestDescriptionFactory,
)


def test_testdescription_dict():
    docstring = """
    Objective:
        Ensure foo works
    Approvals:
        - It runs
    Preconditions:
        1. Bar is set
    Data-driven-test:
        - Data1
    Test steps:
        1. Do foo
    Verify:
        1. Check foo
    """
    desc = TestDescription(docstring)
    d = desc.__dict__()
    assert isinstance(d, dict)
    assert "objective" in d
    assert "approvals" in d
    assert "test_steps" in d
    assert "verify_steps" in d


def test_testdescriptionfactory_from_docstring():
    docstring = """
    Objective:
        Test something
    Approvals:
        - Should pass
    Test steps:
        1. Step one
    Verify:
        1. Step two
    """
    desc = TestDescriptionFactory.from_docstring(docstring)
    assert isinstance(desc, TestDescription)
    assert desc.objective is not None
    assert desc.test_steps
    assert desc.verify_steps


def test_testdescriptionfactory_handles_empty():
    desc = TestDescriptionFactory.from_docstring("")
    assert isinstance(desc, TestDescription)
    assert desc.objective is None
    assert desc.test_steps == {}
    assert desc.verify_steps == {}


def test_testdescription_handles_partial_sections():
    docstring = """
    Objective:
        Only objective
    """
    desc = TestDescriptionFactory.from_docstring(docstring)
    assert desc.objective == "Only objective"
    assert desc.test_steps == {}
    assert desc.verify_steps == {}


def test_parse_verify_steps():
    # Only one step contains SECTION_VERIFY
    test_steps = {
        1: "Do something",
        2: f"{SECTION_VERIFY} that foo works",
        3: "Another step",
    }
    result = TestDescriptionFactory.parse_verify_steps(test_steps)
    assert result == {2: f"{SECTION_VERIFY} that foo works"}

    # No step contains SECTION_VERIFY
    test_steps = {1: "Do something", 2: "Nothing to verify"}
    result = TestDescriptionFactory.parse_verify_steps(test_steps)
    assert result == {}
