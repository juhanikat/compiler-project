import pytest

from compiler.interpreter import interpret
from compiler.my_ast import Expression
from compiler.parser import parse
from compiler.tokenizer import tokenize


def test_interpreter_basics() -> None:
    assert interpret(parse(tokenize("2 + 3"))) == 5
    assert interpret(parse(tokenize("2 - 3"))) == -1
    assert interpret(parse(tokenize("2 - -3"))) == 5
    assert interpret(parse(tokenize("2 + 2 + 3"))) == 7
    assert interpret(parse(tokenize("2 / 4"))) == 0.5
    assert interpret(parse(tokenize("2 + 2 / 4 * 5"))) == 4.5
    assert interpret(parse(tokenize("var x = 5; x"))) == 5
    assert interpret(parse(tokenize("var x = 5; x = x; x"))) == 5
    assert interpret(parse(tokenize("-2"))) == -2
    assert interpret(parse(tokenize("2 + -2"))) == 0
    with pytest.raises(Exception):
        interpret(parse(tokenize("x = 5")))


def test_variables() -> None:
    assert interpret(parse(tokenize("var x = 3; x"))) == 3
    assert interpret(parse(tokenize("var x = 3; var y = 4; x + y"))) == 7
    assert interpret(parse(tokenize("var x = 3; var y = 4; x = y"))) == None
    assert interpret(parse(tokenize("var x = 1; { x = 2; x }"))) == 2
    assert interpret(parse(tokenize("var x = 2; x = (x + -2); x"))) == 0
    assert interpret(
        parse(tokenize("var x = 3; var y = 4; x = y; x + y + x"))) == 12
    with pytest.raises(Exception):
        interpret(parse(tokenize("var x = 3; 2 = x")))


def test_logicals() -> None:
    assert interpret(parse(tokenize("true and false"))) == False
    assert interpret(parse(tokenize("true and true"))) == True
    assert interpret(parse(tokenize("true or false"))) == True
    assert interpret(parse(tokenize("1 or 0"))) == True
    assert interpret(
        parse(tokenize("var moi = true; var hei = false; moi or hei"))) == True

    # right_size should be false since this should short_circuit
    assert interpret(
        parse(tokenize("var right_side = false; true or { right_side = true; true }; right_side"))) == False
    assert interpret(
        parse(tokenize("var right_side = false; false and { right_side = false; true }; right_side"))) == False

    with pytest.raises(Exception):
        interpret(parse(tokenize("true or or false")))


def test_blocks() -> None:
    assert interpret(parse(tokenize("{ 2 + 3 }"))) == 5
    assert interpret(parse(tokenize("{ 2 + 3; 2 + 4 }"))) == 6
    assert interpret(parse(tokenize("{ { 2 + 3; 2 + 4 } { 5 } }"))) == 5
    assert interpret(parse(tokenize("{ 2 + 3; }"))) == None
    assert interpret(parse(tokenize("{ 2 + 3; { 3 + 4; } }"))) == None
    assert interpret(parse(tokenize("{ 2 + 3; { 3 + 4; }; }"))) == None


def test_while_do() -> None:
    assert interpret(
        parse(tokenize("var x = 1; while x < 5 do { x = x + 1 }"))) == None

    assert interpret(
        parse(tokenize("var x = 1; while x < 5 do { x = x + 1 }; x"))) == 5

    assert interpret(parse(tokenize("{ 2 + 3; 2 + 4 }"))) == 6
    assert interpret(parse(tokenize("{ { 2 + 3; 2 + 4 } { 5 } }"))) == 5


def test_functions() -> None:
    assert interpret(
        parse(tokenize("var f() = { true }; f()"))) == True
    assert interpret(
        parse(tokenize("var f(a, b) = { a + b }; f(1, 2)"))) == 3
    assert interpret(
        parse(tokenize("var f(a, b) = { a * b }; f(1, 2)"))) == 2
    # TODO: you should be able to change function values later! (should this be f(a,b) = new_value OR f = new_value?)
    # interpret(
    #    parse(tokenize("var f(a, b) = { a * b }; f(a, b) = { a + b }; f(1, 2)"))) == 3

    assert interpret(
        parse(tokenize("var f(a, b) = { a = 2; a + b }; f(1, 2)"))) == 4

    # variable scope tests
    assert interpret(
        parse(tokenize("var f(a, b) = { a = 2 }; var a = 5; f(1, 2); a"))) == 5
    assert interpret(
        parse(tokenize("var f() = { outer = 2 }; var outer = 5; f(); outer"))) == 2

    with pytest.raises(Exception):
        interpret(parse(tokenize("var f() = 2")))
    with pytest.raises(Exception):
        interpret(parse(tokenize("var f() = f()")))


def test_built_in_funcs() -> None:
    assert interpret(parse(tokenize("print_int(3)"))) == None
    assert interpret(
        parse(tokenize("var f(i) = { print_int(i) }; f(150); true"))) == True
    assert interpret(parse(tokenize("print_bool(true)"))) == None
    # commented since otherwise input is lways needed when running tests
    # assert isinstance(interpret(parse(tokenize("read_int()"))), int)
