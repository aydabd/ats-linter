from dataclasses import dataclass

from ats_linter.parallel_process import FileProcessorCocurrent


@dataclass
class DummyTestModule:
    test_classes: list


class DummyAsyncASTParser:
    def __init__(self, test_files):
        self.test_modules = [DummyTestModule([1, 2])]

    def __len__(self):
        return 42


class DummyFileCollector:
    def __init__(self, root_path):
        self.test_files = ["dummy1.py", "dummy2.py"]


def test_file_processor_cocurrent_len_and_iter(monkeypatch, tmp_path):
    # Patch dependencies
    monkeypatch.setattr("ats_linter.parallel_process.FileCollector", DummyFileCollector)
    monkeypatch.setattr(
        "ats_linter.parallel_process.AsyncASTParser",
        DummyAsyncASTParser,
    )
    processor = FileProcessorCocurrent(str(tmp_path))
    assert len(processor) == 42
    modules = list(processor)
    assert len(modules) == 1
    assert hasattr(modules[0], "test_classes")


def test_file_processor_cocurrent_dict(monkeypatch, tmp_path):
    monkeypatch.setattr("ats_linter.parallel_process.FileCollector", DummyFileCollector)
    monkeypatch.setattr(
        "ats_linter.parallel_process.AsyncASTParser",
        DummyAsyncASTParser,
    )
    processor = FileProcessorCocurrent(str(tmp_path))
    d = processor.__dict__()
    assert isinstance(d, list)
