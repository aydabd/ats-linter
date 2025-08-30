import ast
import pytest
from ats_linter.ast_test_module_factory import ASTTestModuleFactory
from ats_linter.data_classes import TestClass, TestCase, PytestFixture

def make_ast_nodes(source):
    return list(ast.parse(source).body)

def test_get_test_classes():
    src = '''
class TestFoo: pass
class NotATest: pass
class TestBar: pass
'''
    nodes = make_ast_nodes(src)
    test_classes = ASTTestModuleFactory.get_test_classes(nodes)
    assert len(test_classes) == 2
    assert all(cls.name.startswith('Test') for cls in test_classes)

def test_get_function_nodes():
    src = '''
def foo(): pass
def bar(): pass
'''
    nodes = make_ast_nodes(src)
    funcs = ASTTestModuleFactory.get_function_nodes(nodes)
    assert len(funcs) == 2
    assert all(isinstance(f, ast.FunctionDef) for f in funcs)

def test_is_test_case():
    src = '''
def test_foo(): pass
def not_a_test(): pass
'''
    nodes = make_ast_nodes(src)
    assert ASTTestModuleFactory.is_test_case(nodes[0])
    assert not ASTTestModuleFactory.is_test_case(nodes[1])

def test_is_pytest_fixture():
    src = '''
import pytest
@pytest.fixture()
def my_fixture(): pass
'''
    nodes = make_ast_nodes(src)
    func = nodes[1]
    assert ASTTestModuleFactory.is_pytest_fixture(func)

def test_parse_test_classes_extracts_cases_and_fixtures():
    src = '''
import pytest
class TestFoo:
    def test_bar(self):
        """A test case"""
        pass
    @pytest.fixture()
    def my_fixture(self):
        """A fixture"""
        pass
'''
    nodes = make_ast_nodes(src)
    test_classes = ASTTestModuleFactory.get_test_classes(nodes)
    parsed = ASTTestModuleFactory.parse_test_classes(test_classes)
    assert len(parsed) == 1
    test_class = parsed[0]
    assert isinstance(test_class, TestClass)
    assert any(isinstance(tc, TestCase) for tc in test_class.test_cases)
    assert any(isinstance(fx, PytestFixture) for fx in test_class.fixtures)

def test_extract_entities_for_test_cases_and_fixtures():
    src = '''
import pytest
def test_foo(): """doc"""; pass
@pytest.fixture()
def my_fixture(): """doc"""; pass
'''
    nodes = make_ast_nodes(src)
    test_cases = ASTTestModuleFactory.extract_entities(
        nodes, TestCase, ASTTestModuleFactory.is_test_case
    )
    fixtures = ASTTestModuleFactory.extract_entities(
        nodes, PytestFixture, ASTTestModuleFactory.is_pytest_fixture
    )
    assert len(test_cases) == 1
    assert test_cases[0].name == 'test_foo'
    assert len(fixtures) == 1
    assert fixtures[0].name == 'my_fixture'
