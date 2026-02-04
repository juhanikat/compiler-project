import pytest

from compiler.interpreter import interpret
from compiler.my_ast import Expression
from compiler.parser import parse
from compiler.tokenizer import tokenize


def test_interpreter_basics() -> None:
    assert interpret(parse(tokenize("2 + 3"))) == 5
    assert interpret(parse(tokenize("2 + 2 + 3"))) == 7
    assert interpret(parse(tokenize("var x = 5; x"))) == 5
    with pytest.raises(Exception):
        interpret(parse(tokenize("x = 5")))


def test_variables() -> None:
    assert interpret(parse(tokenize("var x = 3; x"))) == 3
    assert interpret(parse(tokenize("var x = 3; var y = 4; x + y"))) == 7
    assert interpret(parse(tokenize("var x = 3; var y = 4; x = y"))) == None
    assert interpret(
        parse(tokenize("var x = 3; var y = 4; x = y; x + y + x"))) == 12
    with pytest.raises(Exception):
        print(interpret(parse(tokenize("var x = 3; 2 = x"))))


def test_blocks() -> None:
    assert interpret(parse(tokenize("{ 2 + 3 }"))) == 5
    assert interpret(parse(tokenize("{ 2 + 3; 2 + 4 }"))) == 6
    assert interpret(parse(tokenize("{ { 2 + 3; 2 + 4 } { 5 } }"))) == 5
