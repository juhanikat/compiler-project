from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, Iterable, Self, Tuple, TypeVar

from compiler import my_ast
from compiler.my_ast import Expression

type Value = int | bool | None | Expression | Callable | Tuple[my_ast.Expression, ...]
T = TypeVar("T")

DEFAULT_LOCALS: Dict[str, Value] = {
    "+": lambda a, b:  a + b,
    "-": lambda a, b: a - b,
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
    "unary_not": lambda a: not a,
    "while": lambda a, b:  a / b,
    "print_int": lambda i: print(str(i) + "\n"),
    "print_bool": lambda b: print(str(b).lower() + "\n"),
    "read_int": lambda: int(input()),
    "print_int_params": tuple([my_ast.Identifier("i")]),
    "print_bool_params": tuple([my_ast.Identifier("b")]),
    "read_int_params": tuple([])
}


@dataclass(init=False)
class SymTable(Generic[T]):
    locals: Dict[str, T]
    parent: Self | None

    def __init__(self, locals: Dict[str, T], parent: Self | None = None) -> None:
        self.locals = locals
        if parent is None:
            self.parent = None
        else:
            self.parent = parent

    def add(self, name: str, value: T) -> None:
        if name in self.locals:
            raise Exception(f"Variable {name} was already in the symbol table")
        self.locals[name] = value
        return None

    def lookup(self, name: str) -> T | None:
        if name in self.locals:
            return self.locals.get(name)
        elif self.parent:
            return self.parent.lookup(name)
        return None

    def change(self, name: str, new_value: T) -> None:
        if not name in self.locals:
            if self.parent is None:
                raise Exception(f"{name} does not exist in the symbol table")
            self.parent.change(name, new_value)
        else:
            self.locals[name] = new_value


def interpret(node: my_ast.Expression | None, sym_table: SymTable | None = None) -> Value:
    if node is None:
        return None
    if sym_table is None:
        sym_table = SymTable[Value](locals=DEFAULT_LOCALS.copy(), parent=None)

    match node:
        case my_ast.Literal():
            return node.value

        case my_ast.Variable():
            # this works te same for both normal vars and functions
            sym_table.add(node.name, node.value)
            return None

        case my_ast.Identifier():
            value = sym_table.lookup(node.name)

            if value is None:
                exception_text = f"'{node.name}' is not defined"
                if node.name == "True":
                    exception_text = f"'{node.name}' is not defined, did you mean 'true'?"
                elif node.name == "False":
                    exception_text = f"'{node.name}' is not defined, did you mean 'false'?"
                raise Exception(exception_text)

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
            # evaluate short-circuiting operators before interpreting the right side
            if node.op == "or" and a == True:
                return True
            elif node.op == "and" and a == False:
                return False
            b: Any = interpret(node.right, sym_table)

            if node.op == "=":
                if not isinstance(node.left, my_ast.Identifier):
                    raise Exception(
                        f"{node.left} is not an identifier, so it cannot be assigned to (assigning to functions is not allowed)")
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
            if node.returns_last:
                return interpret(node.expressions[-1], sym_table)
            else:
                interpret(node.expressions[-1], sym_table)
                return None

        case my_ast.Block():
            if len(node.expressions) == 0:
                return None
            block_sym_table = SymTable[Value](
                locals=DEFAULT_LOCALS.copy(), parent=sym_table)
            for i in range(len(node.expressions) - 1):
                interpret(node.expressions[i], block_sym_table)
            if node.returns_last:
                return interpret(node.expressions[-1], block_sym_table)
            else:
                interpret(node.expressions[-1], block_sym_table)
                return None

        case my_ast.WhileDo():
            while interpret(node.condition, sym_table):
                interpret(node.do_expr, sym_table)
            return None

        case my_ast.FunctionCall():
            func = sym_table.lookup(node.name)
            if not func:
                raise Exception(f"Function {node.name} is not defined")

            given_args = node.args
            if not isinstance(given_args, Iterable):
                raise Exception(
                    f"The arguments given to '{node.name}' ({given_args}) is not an Iterable")

            # interpret the arguments given to the function
            interpreted_args = []
            for given_arg in given_args:
                interpreted_args.append(interpret(given_arg, sym_table))

            if node.name in ["print_int", "print_bool", "read_int"] and callable(func):
                return func(*interpreted_args)
            elif not isinstance(func, my_ast.Function):
                raise Exception(f"Function {node.name} was not a function?")

            # only go here if function was not built in
            if len(given_args) > len(func.params):
                raise Exception(
                    f"Too many arguments for function '{node.name}'")

            func_sym_table = SymTable[Value](
                locals={}, parent=sym_table)
            for func_param, interpreted_arg in zip(func.params, interpreted_args):
                if not isinstance(func_param, my_ast.Identifier):
                    raise Exception(
                        f"Parameter '{func_param}' set for function was not an identifier'")
                func_sym_table.add(
                    func_param.name, interpreted_arg)
            return interpret(func.expr, func_sym_table)

        case _:
            raise Exception(
                f"Interpreter is not implemented for node type {node}")
