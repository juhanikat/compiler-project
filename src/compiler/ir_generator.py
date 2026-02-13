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
    reserved_names: set[str] | None,
    root_expr: my_ast.Expression
) -> list[my_ir.Instruction]:
    if reserved_names is None:
        reserved_names = set(DEFAULT_LOCALS.copy().keys())
    # 'var_unit' is used when an expression's type is 'Unit'.
    var_unit = my_ir.IRVar('unit')

    def new_var() -> my_ir.IRVar:
        for i in range(100):
            if f"v{i}" not in reserved_names:
                reserved_names.add(f"v{i}")
                return my_ir.IRVar(f"v{i}")
        raise Exception("Ran out of variables!")

    def new_label(loc: SourceLocation) -> my_ir.Label:
        for i in range(100):
            if f"L{i}" not in reserved_names:
                reserved_names.add(f"L{i}")
                return my_ir.Label(f"L{i}", loc=loc)
        raise Exception("Ran out of labels!")

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
                            expr.value, var, loc=loc))
                    case int():
                        var = new_var()
                        ins.append(my_ir.LoadIntConst(
                            expr.value, var, loc=loc))
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

            case my_ast.Variable():
                if isinstance(expr.name, my_ast.Function):
                    raise Exception("Not implemented!")
                value_ir = visit(sym_table, expr.value)
                sym_table.add(expr.name, value_ir)
                return var_unit

            case my_ast.UnaryOp():
                if not isinstance(expr.target, my_ast.Literal):
                    raise Exception(
                        "Target of an unary function was not a Literal")
                if expr.op == "-":
                    if not isinstance(expr.target.value, int):
                        raise Exception("Target of '-' was not an int")
                    var = new_var()
                    ins.append(my_ir.LoadIntConst(
                        -(expr.target.value), var, loc=loc))
                    return var
                elif expr.op == "not":
                    var = new_var()
                    ins.append(my_ir.LoadBoolConst(
                        not expr.target, var, loc=loc))
                    return var
                raise Exception("Expected either '-' or 'not")

            case my_ast.BinaryOp():
                if expr.op == "=":
                    if not isinstance(expr.left, my_ast.Identifier):
                        raise Exception(f"{expr.left} is not an identifier")

                    var_left = visit(sym_table, expr.left)
                    var_right = visit(sym_table, expr.right)
                    ins.append(my_ir.Copy(var_right, var_left, loc=loc))
                    return var_unit

                var_left = visit(sym_table, expr.left)
                # this might not work correctly
                if expr.op == "or" and isinstance(ins[-1], my_ir.LoadBoolConst) and ins[-1].value == True:
                    var = new_var()
                    ins.append(my_ir.LoadBoolConst(
                        True, var, loc=loc))
                    return var
                elif expr.op == "and" and isinstance(ins[-1], my_ir.LoadBoolConst) and ins[-1].value == False:
                    var = new_var()
                    ins.append(my_ir.LoadBoolConst(
                        False, var, loc=loc))
                    return var

                var_op = sym_table.lookup(expr.op)
                if not var_op:
                    raise Exception(f"{expr.op} not found in IR Table")

                var_right = visit(sym_table, expr.right)
                var_result = new_var()

                ins.append(my_ir.Call(
                    var_op, [var_left, var_right], var_result, loc=loc))
                return var_result

            case my_ast.IfThen():
                l_then = new_label(loc=loc)
                l_end = new_label(loc=loc)

                var_cond = visit(sym_table, expr.if_expr)

                ins.append(my_ir.CondJump(var_cond, l_then, l_end, loc=loc))

                ins.append(l_then)
                visit(sym_table, expr.then_expr)

                ins.append(l_end)
                return var_unit

            case my_ast.IfThenElse():
                l_then = new_label(loc=loc)
                l_else = new_label(loc=loc)
                l_end = new_label(loc=loc)

                var_cond = visit(sym_table, expr.if_expr)
                ins.append(my_ir.CondJump(var_cond, l_then, l_end, loc=loc))

                ins.append(l_then)
                visit(sym_table, expr.then_expr)
                ins.append(my_ir.Jump(l_end, loc=loc))

                ins.append(l_else)
                visit(sym_table, expr.then_expr)

                ins.append(l_end)
                return var_unit

            case my_ast.TopLevel():
                for child_expr in expr.expressions:
                    visit(sym_table, child_expr)
                return var_unit

            case my_ast.Block():
                block_sym_table = SymTable[my_ir.IRVar](locals={}, parent=None)
                for name in reserved_names:
                    block_sym_table.add(name, my_ir.IRVar(name))

                for child_expr in expr.expressions:
                    visit(block_sym_table, child_expr)
                return var_unit

            case _:
                print(expr)
                raise Exception("Didn't match any ast!")

    # We start with a SymTab that maps all available global names
    # like 'print_int' to IR variables of the same name.
    # In the Assembly generator stage, we will give
    # actual implementations for these globals. For now,
    # they just need to exist so the variable lookups work,
    # and clashing variable names can be avoided.

    root_sym_table = SymTable[my_ir.IRVar](locals={}, parent=None)
    for name in reserved_names:
        root_sym_table.add(name, my_ir.IRVar(name))

    # Start visiting the AST from the root.
    var_final_result = visit(root_sym_table, root_expr)

    # Add IR code to print the result, based on the type assigned earlier
    # by the type checker.
    if root_expr.type == Int:
        ins.append(my_ir.Call(my_ir.IRVar("print_int"),
                   [var_final_result], new_var()))
    elif root_expr.type == Bool:
        ins.append(my_ir.Call(my_ir.IRVar("print_bool"),
                   [var_final_result], new_var()))

    return ins


reserved_names = set(DEFAULT_LOCALS.copy().keys())
root_expr = parse(tokenize("1 + 2 * 3"))
