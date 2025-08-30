from ats_linter.data_classes import Section

def test_section_dict():
    s = Section(name="foo", error_message=None)
    d = s.__dict__()
    assert d == {"name": "foo", "error_message": None}
    s2 = Section(name="bar", error_message="err")
    d2 = s2.__dict__()
    assert d2 == {"name": "bar", "error_message": "err"}
