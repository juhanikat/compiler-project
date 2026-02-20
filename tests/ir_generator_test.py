from compiler.ir_generator import generate_ir
from compiler.my_ir import *


def test_basics() -> None:
    assert generate_ir(None, parse(tokenize("1 + 2"))) == \
        [LoadIntConst(1, IRVar("v0")),
         LoadIntConst(2, IRVar("v1")),
         Call(IRVar("+"), [IRVar("v0"), IRVar("v1")], IRVar("v2")),
         # NOTE: the result is always printed if it is an Int or a Bool
         Call(IRVar(name='print_int'), [IRVar(name='v2')], IRVar(name='v3'))]

    assert generate_ir(None, parse(tokenize("1 + 2 * 3"))) == \
        [LoadIntConst(1, IRVar("v0")),
         LoadIntConst(2, IRVar("v1")),
         LoadIntConst(3, IRVar("v2")),
         Call(IRVar("*"), [IRVar("v1"), IRVar("v2")], IRVar("v3")),
         Call(IRVar("+"), [IRVar("v0"), IRVar("v3")], IRVar("v4")),
         Call(IRVar(name='print_int'), [IRVar(name='v4')], IRVar(name='v5'))]

    assert generate_ir(None, parse(tokenize("var x = 1"))) == \
        [LoadIntConst(1, IRVar("v0"))]

    assert generate_ir(None, parse(tokenize("var x = 1; x = x + 2; x"))) == \
        [LoadIntConst(1, IRVar("v0")),
         LoadIntConst(2, IRVar("v1")),
         Call(IRVar("+"), [IRVar("v0"), IRVar("v1")], IRVar("v2")),
         Copy(IRVar("v2"), IRVar("v0")),
         Call(IRVar(name='print_int'), [IRVar(name='v0')], IRVar(name='v3'))]

    assert generate_ir(None, parse(tokenize("if true then 1"))) == \
        [LoadBoolConst(True, IRVar("v0")),
         CondJump(IRVar("v0"), Label("L0"), Label("L1")),
         Label("L0"),
         LoadIntConst(1, IRVar("v1")),
         Label("L1"),]
