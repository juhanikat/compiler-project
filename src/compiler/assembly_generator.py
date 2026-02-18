import dataclasses

from compiler import intrinsics, my_ir


class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[my_ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[my_ir.IRVar]) -> None:
        self._var_to_location = {}
        self._stack_used = 0
        offset = 0
        for var in variables:
            offset -= 8
            self._var_to_location[var] = f"{offset}(%rbp)"
        self._stack_used = abs(offset)

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


def generate_assembly(instructions: list[my_ir.Instruction]) -> str:
    lines = []

    def emit(line: str) -> None:
        lines.append(line)

    locals = Locals(
        variables=get_all_ir_variables(instructions)
    )
    # functions will not have more parameters than 6
    param_registers = ['%rdi', '%rsi', '%rdx', '%rcx', '%r8', '%r9']

    emit('.extern print_int')
    emit('.extern print_bool')
    emit('.extern read_int')
    emit('.global main')
    emit('.type main, @ function')

    emit('.section .text')

    emit('main:')
    emit('pushq %rbp')
    emit('movq %rsp, %rbp')
    emit(f'subq ${locals.stack_used()}, %rsp')

    for insn in instructions:
        emit('# ' + str(insn))
        match insn:
            case my_ir.Label():
                emit("")
                # ".L" prefix marks the symbol as "private".
                # This makes GDB backtraces look nicer too:
                # https://stackoverflow.com/a/26065570/965979
                emit(f'.L{insn.name}:')
            case my_ir.LoadIntConst():
                if -2**31 <= insn.value < 2**31:
                    emit(f'movq ${insn.value}, {locals.get_ref(insn.dest)}')
                else:
                    # Due to a quirk of x86-64, we must use
                    # a different instruction for large integers.
                    # It can only write to a register,
                    # not a memory location, so we use %rax
                    # as a temporary.
                    emit(f'movabsq ${insn.value}, %rax')
                    emit(f'movq %rax, {locals.get_ref(insn.dest)}')
            case my_ir.LoadBoolConst():
                if insn.value == True:
                    emit(f'movq ${1}, {locals.get_ref(insn.dest)}')
                else:
                    emit(f'movq ${0}, {locals.get_ref(insn.dest)}')
            case my_ir.Copy():
                emit(f'movq {locals.get_ref(insn.source)}, %rax')
                emit(f'movq %rax, {locals.get_ref(insn.dest)}')
            case my_ir.Jump():
                emit(f'jmp .L{insn.label.name}')
            case my_ir.CondJump():
                emit(f'cmpq $0, {locals.get_ref(insn.cond)}')
                emit(f'jne .L{insn.then_label.name}')
                emit(f'jmp .L{insn.else_label.name}')
            case my_ir.Call():
                if insn.fun.name in intrinsics.all_intrinsics:
                    refs = []
                    for arg in insn.args:
                        refs.append(locals.get_ref(arg))
                    args = intrinsics.IntrinsicArgs(refs,
                                                    r"%rax",
                                                    emit)
                    # call intrinsic function
                    intrinsics.all_intrinsics[insn.fun.name](args)
                else:
                    for param, register in zip(insn.args, param_registers):
                        emit(f'movq {locals.get_ref(param)}, {register}')
                    emit(f'callq {locals.get_ref(insn.fun)}')
                    emit(f'popq %rbp')
                    emit('ret')

    emit('movq $0, %rax')
    emit('movq %rbp, %rsp')
    emit('popq %rbp')
    emit('ret')
    return "\n".join(lines)
