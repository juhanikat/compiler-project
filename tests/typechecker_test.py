import pytest

from compiler.my_types import Bool, FunType, Int, Unit
from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.typechecker import typecheck


def test_typechecker_basics() -> None:
    assert typecheck(parse(tokenize("1"))) == Int()
    assert typecheck(parse(tokenize("true"))) == Bool()
    assert typecheck(parse(tokenize(""))) == Unit()
    assert typecheck(parse(tokenize("var a = 1; a"))) == Int()


def test_binary_op() -> None:
    assert typecheck(parse(tokenize("1 + 2"))) == Int()
    assert typecheck(
        parse(tokenize("var a = 2; var b = a * a; a + b"))) == Int()

    with pytest.raises(TypeError):
        typecheck(parse(tokenize("var a = 1; var b = true; a + b")))


def test_functions() -> None:
    # TODO: Implement this?
    # assert typecheck(parse(tokenize(
    #    "var f(x, y) = { x + y }; f"))) == FunType(Int(), Int(), return_type=Int())

    assert typecheck(
        parse(tokenize("var f(x, y) = { x + y }; f(1, 2)"))) == Int()


def test_others() -> None:
    pass
    # assert typecheck(parse(tokenize("while true do { 1 + 2 }"))) == Unit()
    # assert typecheck(
    # parse(tokenize("var i = 0; while i < 5 do { i = i + 1 }; true"))) == Bool()
