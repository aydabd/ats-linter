from ats_linter import exception


def test_ATSLinterError_inheritance():
    err = exception.ATSLinterError("msg")
    assert isinstance(err, Exception)
    assert str(err) == "msg"


def test_ATSFileCollectionError_inheritance():
    err = exception.ATSFileCollectionError("file error")
    assert isinstance(err, exception.ATSLinterError)
    assert str(err) == "file error"


def test_ATSASTParseError_inheritance():
    err = exception.ATSASTParseError("ast error")
    assert isinstance(err, exception.ATSLinterError)
    assert str(err) == "ast error"
