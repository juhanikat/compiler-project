import pytest

from compiler.my_ast import (BinaryOp, Block, Function, Identifier, IfThen,
                             IfThenElse, Literal, UnaryOp, Variable)
from compiler.parser import parse
from compiler.tokenizer import SourceLocation, tokenize


def test_parser_basics() -> None:
    assert parse(tokenize("1")) == Literal(1)
    assert parse(tokenize("1 + 2")) == BinaryOp(Literal(1), "+", Literal(2))
    assert parse(tokenize("a + b")) == BinaryOp(Identifier("a"),
                                                "+", Identifier("b"))
    assert parse(tokenize("hapsu + hapsu2")
                 ) == BinaryOp(Identifier("hapsu"), "+", Identifier("hapsu2"))


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
    assert parse(tokenize("1 + (2 + 3) * 4")) == \
        BinaryOp(Literal(1),
                 '+',
                 BinaryOp(BinaryOp(Literal(2),
                                   "+",
                                   Literal(3)),
                          "*",
                          Literal(4)))


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

    assert parse(tokenize("if a then 2 else b + 4")) == \
        IfThenElse(Identifier("a"),
                   Literal(2),
                   BinaryOp(Identifier("b"),
                            "+",
                            Literal(4)))

    with pytest.raises(Exception):
        parse(tokenize("if 1 then 2 else"))
    with pytest.raises(Exception):
        parse(tokenize("if 1 else 2"))
    with pytest.raises(Exception):
        parse(tokenize("if 1"))
    with pytest.raises(Exception):
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


def test_unary_parsing() -> None:
    assert parse(tokenize("-a")) == UnaryOp("-", Identifier("a"))
    assert parse(tokenize("not b")) == UnaryOp("not", Identifier("b"))


def test_assignment_operator() -> None:
    # NOTE: these have to be right-associative!
    assert parse(tokenize("a = b")) == BinaryOp(
        Identifier("a"), "=", Identifier("b"))
    assert parse(tokenize("a = b = c")) == BinaryOp(Identifier("a"),
                                                    "=",
                                                    BinaryOp(Identifier("b"),
                                                             "=",
                                                             Identifier("c"))
                                                    )

    assert parse(tokenize("a = b = c + 2")) == \
        BinaryOp(Identifier("a"),
                 "=",
                 BinaryOp(Identifier("b"),
                          "=",
                          BinaryOp(Identifier("c"),
                                   "+",
                                   Literal(2))
                          )
                 )


def test_operator_precedence() -> None:
    assert parse(tokenize(r"a * b + c / d")) == BinaryOp(
        BinaryOp(Identifier('a'),
                 r"*",
                 Identifier('b')),
        r"+",
        BinaryOp(Identifier('c'),
                 "/",
                 Identifier('d')))

    assert parse(tokenize(r"a + b % c and d")) == BinaryOp(
        BinaryOp(Identifier('a'),
                 r"+",
                 BinaryOp(Identifier('b'),
                          r"%",
                          Identifier("c"))),
        "and",
        Identifier('d'))

    assert parse(tokenize(r"a % if b * c + b then d else e")) == BinaryOp(
        Identifier("a"),
        r"%",
        IfThenElse(BinaryOp(BinaryOp(Identifier("b"),
                                     "*",
                                     Identifier("c")),
                            "+",
                            Identifier("b")
                            ),
                   Identifier("d"),
                   Identifier("e"))
    )


def test_blocks() -> None:
    assert parse(tokenize("{ x = 10 }")) == Block(
        BinaryOp(Identifier("x"),
                 "=",
                 Literal(10)), result_expr=BinaryOp(Identifier("x"),
                                                    "=",
                                                    Literal(10)),
    )

    block2 = parse(tokenize("{ x = 10;"
                            "True }"))
    assert isinstance(block2, Block)
    assert block2 == \
        Block(BinaryOp(Identifier("x"),
                       "=",
                       Literal(10)),
              Identifier("True"), result_expr=Identifier("True")
              )

    assert parse(tokenize("{ a; }")) == Block(
        Identifier("a"), result_expr=Literal(None))

    assert parse(tokenize("x = { f(a); b }")) == \
        BinaryOp(Identifier("x"),
                 "=",
                 Block(Function("f",
                                Identifier("a")),
                       Identifier("b"),
                       result_expr=Identifier("b")
                       )
                 )

    assert parse(tokenize("{ { } }")) == Block(Block(result_expr=Literal(None)),
                                               result_expr=Block(result_expr=Literal(None)))

    with pytest.raises(Exception):
        parse(tokenize("{ 1 + 2"
                       "abc }"))
    with pytest.raises(Exception):
        parse(tokenize("{ 1 + 2 + { abc }; "))


def test_variable_declaration() -> None:
    # these should only work directly, in top-level and in blocks, not in e.g. "if True then var x = 1"
    assert parse(tokenize("var x = 1")) == Variable("x", Literal(1))
    assert parse(tokenize("var x = 3 * 4")) == Variable("x",
                                                        BinaryOp(Literal(3), "*", Literal(4)))
    assert parse(tokenize("var x = { var y = 1; y }")) == \
        Variable("x",
                 Block(Variable("y",
                                Literal(1)),
                       Identifier(
                     "y"),
                     result_expr=Identifier("y")))

    with pytest.raises(Exception):
        parse(tokenize("var x = var y"))
    with pytest.raises(Exception):
        parse(tokenize("if True then var x = 1 else var y = 2"))


def test_advanced_blocks() -> None:
    assert parse(tokenize("{ { a } }")) == \
        Block(Block(Identifier("a"),
                    result_expr=Identifier("a")),
              result_expr=Block(Identifier("a"),
                                result_expr=Identifier("a")))

    assert parse(tokenize("{ { a } { b } }")) == \
        Block(Block(Identifier("a"),
                    result_expr=Identifier("a")),
              Block(Identifier("b"),
                    result_expr=Identifier("b")),
              result_expr=Block(Identifier("b"),
                                result_expr=Identifier("b")))

    assert parse(tokenize("{ if true then { a } b }")) == \
        Block(IfThen(Identifier("true"),
                     Block(Identifier("a"),
              result_expr=Identifier("a"))),
              Identifier("b"),
              result_expr=Identifier("b"))

    assert parse(tokenize("{ if true then { a }; b }")) == \
        Block(IfThen(Identifier("true"),
                     Block(Identifier("a"),
              result_expr=Identifier("a"))),
              Identifier("b"),
              result_expr=Identifier("b"))

    with pytest.raises(Exception):
        parse(tokenize("{ a b }"))

    with pytest.raises(Exception):
        parse(tokenize("{ if true then { a } b c }"))

    assert parse(tokenize("{ if true then { a } b; c }")) == \
        Block(IfThen(Identifier("true"),
                     Block(Identifier("a"),
                           result_expr=Identifier("a"))),
              Identifier("b"),
              Identifier("c"),
              result_expr=Identifier("c"))

    assert parse(tokenize("{ if true then { a } else { b } c }")) == \
        Block(IfThenElse(Identifier("true"),
                         Block(Identifier("a"),
                               result_expr=Identifier("a")),
                         Block(Identifier("b"),
                               result_expr=Identifier("b"))),
              Identifier("c"),
              result_expr=Identifier("c"))

    assert parse(tokenize("x = { { f(a) } { b } }")) == \
        BinaryOp(Identifier("x"),
                 "=",
                 Block(Block(Function("f",
                                      Identifier("a")),
                       result_expr=Function("f",
                                            Identifier("a"))),
                       Block(Identifier("b"),
                             result_expr=Identifier("b")),
                       result_expr=Block(Identifier("b"),
                                         result_expr=Identifier("b"))),
                 )
