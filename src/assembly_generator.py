import dataclasses

from compiler import my_ir


class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[my_ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[my_ir.IRVar]) -> None:
        ...  # Completed in task 1

    def get_ref(self, v: my_ir.IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used


def get_all_ir_variables(instructions: list[my_ir.Instruction]) -> list[my_ir.IRVar]:
    result_list: list[my_ir.IRVar] = []
    result_set: set[my_ir.IRVar] = set()

    def add(v: my_ir.IRVar) -> None:
        if v not in result_set:
            result_list.append(v)
            result_set.add(v)

    for insn in instructions:
        for field in dataclasses.fields(insn):
            value = getattr(insn, field.name)
            if isinstance(value, my_ir.IRVar):
                add(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, my_ir.IRVar):
                        add(v)
    return result_list
