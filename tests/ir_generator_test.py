from compiler.interpreter import DEFAULT_LOCALS
from compiler.ir_generator import generate_ir
from compiler.my_ir import *


def test_basics() -> None:
    assert generate_ir(None, parse(tokenize("1 + 2"))) == \
        [LoadIntConst(1, IRVar("v0")), LoadIntConst(2, IRVar("v1")), Call(
            IRVar("+"), [IRVar("v0"), IRVar("v1")], IRVar("v2"))]
