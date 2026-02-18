from dataclasses import dataclass
from types import NoneType
from typing import Dict, List, Self

from compiler import my_ast
from compiler.my_types import Bool, FunType, Int, Type, Unit


@dataclass(init=False)
class TypeTable:
    """Like SymTable, but maps variable names to types"""
    locals: Dict[str, Type]
    parent: Self | None

    def __init__(self, locals: Dict[str, Type] | None = None, parent: Self | None = None) -> None:
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
                "read_int": FunType(return_type=Int())
            }
        if parent:
            self.parent = parent
        else:
            self.parent = None

    def add(self, name: str, value: Type) -> None:
        if name in self.locals:
            raise Exception(f"Variable {name} was already in the type table")
        self.locals[name] = value
        return None

    def lookup(self, name: str) -> Type | None:
        if name in self.locals:
            return self.locals.get(name)
        elif self.parent:
            return self.parent.lookup(name)
        return None


def typecheck(node: my_ast.Expression | None) -> Type:
    """Uses get_type() to get the type of the node, then sets node.type to that type and returns the type."""

    def get_type(node: my_ast.Expression, type_table: TypeTable) -> Type:
        match node:
            case my_ast.EmptyExpression():
                return Unit()

            case my_ast.Literal():
                if isinstance(node.value, bool):
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
                if not value:
                    raise Exception(
                        f"'{node.name}' does not exist in the type table")
                if not isinstance(value, FunType):
                    raise Exception(
                        f"TypeTable has function {node.name}, but its value is not a FunType!")
                return value.return_type

            case my_ast.Variable():
                if isinstance(node.value, my_ast.Function):
                    params: List[Type] = []
                    if not isinstance(node.type, FunType):
                        # TODO: if typing information is not given, assume every param is an Int, should probably fix
                        for param in node.value.params:
                            type_table.add(param.name, Int())
                            params.append(Int())
                    else:
                        for param, type_arg in zip(node.value.params, node.type.type_args):
                            type_table.add(param.name, type_arg)
                            params.append(type_arg)

                    block_expr_type = get_type(node.value.expr, type_table)
                    if not isinstance(block_expr_type, (Int | Bool | Unit)):
                        raise Exception(
                            "Function's value type was not a basic type")

                    type_table.add(node.name, FunType(
                        *params, return_type=block_expr_type))
                else:
                    value_type = get_type(node.value, type_table)
                    type_table.add(node.name, value_type)
                return Unit()

            case my_ast.BinaryOp():
                left_type = get_type(node.left, type_table)
                right_type = get_type(node.right, type_table)

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
                t1 = get_type(node.if_expr, type_table)
                if not isinstance(t1, Bool):
                    raise Exception()
                t2 = get_type(node.then_expr, type_table)
                t3 = get_type(node.else_expr, type_table)
                if t2 != t3:
                    raise Exception()
                return t2  # or t3, they are the same type

            case my_ast.WhileDo():
                return Unit()

            case my_ast.FunctionCall():
                value = type_table.lookup(node.name)
                if not isinstance(value, FunType):
                    raise Exception(
                        f"TypeTable has function {node.name}, but its value is not a FunType!")
                return value.return_type

            case my_ast.Block():
                block_type_table = TypeTable(locals=None, parent=type_table)
                block_exprs: List[Type] = []
                for expr in node.expressions:
                    t = get_type(expr, block_type_table)
                    block_exprs.append(t)

                if node.returns_last:
                    return_type = block_exprs[-1]
                    if not isinstance(return_type, (Int | Bool | Unit)):
                        raise Exception(
                            "Block return type was not a basic type")
                    return return_type
                return Unit()

            case my_ast.TopLevel():
                top_exprs: List[Type] = []
                for expr in node.expressions:
                    t = get_type(expr, type_table)
                    top_exprs.append(t)

                if node.returns_last:
                    return top_exprs[-1]
                return Unit()

        raise Exception("No match")

    if node is None:
        return Unit()
    node_type = get_type(node, TypeTable())
    node.type = node_type
    return node_type
