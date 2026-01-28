from dataclasses import dataclass
from typing import Tuple


@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""


@dataclass
class Literal(Expression):
    value: int | bool | None


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class Punctuation(Expression):
    name: str


@dataclass
class Variable(Expression):
    name: str
    value:  Expression


@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression


@dataclass
class UnaryOp(Expression):
    """AST node for an unary operation like `not A`"""
    op: str
    target: Expression


@dataclass
class IfThen(Expression):
    """AST node for an if then conditional structure (without else)"""
    if_expr: Expression
    then_expr: Expression


@dataclass
class IfThenElse(Expression):
    """AST node for an if then else conditional structure"""
    if_expr: Expression
    then_expr: Expression
    else_expr: Expression


@dataclass(init=False)
class Function(Expression):
    name: str
    args: Tuple[Expression, ...]

    def __init__(self, name: str, *args: Expression) -> None:
        self.name = name
        self.args = args


@dataclass(init=False)
class Block(Expression):
    expressions: Tuple[Expression, ...]
    result_expr: Expression

    def __init__(self, *expressions: Expression, result_expr: Expression) -> None:
        self.expressions = expressions
        self.result_expr = result_expr
