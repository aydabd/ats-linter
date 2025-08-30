import ast
import asyncio
from pathlib import Path
import tempfile
import pytest
from ats_linter.async_ast_parser import ASTProducer, ASTConsumer, AsyncASTParser, SENTINEL
from ats_linter.data_classes import TestModule

def test_astproducer_get_ast_tree(tmp_path):
    file = tmp_path / "test_file.py"
    file.write_text("def foo(): pass\n")
    ast_tree = ASTProducer._get_ast_tree(file)
    assert isinstance(ast_tree, ast.Module)
    assert any(isinstance(n, ast.FunctionDef) for n in ast_tree.body)

def test_astproducer_is_test_file(tmp_path):
    test_file = tmp_path / "test_foo.py"
    non_test_file = tmp_path / "foo.py"
    test_file.write_text("")
    non_test_file.write_text("")
    assert ASTProducer.is_test_file(test_file)
    assert not ASTProducer.is_test_file(non_test_file)

@pytest.mark.asyncio
async def test_astproducer_and_consumer(tmp_path):
    # Create a test file
    test_file = tmp_path / "test_sample.py"
    test_file.write_text("""
def test_foo(): pass
""")
    # Producer
    producer = ASTProducer([test_file])
    await producer.__aenter__()
    # Consumer
    test_modules = []
    consumer = ASTConsumer(producer.ast_tree_queue, test_modules)
    await consumer.__aenter__()
    # Run producer and consumer
    await producer.task
    await producer.ast_tree_queue.put(SENTINEL)  # Use the correct sentinel
    await consumer.task
    await producer.__aexit__(None, None, None)
    await consumer.__aexit__(None, None, None)
    assert test_modules
    assert isinstance(test_modules[0], TestModule)

@pytest.mark.asyncio
async def test_async_ast_parser(tmp_path):
    test_file = tmp_path / "test_integration.py"
    test_file.write_text("""
def test_bar(): pass
""")
    # Use the async factory method for testing
    parser = await AsyncASTParser.from_files([test_file])
    assert len(parser.test_modules) == 1
    assert parser.test_modules[0].name == "test_integration"
