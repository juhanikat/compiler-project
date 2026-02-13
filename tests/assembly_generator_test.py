from compiler.assembly_generator import generate_assembly
from compiler.ir_generator import generate_ir
from compiler.parser import parse
from compiler.tokenizer import tokenize


def test_basics() -> None:
    print(generate_assembly(generate_ir(reserved_names=None, root_expr=parse(
        tokenize("{var x = true; if x then 1 else 2; }")))))
