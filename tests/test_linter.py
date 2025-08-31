import threading

import ats_linter.linter as linter_mod
from ats_linter.data_classes import TestCase
from ats_linter.description import (
    SECTION_APPROVALS,
    SECTION_OBJECTIVE,
    SECTION_TEST_STEPS,
)
from ats_linter.linter import (
    MANDATORY_SECTIONS,
    ATSTestCase,
    ATSTestCasesFactory,
    ATSTestCasesLinter,
    LintTestCase,
    lint_ats_test_case,
)


def make_docstring(sections):
    doc = []
    for name, content in sections.items():
        doc.append(f"{name}:")
        for line in content.splitlines():
            doc.append(f"    {line}")
    return "\n".join(doc)


def minimal_sections():
    return {
        SECTION_OBJECTIVE: "Test the objective section.",
        SECTION_APPROVALS: "- Approval 1\n- Approval 2",
        SECTION_TEST_STEPS: (
            "1. Do something\n2. Verify that step 1\n3. Do something else\n"
            "4. Verify that step 2"
        ),
    }


def test_atstestcase_len_and_dict():
    docstring = make_docstring(minimal_sections())
    tc = TestCase(name="test_foo", docstring=docstring, code="def test_foo(): pass")
    ats = ATSTestCase(tc)
    assert isinstance(ats.__dict__(), dict)
    # Should have 2 verify steps
    assert len(ats) == 2


def test_atstestcasesfactory_and_linter():
    docstring = make_docstring(minimal_sections())
    tc1 = TestCase(name="test_foo", docstring=docstring, code="def test_foo(): pass")
    tc2 = TestCase(name="test_bar", docstring=docstring, code="def test_bar(): pass")
    factory = ATSTestCasesFactory([tc1, tc2])
    assert len(factory) == 2
    linter = ATSTestCasesLinter(factory.ats_test_cases)
    assert linter.lint() is True


def test_linttestcase_missing_sections():
    # Missing approvals
    docstring = make_docstring(
        {
            SECTION_OBJECTIVE: "obj",
            SECTION_TEST_STEPS: "1. Do something\n2. Verify that step 1",
        },
    )
    tc = TestCase(
        name="test_missing",
        docstring=docstring,
        code="def test_missing(): pass",
    )
    ats = ATSTestCase(tc)
    linter = LintTestCase(ats)
    assert linter.lint() is False
    assert any(s.error_message for s in linter.sections if s.name == SECTION_APPROVALS)


def test_linttestcase_mismatched_approvals_and_steps():
    docstring = make_docstring(
        {
            SECTION_OBJECTIVE: "obj",
            SECTION_APPROVALS: "- Approval 1",
            SECTION_TEST_STEPS: (
                "1. Do something\n2. Verify that step 1\n3. Do something else\n"
                "4. Verify that step 2"
            ),
        },
    )
    tc = TestCase(
        name="test_mismatch",
        docstring=docstring,
        code="def test_mismatch(): pass",
    )
    ats = ATSTestCase(tc)
    linter = LintTestCase(ats)
    assert linter.lint() is False
    assert any("Mismatch" in (s.error_message or "") for s in linter.sections)


def test_check_section_presence_attribute_error():
    class DummySection:
        name = "Nonexistent"
        error_message = None

    class DummyDescription:
        pass  # No attribute for section

    linter = LintTestCase.__new__(LintTestCase)
    linter.test_description = DummyDescription()
    section = DummySection()
    linter._check_section_presence(section)
    assert "Missing" in section.error_message


def test_check_sections_with_none():
    class DummySection:
        def __init__(self, name):
            self.name = name
            self.error_message = None

    linter = LintTestCase.__new__(LintTestCase)
    linter.sections = [DummySection(name) for name in MANDATORY_SECTIONS]
    # Add a section that is not in MANDATORY_SECTIONS to trigger None
    linter.sections.append(DummySection("NotMandatory"))
    linter.test_description = type(
        "Dummy",
        (),
        {s.lower().replace(" ", "_"): True for s in MANDATORY_SECTIONS},
    )()
    linter._check_sections(MANDATORY_SECTIONS + ["NotMandatory"])
    # Should not raise


def test_lint_ats_test_case_exception():
    class BadLintTestCase(LintTestCase):
        def lint(self):
            raise ValueError("fail lint")

    tc = TestCase(name="bad", docstring="Objective:\nfoo", code="def bad(): pass")
    ats = ATSTestCase(tc)
    lock = threading.Lock()
    results = {}
    # Patch LintTestCase to our bad one
    orig = LintTestCase.__init__

    def fake_init(self, ats):
        pass

    LintTestCase.__init__ = fake_init
    LintTestCase.lint = BadLintTestCase.lint
    try:
        out = lint_ats_test_case(ats, results, lock)
        assert out is False
        assert results["bad"]["status"] is False
    finally:
        LintTestCase.__init__ = orig


def test_atstestcaseslinter_lint_all_pass(monkeypatch):
    # Patch lint_ats_test_case to always return True
    orig = linter_mod.lint_ats_test_case
    linter_mod.lint_ats_test_case = lambda *a, **kw: True
    try:
        tc1 = TestCase(
            name="test_foo",
            docstring="Objective:\nfoo",
            code="def test_foo(): pass",
        )
        ats1 = ATSTestCase(tc1)
        linter = ATSTestCasesLinter([ats1])
        assert linter.lint() is True
    finally:
        linter_mod.lint_ats_test_case = orig


def test_atstestcaseslinter_lint_multiple_workers(monkeypatch):
    orig = linter_mod.lint_ats_test_case
    linter_mod.lint_ats_test_case = lambda *a, **kw: True
    try:
        tc1 = TestCase(
            name="test_foo",
            docstring="Objective:\nfoo",
            code="def test_foo(): pass",
        )
        tc2 = TestCase(
            name="test_bar",
            docstring="Objective:\nbar",
            code="def test_bar(): pass",
        )
        ats1 = ATSTestCase(tc1)
        ats2 = ATSTestCase(tc2)
        linter = ATSTestCasesLinter([ats1, ats2])
        assert linter.lint() is True
    finally:
        linter_mod.lint_ats_test_case = orig


def test_atstestcaseslinter_lint_empty():
    linter = ATSTestCasesLinter([])
    assert linter.lint() is True
