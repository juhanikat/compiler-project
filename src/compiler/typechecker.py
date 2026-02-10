from dataclasses import dataclass
from types import NoneType
from typing import Any, Dict, List, Self, Tuple, Type

from compiler import my_ast

type BasicType = Int | Bool | Unit
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
    type_args: Tuple[MyType, ...]
    return_type: MyType

    def __eq__(self, value: Any) -> bool:
        return self.__class__ == value.__class__

    def __init__(self, *type_args: MyType, return_type: MyType):
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
                "*": FunType(Int(), Int(), return_type=Int()),
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

    def add(self, name: str, value: MyType) -> None:
        if name in self.locals:
            raise Exception(f"Variable {name} was already in the type table")
        self.locals[name] = value
        return None

    def lookup(self, name: str) -> MyType | None:
        if name in self.locals:
            return self.locals.get(name)
        elif self.parent:
            return self.parent.lookup(name)
        return None


def typecheck(node: my_ast.Expression | None, type_table: TypeTable | None = None) -> MyType:
    if node is None:
        return Unit()
    if type_table is None:
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

        case my_ast.Identifier():
            value = type_table.lookup(node.name)
            if not value:
                raise Exception(
                    f"'{node.name}' does not exist in the type table")
            return value

        case my_ast.Function():
            value = type_table.lookup(node.name)
            if not isinstance(value, FunType):
                raise Exception(
                    f"TypeTable has function {node.name}, but its value is not a FunType!")
            return value.return_type

        case my_ast.Boolean():
            # TODO: should probably remove my_ast.Boolean entirely since Literal can already be bool?
            if isinstance(node.value, bool):
                return Bool()
            else:
                raise TypeError(
                    f"{node.value} is not a boolean")

        case my_ast.Variable():
            if isinstance(node.name, my_ast.Function):
                if not isinstance(node.value, my_ast.Block):
                    raise Exception(
                        "The value of a Function Variable was not a Block!")

                params: List[Int] = []
                for param in node.name.params:
                    # NOTE: All params are assumed to be Ints
                    if not isinstance(param, my_ast.Identifier):
                        raise Exception(
                            "Function has a parameter that is not an Identifier")

                    type_table.add(param.name, Int())
                    params.append(Int())

                value_type = typecheck(node.value, type_table)
                if not isinstance(value_type, FunType):
                    raise Exception("Function's value type was not a FunType")

                type_table.add(node.name.name, FunType(
                    *params, return_type=value_type.return_type))
            else:
                value_type = typecheck(node.value, type_table)
                type_table.add(node.name, value_type)
            return Unit()

        case my_ast.BinaryOp():
            left_type = typecheck(node.left, type_table)
            right_type = typecheck(node.right, type_table)

            if node.op == "==":
                if left_type != right_type:
                    raise TypeError()
            if node.op == "!=":
                if left_type != right_type:
                    raise TypeError()
            else:
                fun_type = type_table.lookup(node.op)

                if not isinstance(fun_type, FunType):
                    raise Exception(
                        f"'{node.op}' does not have a matching type in the TypeTable")
                if left_type.__class__ != fun_type.type_args[0].__class__:
                    raise TypeError(
                        f"Expected argument 1 to be {fun_type.type_args[0]}, but got {left_type}")
                if right_type.__class__ != fun_type.type_args[1].__class__:
                    raise TypeError(
                        f"Expected argument 2 to be {fun_type.type_args[1]}, but got {right_type}")
                return fun_type.return_type

        case my_ast.IfThenElse():
            t1 = typecheck(node.if_expr)
            if not isinstance(t1, Bool):
                raise Exception()
            t2 = typecheck(node.then_expr)
            t3 = typecheck(node.else_expr)
            if t2 != t3:
                raise Exception()
            return t2  # or t3, they are the same type

        case my_ast.WhileDo():
            return Unit()

        case my_ast.Block():
            block_type_table = TypeTable(locals=None, parent=type_table)
            block_exprs: List[MyType] = []
            for expr in node.expressions:
                t = typecheck(expr, block_type_table)
                block_exprs.append(t)

            if node.returns_last:
                return_type = block_exprs[-1]
                return FunType(*block_exprs, return_type=return_type)
            return FunType(*block_exprs, return_type=Unit())

        case my_ast.TopLevel():
            top_exprs: List[MyType] = []
            for expr in node.expressions:
                t = typecheck(expr, type_table)
                top_exprs.append(t)

            if node.returns_last:
                return top_exprs[-1]
            return Unit()

    raise Exception("No match")
