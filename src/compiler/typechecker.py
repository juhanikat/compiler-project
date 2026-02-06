from dataclasses import dataclass
from types import NoneType
from typing import Any, Dict, Self, Tuple, Type

from compiler import my_ast

type MyType = Int | Bool | Unit | FunType


class Int:

    def __eq__(self, value: Any) -> bool:
        return self.__class__ == value.__class__

    def __repr__(self) -> str:
        return "Int"


class Bool:

    def __eq__(self, value: Any) -> bool:
        return self.__class__ == value.__class__

    def __repr__(self) -> str:
        return "Bool"


class Unit:

    def __eq__(self, value: Any) -> bool:
        return self.__class__ == value.__class__

    def __repr__(self) -> str:
        return "Unit"


@dataclass(init=False)
class FunType:
    type_args: Tuple[Int | Bool | Unit, ...]
    return_type: Int | Bool | Unit

    def __eq__(self, value: Any) -> bool:
        return self.__class__ == value.__class__

    def __init__(self, *type_args: Int | Bool | Unit, return_type: Int | Bool | Unit):
        self.type_args = type_args
        self.return_type = return_type


@dataclass(init=False)
class TypeTable:
    """Like SymTable, but maps variable names to types"""
    locals: Dict[str, MyType]
    parent: Self | None

    def __init__(self, locals: Dict[str, MyType] | None = None, parent: Self | None = None) -> None:
        if locals:
            self.locals = locals
        else:
            self.locals = {
                "+": FunType(Int(), Int(), return_type=Int()),
                "unary_-": FunType(Int(), return_type=Int()),
                "/": FunType(Int(), Int(), return_type=Int()),
                "%": FunType(Int(), Int(), return_type=Int()),
                "<": FunType(Int(), Int(), return_type=Int()),
                "<=": FunType(Int(), Int(), return_type=Int()),
                ">": FunType(Int(), Int(), return_type=Int()),
                ">=": FunType(Int(), Int(), return_type=Int()),
                "or": FunType(Bool(), Bool(), return_type=Bool()),
                "and": FunType(Bool(), Bool(), return_type=Bool()),
                "unary_not": FunType(Bool(), return_type=Bool()),
                "while": Unit(),
                "print_int": FunType(Int(), return_type=Unit()),
                "print_bool": FunType(Bool(), return_type=Unit()),
                # TODO: read_int
            }
        if parent:
            self.parent = parent
        else:
            self.parent = None

    def lookup(self, name: str) -> MyType | None:
        if name in self.locals:
            return self.locals.get(name)
        elif self.parent:
            return self.parent.lookup(name)
        return None


def typecheck(node: my_ast.Expression | None) -> MyType:
    if node is None:
        return Unit()

    type_table = TypeTable()
    match node:
        case my_ast.Literal():
            if isinstance(node.value, bool) and not isinstance(node.value, int):
                return Bool()
            elif isinstance(node.value, int):
                return Int()
            elif isinstance(node.value, NoneType):
                return Unit()
            else:
                raise TypeError(
                    f"{node.value} is not an integer, a boolean or NoneType")

        case my_ast.BinaryOp():
            left_type = typecheck(node.left)
            right_type = typecheck(node.right)

            if node.op == "==":
                if left_type != right_type:
                    raise TypeError()
            if node.op == "!=":
                if left_type != right_type:
                    raise TypeError()
            else:
                fun_type = type_table.lookup(node.op)

                if not isinstance(fun_type, FunType):
                    raise Exception("Not a FunType")
                if left_type.__class__ != fun_type.type_args[0].__class__:
                    raise TypeError(
                        f"Expected argument 1 to be {fun_type.type_args[0]}, but got {left_type}")
                if right_type.__class__ != fun_type.type_args[1].__class__:
                    raise TypeError(
                        f"Expected argument 2 to be {fun_type.type_args[1]}, but got {right_type}")
                return fun_type.return_type

        case my_ast.IfThenElse():
            t1 = typecheck(node.if_expr)
            if t1 is not Bool:
                raise Exception()
            t2 = typecheck(node.then_expr)
            t3 = typecheck(node.else_expr)
            if t2 != t3:
                raise Exception()
            return t2
    raise Exception("No match")
