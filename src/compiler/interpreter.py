from dataclasses import dataclass
from typing import Any, Callable, Dict, Self

from compiler import my_ast
from compiler.my_ast import Expression

type Value = int | bool | None | Expression | Callable


@dataclass(init=False)
class SymTable:
    locals: Dict[str, Value]
    parent: Self | None = None

    def __init__(self) -> None:
        self.locals = {
            "+": lambda a, b:  a + b,
            "unary_-": lambda a: -a,
            "*": lambda a, b:  a * b,
            "/": lambda a, b:  a / b,
            "%": lambda a, b:  a % b,
            "<": lambda a, b:  a < b,
            "<=": lambda a, b:  a <= b,
            ">": lambda a, b:  a > b,
            ">=": lambda a, b:  a >= b,
            "==": lambda a, b:  a == b,
            "!=": lambda a, b:  a != b,
            "or": lambda a, b:  a or b,
            "and": lambda a, b:  a and b,
            "while": lambda a, b:  a / b,

        }

    def add(self, name: str, value: Value) -> None:
        if self.locals.get(name):
            raise Exception(f"Variable {name} was already in the symbol table")
        self.locals[name] = value
        return None

    def lookup(self, name: str) -> Value:
        if self.locals.get(name):
            return self.locals.get(name)
        elif self.parent:
            return self.parent.lookup(name)
        return None

    def change(self, name: str, new_value: Value) -> None:
        while not self.locals.get(name):
            if self.parent is None:
                raise Exception(f"{name} does not exist in the symbol table")
            self.parent.change(name, new_value)
        self.locals[name] = new_value


def interpret(node: my_ast.Expression | None, sym_table: SymTable | None = None) -> Value:
    if node is None:
        return None
    if sym_table is None:
        sym_table = SymTable()

    match node:
        case my_ast.Literal():
            return node.value
        case my_ast.Boolean():
            return node.value

        case my_ast.Variable():
            sym_table.add(node.name, node.value)
            return None

        case my_ast.Identifier():
            value = sym_table.lookup(node.name)
            if value is None:
                raise Exception(f"\'{node.name}' is not defined")
            if isinstance(value, my_ast.Expression):
                return interpret(value, sym_table)
            return value

        case my_ast.UnaryOp():
            target: Any = interpret(node.target, sym_table)
            unary_func = sym_table.lookup("unary_" + node.op)

            if not unary_func:
                raise Exception(f"Invalid operator '{node.op}' for UnaryOp")
            if not callable(unary_func):
                raise Exception(f"{node.op} is not callable")

            return unary_func(target)

        case my_ast.BinaryOp():
            a: Any = interpret(node.left, sym_table)
            b: Any = interpret(node.right, sym_table)

            if node.op == "=":
                if not isinstance(node.left, my_ast.Identifier):
                    raise Exception(
                        f"{node.left} is not an identifier, so it cannot be assigned to")
                sym_table.change(node.left.name, b)
                return None

            binary_func = sym_table.lookup(node.op)

            if not binary_func:
                raise Exception(f"Invalid operator '{node.op}' for BinaryOp")
            if not callable(binary_func):
                raise Exception(f"{node.op} is not callable")

            return binary_func(a, b)

        case my_ast.IfThen():
            if interpret(node.if_expr, sym_table):
                return interpret(node.then_expr, sym_table)
            return None

        case my_ast.IfThenElse():
            if interpret(node.if_expr, sym_table):
                return interpret(node.then_expr, sym_table)
            else:
                return interpret(node.else_expr, sym_table)

        case my_ast.TopLevel():
            for i in range(len(node.expressions) - 1):
                interpret(node.expressions[i], sym_table)
            return interpret(node.expressions[-1], sym_table)

        case my_ast.Block():
            for i in range(len(node.expressions) - 1):
                interpret(node.expressions[i], sym_table)
            return interpret(node.expressions[-1], sym_table)
        case _:
            raise Exception(
                f"Interpreter is not implemented for node type {node}")
