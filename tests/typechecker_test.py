import pytest

from compiler.parser import parse
from compiler.tokenizer import tokenize
from compiler.typechecker import Bool, Int, Unit, typecheck


def test_binary_op() -> None:
    assert typecheck(parse(tokenize("1 + 2"))) == Int()
