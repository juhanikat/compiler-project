import dataclasses
from dataclasses import dataclass
from typing import Any, Dict

from compiler import my_ast, my_ir
from compiler.interpreter import DEFAULT_LOCALS, SymTable, Value
from compiler.my_types import Bool, Int, Unit
from compiler.parser import parse
from compiler.tokenizer import SourceLocation, tokenize


def generate_ir(
    # 'reserved_names' should contain all global names
    # like 'print_int' and '+'. You can get them from
    # the global symbol table of your interpreter or type checker.
    reserved_names: set[str],
    root_expr: my_ast.Expression
) -> list[my_ir.Instruction]:
    # 'var_unit' is used when an expression's type is 'Unit'.
    var_unit = my_ir.IRVar('unit')

    def new_var() -> my_ir.IRVar:
        for i in range(100):
            if f"v{i}" not in reserved_names:
                reserved_names.add(f"v{i}")
                return my_ir.IRVar(f"v{i}")
        raise Exception("Ran out of variables!")

    # We collect the IR instructions that we generate
    # into this list.
    ins: list[my_ir.Instruction] = []

    # This function visits an AST node,
    # appends IR instructions to 'ins',
    # and returns the IR variable where
    # the emitted IR instructions put the result.
    #
    # It uses a symbol table to map local variables
    # (which may be shadowed) to unique IR variables.
    # The symbol table will be updated in the same way as
    # in the interpreter and type checker.
    def visit(sym_table: SymTable[my_ir.IRVar], expr: my_ast.Expression) -> my_ir.IRVar:
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
                        ins.append(my_ir.LoadBoolConst(
                            loc, expr.value, var))
                    case int():
                        var = new_var()
                        ins.append(my_ir.LoadIntConst(
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
                ins.append(my_ir.Call(
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

    root_symtab = SymTable[my_ir.IRVar](locals={}, parent=None)
    for name in reserved_names:
        root_symtab.add(name, my_ir.IRVar(name))

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
