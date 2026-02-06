from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.typechecker import Bool, Int, Unit, typecheck


def test_typechecker_basics() -> None:
    assert typecheck(parse(tokenize("1"))) == Int()
    typecheck(parse(tokenize("true"))) == Bool()
    typecheck(parse(tokenize(""))) == Unit()


def test_binary_op() -> None:
    assert typecheck(parse(tokenize("1 + 2"))) == Int()


def test_while_do() -> None:
    assert typecheck(parse(tokenize("while true do { 1 + 2 }"))) == Int()
    assert isinstance(typecheck(
        # should this return Bool instead? Currently TopLevel does not return anything like Block does
        parse(tokenize("var i = 0; while i < 5 do { i = i + 1 }; true"))), Unit)
