import pytest

from compiler.my_ast import (BinaryOp, Function, Identifier, IfThen,
                             IfThenElse, Literal)
from compiler.parser import parse
from compiler.tokenizer import tokenize


def test_parser_basics() -> None:
    assert parse(tokenize("1 + 2")) == BinaryOp(Literal(1), "+", Literal(2))
    assert parse(tokenize("a + b")) == BinaryOp(Identifier("a"),
                                                "+", Identifier("b"))


def test_parentheses() -> None:
    assert parse(tokenize("(1 + 2) + 3 * 4")) == BinaryOp(
        BinaryOp(Literal(1),
                 '+',
                 Literal(2)),
        '+',
        BinaryOp(Literal(3),
                 '*',
                 Literal(4))
    )
    parse(tokenize("1 + (2 + 3) * 4"))


def test_empty_input() -> None:
    assert parse(tokenize("")) is None


def test_garbage_at_end() -> None:
    with pytest.raises(Exception):
        parse(tokenize("1 + 2 xd"))
    with pytest.raises(Exception):
        parse(tokenize("1 + 2 +"))


def test_if_then_else() -> None:
    assert parse(tokenize("if 1 then 2")) == IfThen(Literal(1), Literal(2))
    assert parse(tokenize("if 1 then 2 else 3 + 4")) == IfThenElse(Literal(1),
                                                                   Literal(2),
                                                                   BinaryOp(Literal(3),
                                                                            "+",
                                                                            Literal(4)))
    assert parse(tokenize("if 1 then if 2 then 3 else  4 + 5 * 6 else 5")) == \
        IfThenElse(Literal(1),
                   IfThenElse(Literal(2),
                              Literal(3),
                              BinaryOp(Literal(4),
                                       "+",
                                       BinaryOp(Literal(5),
                                                "*",
                                                Literal(6)
                                                )
                                       )
                              ),
                   Literal(5))
    parse(tokenize("if a then 2 else b + 4"))
    with pytest.raises(Exception):
        parse(tokenize("if 1 then 2 else"))
        parse(tokenize("if 1 else 2"))
        parse(tokenize("if 1"))
        parse(tokenize("if 1 then if 2 else 3"))


def test_functions() -> None:
    assert parse(tokenize("f(1, 2)")) == Function("f", Literal(1), Literal(2))
    assert parse(tokenize("g(1 , 2 + 3, 3 * 4)")) == Function("g",
                                                              Literal(1),
                                                              BinaryOp(Literal(2),
                                                                       "+",
                                                                       Literal(3)),
                                                              BinaryOp(Literal(3),
                                                                       "*",
                                                                       Literal(4)))
    assert parse(tokenize("h(a, b + c)")) == Function("h",
                                                      Identifier("a"),
                                                      BinaryOp(Identifier("b"),
                                                               "+",
                                                               Identifier("c")))


"""
def test_operator_presedence() -> None:
    binary_op = parse(tokenize(r"a + b % c"))
    print(binary_op)
    assert type(binary_op) == BinaryOp
    assert binary_op.right == BinaryOp(
        Identifier('b'), r"%", Identifier("c"))

    binary_op = parse(tokenize(r"a * b + c / d"))
    print(binary_op)
    assert binary_op == BinaryOp(BinaryOp(Identifier(
        'a'), r"*", Identifier('b')), r"+", BinaryOp(Identifier('c'), "/", Identifier('d')))

    binary_op = parse(tokenize(r"a + b % c and d"))
    print(binary_op)
    assert binary_op == BinaryOp(Identifier('a'), r"+", BinaryOp(
        Identifier('b'), r"%", BinaryOp(Identifier('c'), "and", Identifier('d'))))
"""
