import pytest

from compiler.my_ast import (BinaryOp, Block, EmptyExpression, Function,
                             FunctionCall, Identifier, IfThen, IfThenElse,
                             Literal, TopLevel, UnaryOp, Variable, WhileDo)
from compiler.my_types import Bool, FunType, Int, Unit
from compiler.parser import parse
from compiler.tokenizer import tokenize


def test_parser_basics() -> None:
    assert parse(tokenize("1")) == Literal(1)
    assert parse(tokenize("1 + 2")) == BinaryOp(Literal(1), "+", Literal(2))
    assert parse(tokenize("1 + 2 * 3 / 4")) == BinaryOp(Literal(1),
                                                        "+",
                                                        BinaryOp(BinaryOp(Literal(2),
                                                                          "*",
                                                                          Literal(3)),
                                                                 "/",
                                                                 Literal(4)))
    assert parse(tokenize("a + b")) == BinaryOp(Identifier("a"),
                                                "+", Identifier("b"))
    assert parse(tokenize("hapsu + hapsu2")
                 ) == BinaryOp(Identifier("hapsu"), "+", Identifier("hapsu2"))
    assert parse(tokenize("true")) == Literal(True)


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
    assert parse(tokenize("")) == EmptyExpression()


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
    assert parse(tokenize("var f(a, b) = { 1 }")) == Variable("f", Function(
        "f", Identifier("a"), Identifier("b"), expr=Block(Literal(1), returns_last=True)))

    assert parse(tokenize("var g(a, b, c, d) = { a + b - c * d }")) == \
        Variable("g", Function("g",
                 Identifier("a"),
                 Identifier("b"),
                 Identifier("c"),
                 Identifier("d"),
                 expr=Block(
                     BinaryOp(BinaryOp(Identifier("a"),
                                       "+",
                                       Identifier("b")),
                              "-",
                              BinaryOp(Identifier("c"),
                                       "*",
                                       Identifier("d"))
                              ),
                     returns_last=True
                 )
                 )
                 )


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
                 Literal(10)),
        returns_last=True
    )

    assert parse(tokenize("{ x = 10;"
                          "True }")) == \
        Block(BinaryOp(Identifier("x"),
                       "=",
                       Literal(10)),
              Identifier("True"), returns_last=True)

    assert parse(tokenize("{ a; }")) == Block(
        Identifier("a"))

    assert parse(tokenize("x = { f(a); b }")) == \
        BinaryOp(Identifier("x"),
                 "=",
                 Block(FunctionCall("f",
                                    Identifier("a")),
                       Identifier("b"),
                       returns_last=True
                       )
                 )

    # NOTE: might need to change this returns_last behaviour
    assert parse(tokenize("{ { } }")) == Block(
        Block(), returns_last=True)

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
                       Identifier("y"),
                       returns_last=True))

    assert parse(tokenize("var x = 1; { x = 2; x }")) == \
        TopLevel(Variable("x",
                          Literal(1)),
                 Block(BinaryOp(Identifier("x"),
                                "=",
                                Literal(2)),
                       Identifier("x"),
                       returns_last=True), returns_last=True)

    with pytest.raises(Exception):
        parse(tokenize("var x = var y"))
    with pytest.raises(Exception):
        parse(tokenize("if True then var x = 1 else var y = 2"))


def test_advanced_blocks() -> None:
    assert parse(tokenize("{ { a } }")) == \
        Block(Block(Identifier("a"),
                    returns_last=True
                    ),
              returns_last=True
              )

    assert parse(tokenize("{ { a } { b } }")) == \
        Block(Block(Identifier("a"), returns_last=True),
              Block(Identifier("b"), returns_last=True),
              returns_last=True)

    assert parse(tokenize("{ if true then { a } b }")) == \
        Block(IfThen(Literal(True),
                     Block(Identifier("a"),
                           returns_last=True
                           )),
              Identifier("b"),
              returns_last=True)

    assert parse(tokenize("{ if true then { a }; b }")) == \
        Block(IfThen(Literal(True),
                     Block(Identifier("a"),
                           returns_last=True
                           )),
              Identifier("b"),
              returns_last=True
              )

    with pytest.raises(Exception):
        parse(tokenize("{ a b }"))

    with pytest.raises(Exception):
        parse(tokenize("{ if true then { a } b c }"))

    assert parse(tokenize("{ if true then { a } b; c }")) == \
        Block(IfThen(Literal(True),
                     Block(Identifier("a"),
                           returns_last=True
                           )),
              Identifier("b"),
              Identifier("c"),
              returns_last=True
              )

    assert parse(tokenize("{ if true then { a } else { b } c }")) == \
        Block(IfThenElse(Literal(True),
                         Block(Identifier("a"),
                               returns_last=True
                               ),
                         Block(Identifier("b"),
                               returns_last=True
                               )),
              Identifier("c"),
              returns_last=True
              )

    assert parse(tokenize("x = { { f(a) } { b } }")) == \
        BinaryOp(Identifier("x"),
                 "=",
                 Block(Block(FunctionCall("f",
                                          Identifier("a")),
                             returns_last=True
                             ),
                       Block(Identifier("b"),
                             returns_last=True
                             ),
                       returns_last=True
                       ),
                 )


def test_top_level_blocks() -> None:
    assert parse(tokenize("a = 1;")) == \
        TopLevel(BinaryOp(Identifier("a"), "=", Literal(1)))

    assert parse(tokenize("a = 1; b + 2")) == \
        TopLevel(BinaryOp(Identifier("a"),
                          "=",
                          Literal(1)),
                 BinaryOp(Identifier("b"),
                          "+",
                          Literal(2)), returns_last=True)

    assert parse(tokenize(" true; b = { x }")) == \
        TopLevel(Literal(True),
                 BinaryOp(Identifier("b"),
                          "=",
                          Block(Identifier("x"), returns_last=True)
                          ), returns_last=True)

    assert parse(tokenize("a = 1; b = { x = 2; x }; f(a);")) == \
        TopLevel(BinaryOp(Identifier("a"),
                          "=",
                          Literal(1)
                          ),
                 BinaryOp(Identifier("b"),
                          "=",
                          Block(BinaryOp(Identifier("x"),
                                         "=",
                                         Literal(2)),
                                Identifier("x"), returns_last=True
                                )
                          ),
                 FunctionCall("f",
                              Identifier("a"))
                 )


def test_while_do() -> None:
    assert parse(tokenize("while x do f(x)")) == \
        WhileDo(Identifier("x"), FunctionCall("f", Identifier("x")))


def test_typing() -> None:
    assert parse(tokenize("var x: Int = 1")) == Variable(
        "x", Literal(1), type=Int())
    assert parse(tokenize("var x: Bool = true")) == Variable(
        "x", Literal(True), type=Bool())
    assert parse(tokenize("var x: Bool = true; x")) == \
        TopLevel(Variable("x",
                          Literal(True),
                          type=Bool()),
                 Identifier("x"),
                 returns_last=True)

    assert parse(
        tokenize("var f(a, b): (Bool, Bool) => Bool = { a or b };")) == \
        TopLevel(Variable("f",
                 Function("f",
                          Identifier("a"),
                          Identifier("b"),
                          expr=Block(BinaryOp(Identifier("a"),
                                              "or",
                                              Identifier("b")),
                                     returns_last=True,
                                     ),

                          ),
                          type=FunType(Bool(),
                                       Bool(),
                                       return_type=Bool()))
                 )

    assert parse(
        tokenize("var f(a): (Bool) => Unit = { not a };")) == \
        TopLevel(Variable("f",
                          Function("f",
                                   Identifier("a"),
                                   expr=Block(UnaryOp("not",
                                                      Identifier("a")),
                                              returns_last=True),
                                   ),
                          type=FunType(Bool(), return_type=Unit()),
                          )
                 )

    # TODO: make this work!
    # parse(tokenize("{ var f: (Int) => Unit = print_int; f(123) }"))

    with pytest.raises(Exception):
        parse(tokenize("var x: ABC = true"))
    with pytest.raises(Exception):
        parse(tokenize("var x: bool = true"))

    parse(tokenize("var f(x): () => Int = { 2 * 2 }"))
    with pytest.raises(Exception):
        # no return type
        parse(tokenize("var f(x): (Int) = { x * 2 }"))
