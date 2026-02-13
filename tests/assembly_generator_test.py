from compiler.assembly_generator import generate_assembly
from compiler.ir_generator import generate_ir
from compiler.parser import parse
from compiler.tokenizer import tokenize


def test_basics() -> None:
    #generate_assembly(generate_ir(reserved_names=None, root_expr=parse(
    #    tokenize("{var x = true; if x then 1 else 2; }"))))
    #generate_assembly(generate_ir(reserved_names=None, root_expr=parse(
    #    tokenize("{ var x = 1 + 2; x = 1 }"))))

    #generate_assembly(generate_ir(reserved_names=None, root_expr=parse(
    #    tokenize("{ var x = -1 }"))))

    generate_assembly(generate_ir(reserved_names=None, root_expr=parse(
        tokenize("1 + 1; print_int(1)"))))
