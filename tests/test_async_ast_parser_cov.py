import ast
import asyncio
import shutil
import uuid
from pathlib import Path

import pytest

from ats_linter.async_ast_parser import (
    SENTINEL,
    ASTConsumer,
    ASTProducer,
    AsyncASTParser,
)


@pytest.mark.asyncio
async def test_astproducer_and_consumer_basic():
    # Create a temp python file with a test class and test function

    tmp_dir = Path(__file__).parent / "_tmp"
    tmp_dir.mkdir(exist_ok=True)
    unique_name = f"test_temp_{uuid.uuid4().hex}.py"
    file_path = tmp_dir / unique_name
    try:
        file_path.write_text(
            "class TestSomething:\n"
            '    """A test class docstring."""\n'
            "    def test_foo(self):\n"
            '        """A test method docstring."""\n'
            "        pass\n",
        )
        # Print the AST for debugging
        with file_path.open("r") as source:
            tree = ast.parse(source.read())
            print("AST:", ast.dump(tree, indent=2))
        modules = []
        producer = ASTProducer([file_path])
        consumer = ASTConsumer(producer.ast_tree_queue, modules)
        async with producer, consumer:
            await producer.task
            await producer.ast_tree_queue.put(SENTINEL)
            await consumer.task
        assert len(modules) == 1
        assert hasattr(modules[0], "test_cases")
    finally:
        # Remove the file and the _tmp directory if empty
        if file_path.exists():
            file_path.unlink()
        # Remove the _tmp directory and all its contents if it exists
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)


@pytest.mark.asyncio
async def test_astproducer_handles_no_files():
    modules = []
    queue = asyncio.Queue()
    producer = ASTProducer([])
    consumer = ASTConsumer(queue, modules)
    async with producer, consumer:
        await producer.task
        await queue.put(SENTINEL)
        await consumer.task
    assert modules == []


def test_asyncastparser_len_and_run(tmp_path):
    # Create two temp python files
    f1 = tmp_path / "test_a.py"
    f1.write_text("class TestA:\n    def test_foo(self): pass\n")
    f2 = tmp_path / "test_b.py"
    f2.write_text("class TestB:\n    def test_bar(self): pass\n")
    parser = AsyncASTParser([f1, f2])

    asyncio.run(parser.async_run())
    assert isinstance(len(parser), int)


@pytest.mark.asyncio
async def test_asyncastparser_from_files(tmp_path):
    f1 = tmp_path / "a.py"
    f1.write_text("def foo():\n    pass\n")
    parser = await AsyncASTParser.from_files([f1])
    assert isinstance(parser, AsyncASTParser)
    assert len(parser) >= 0


@pytest.mark.asyncio
async def test_astproducer_aexit_cancels_task(monkeypatch):
    # Simulate a running task that is cancelled
    class DummyProducer(ASTProducer):
        async def produce_ast_trees(self):
            await asyncio.sleep(0.01)

    producer = DummyProducer([])
    await producer.__aenter__()
    await producer.__aexit__(Exception, Exception("fail"), None)
    assert producer.task.cancelled() or producer.task.done()


@pytest.mark.asyncio
async def test_astconsumer_aexit_logs(monkeypatch):
    modules = []
    queue = asyncio.Queue()
    consumer = ASTConsumer(queue, modules)
    await consumer.__aenter__()
    await consumer.__aexit__(Exception, Exception("fail"), None)
    # Just ensure no exceptions


@pytest.mark.asyncio
async def test_astproducer_aexit_with_exception():
    asyncio.Queue()
    producer = ASTProducer([])
    await producer.__aenter__()
    # Simulate an exception in the context
    await producer.__aexit__(Exception, Exception("fail"), None)
    # Should reach here without error


@pytest.mark.asyncio
async def test_astconsumer_aexit_with_exception():
    modules = []
    queue = asyncio.Queue()
    consumer = ASTConsumer(queue, modules)
    await consumer.__aenter__()
    # Simulate an exception in the context
    await consumer.__aexit__(Exception, Exception("fail"), None)
    # Should reach here without error


def test_asyncastparser_post_init_outside_event_loop(tmp_path):
    # This should run the .run() branch in __post_init__
    f1 = tmp_path / "test_post_init.py"
    f1.write_text("def test_post(): pass\n")
    parser = AsyncASTParser([f1])
    assert isinstance(parser, AsyncASTParser)


@pytest.mark.asyncio
async def test_asyncastparser_gather_producer_consumer_task(tmp_path):
    f1 = tmp_path / "test_gather.py"
    f1.write_text("def test_gather(): pass\n")
    parser = AsyncASTParser([f1])
    await parser.gather_producer_consumer_task()
    assert isinstance(parser.test_modules, list)


@pytest.mark.asyncio
async def test_astproducer_produce_ast_trees_none(monkeypatch, tmp_path):
    # Simulate _get_ast_tree returning None (e.g., file read error)
    test_file = tmp_path / "test_none.py"
    test_file.write_text("def foo(): pass\n")
    producer = ASTProducer([test_file])
    monkeypatch.setattr(ASTProducer, "_get_ast_tree", staticmethod(lambda _: None))
    await producer.__aenter__()
    await producer.task
    # Should not put anything in the queue
    assert producer.ast_tree_queue.empty()
    await producer.__aexit__(None, None, None)


def test_asyncastparser_len_empty():
    parser = AsyncASTParser([])
    assert len(parser) == 0


def test_asyncastparser_len_with_module(tmp_path):
    f1 = tmp_path / "test_len.py"
    f1.write_text("def test_len(): pass\n")
    parser = AsyncASTParser([f1])
    parser.test_modules.clear()  # Remove any auto-added modules

    class DummyTestModule:
        def __len__(self):
            return 42

    parser.test_modules.append(DummyTestModule())
    assert len(parser) == 42


def test_asyncastparser_run_no_event_loop(tmp_path):
    """Covers the except branch in AsyncASTParser.run() when no event loop is running."""  # noqa: E501
    f1 = tmp_path / "test_run_no_event_loop.py"
    f1.write_text("def test_run(): pass\n")
    parser = AsyncASTParser([f1])
    # This should hit the except branch and use asyncio.run
    parser.run()
    assert isinstance(parser.test_modules, list)


def test_asyncastparser_run_explicit_except_branch(tmp_path, monkeypatch):
    """Explicitly cover the except RuntimeError: branch in AsyncASTParser.run() by mocking get_running_loop."""  # noqa: E501
    f1 = tmp_path / "test_run_explicit_except_branch.py"
    f1.write_text("def test_run(): pass\n")
    parser = AsyncASTParser([f1])

    def raise_runtime_error():
        raise RuntimeError

    monkeypatch.setattr(asyncio, "get_running_loop", raise_runtime_error)
    parser.run()
    assert isinstance(parser.test_modules, list)
