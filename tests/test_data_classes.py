from ats_linter.data_classes import TestCase, TestClass, TestModule


def test_testclass_len_and_dict():
    tc1 = TestCase(name="t1", docstring="doc1", code="code1")
    tc2 = TestCase(name="t2", docstring="doc2", code="code2")
    test_class = TestClass(
        name="A", docstring="docA", test_cases=[tc1, tc2], fixtures=[]
    )
    assert len(test_class) == 2
    d = test_class.__dict__()
    assert d["nbr_of_test_cases"] == 2
    assert d["test_cases"][0]["name"] == "t1"
    assert d["fixtures"] == []
    assert d["nbr_of_fixtures"] == 0


def test_testmodule_len_and_dict():
    tc1 = TestCase(name="t1", docstring="doc1", code="code1")
    tc2 = TestCase(name="t2", docstring="doc2", code="code2")
    test_class = TestClass(name="A", docstring="docA", test_cases=[tc1], fixtures=[])
    mod = TestModule(
        name="mod1", test_classes=[test_class], test_cases=[tc2], fixtures=[]
    )
    assert len(mod) == 2
    d = mod.__dict__()
    assert d["test_module"] == "mod1"
    assert d["test_classes"][0]["name"] == "A"
    assert d["test_cases"][0]["name"] == "t2"
