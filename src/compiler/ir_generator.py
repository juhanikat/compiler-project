import dataclasses
from dataclasses import dataclass
from typing import Any, Dict

from compiler import my_ast
from compiler.interpreter import DEFAULT_LOCALS, SymTable, Value
from compiler.my_types import Bool, Int, Unit
from compiler.parser import parse
from compiler.tokenizer import SourceLocation, tokenize


@dataclass(frozen=True)
class IRVar:
    """Represents the name of a memory location or built-in."""
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Instruction():
    """Base class for IR instructions."""
    location: SourceLocation

    def __str__(self) -> str:
        """Returns a string representation similar to
        our IR code examples, e.g. 'LoadIntConst(3, x1)'"""
        def format_value(v: Any) -> str:
            if isinstance(v, list):
                return f'[{", ".join(format_value(e) for e in v)}]'
            else:
                return str(v)
        args = ', '.join(
            format_value(getattr(self, field.name))
            for field in dataclasses.fields(self)
            if field.name != 'location'
        )
        return f'{type(self).__name__}({args})'


@dataclass(frozen=True)
class Label(Instruction):
    """Marks the destination of a jump instruction."""
    name: str


@dataclass(frozen=True)
class LoadBoolConst(Instruction):
    """Loads a boolean constant value to `dest`."""
    value: bool
    dest: IRVar


@dataclass(frozen=True)
class LoadIntConst(Instruction):
    """Loads a constant value to `dest`."""
    value: int
    dest: IRVar


@dataclass(frozen=True)
class Copy(Instruction):
    """Copies a value from one variable to another."""
    source: IRVar
    dest: IRVar


@dataclass(frozen=True)
class Call(Instruction):
    """Calls a function or built-in."""
    fun: IRVar
    args: list[IRVar]
    dest: IRVar


@dataclass(frozen=True)
class Jump(Instruction):
    """Unconditionally continues execution from the given label."""
    label: Label


@dataclass(frozen=True)
class CondJump(Instruction):
    """Continues execution from `then_label` if `cond` is true, otherwise from `else_label`."""
    cond: IRVar
    then_label: Label
    else_label: Label


def generate_ir(
    # 'reserved_names' should contain all global names
    # like 'print_int' and '+'. You can get them from
    # the global symbol table of your interpreter or type checker.
    reserved_names: set[str],
    root_expr: my_ast.Expression
) -> list[Instruction]:
    # 'var_unit' is used when an expression's type is 'Unit'.
    var_unit = IRVar('unit')

    def new_var() -> IRVar:
        for i in range(100):
            if f"v{i}" not in reserved_names:
                reserved_names.add(f"v{i}")
                return IRVar(f"v{i}")
        raise Exception("Ran out of variables!")

    # We collect the IR instructions that we generate
    # into this list.
    ins: list[Instruction] = []

    # This function visits an AST node,
    # appends IR instructions to 'ins',
    # and returns the IR variable where
    # the emitted IR instructions put the result.
    #
    # It uses a symbol table to map local variables
    # (which may be shadowed) to unique IR variables.
    # The symbol table will be updated in the same way as
    # in the interpreter and type checker.
    def visit(sym_table: SymTable[IRVar], expr: my_ast.Expression) -> IRVar:
        loc = expr.source_loc
        if not loc:
            raise Exception("Missing SourceLocation")

        match expr:
            case my_ast.Literal():
                # Create an IR variable to hold the value,
                # and emit the correct instruction to
                # load the constant value.
                match expr.value:
                    case bool():
                        var = new_var()
                        ins.append(LoadBoolConst(
                            loc, expr.value, var))
                    case int():
                        var = new_var()
                        ins.append(LoadIntConst(
                            loc, expr.value, var))
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(
                            f"{loc}: unsupported literal: {type(expr.value)}")

                # Return the variable that holds
                # the loaded value.
                return var

            case my_ast.Identifier():
                # Look up the IR variable that corresponds to
                # the source code variable.
                ir_var = sym_table.lookup(expr.name)
                if not ir_var:
                    raise Exception(f"{expr.name} not found in IR Table")
                return ir_var

            case my_ast.BinaryOp():
                # Ask the symbol table to return the variable that refers
                # to the operator to call.
                var_op = sym_table.lookup(expr.op)
                if not var_op:
                    raise Exception(f"{expr.op} not found in IR Table")
                # Recursively emit instructions to calculate the operands.
                var_left = visit(sym_table, expr.left)
                var_right = visit(sym_table, expr.right)
                # Generate variable to hold the result.
                var_result = new_var()
                # Emit a Call instruction that writes to that variable.
                ins.append(Call(
                    loc, var_op, [var_left, var_right], var_result))
                return var_result

            case _:
                raise Exception("Not implemented!")

    # We start with a SymTab that maps all available global names
    # like 'print_int' to IR variables of the same name.
    # In the Assembly generator stage, we will give
    # actual implementations for these globals. For now,
    # they just need to exist so the variable lookups work,
    # and clashing variable names can be avoided.

    root_symtab = SymTable[IRVar](locals={}, parent=None)
    for name in reserved_names:
        root_symtab.add(name, IRVar(name))

    # Start visiting the AST from the root.
    var_final_result = visit(root_symtab, root_expr)

    # Add IR code to print the result, based on the type assigned earlier
    # by the type checker.
    if root_expr.type == Int:
        ...  # Emit a call to 'print_int'
    elif root_expr.type == Bool:
        ...  # Emit a call to 'print_bool'

    return ins


reserved_names = set(DEFAULT_LOCALS.copy().keys())
root_expr = parse(tokenize("1 + 2 * 3"))
if root_expr is None:
    raise Exception
print(generate_ir(reserved_names, root_expr))
