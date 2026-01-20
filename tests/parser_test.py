import pytest

from compiler.parser import parse
from compiler.tokenizer import tokenize


def test_parser_basics() -> None:
    # will fail if an error is raised
    parse(tokenize("1 + 2"))


def test_parentheses() -> None:
    parse(tokenize("(1 + 2) + 3 * 4"))
    parse(tokenize("1 + (2 + 3) * 4"))


def test_empty_input() -> None:
    assert parse(tokenize("")) is None


def test_garbage_at_end() -> None:
    with pytest.raises(Exception):
        parse(tokenize("1 + 2 xd"))
    with pytest.raises(Exception):
        parse(tokenize("1 + 2 +"))


def test_if_then_else() -> None:
    parse(tokenize("if 1 then 2"))
    parse(tokenize("if 1 then 2 else 3 + 4"))
    parse(tokenize("if 1 then if 2 then 3 else 4 else 5"))
    with pytest.raises(Exception):
        parse(tokenize("if 1 then 2 else"))
        parse(tokenize("if 1 else 2"))
        parse(tokenize("if 1"))
        parse(tokenize("if 1 then if 2 else 3"))
