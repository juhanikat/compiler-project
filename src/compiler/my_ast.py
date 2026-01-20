from dataclasses import dataclass
from typing import Any, Tuple


@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""


@dataclass
class Literal(Expression):
    value: int | bool


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression


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
    args: Tuple[Literal, ...]

    def __init__(self, *args: Literal) -> None:
        self.args = args
