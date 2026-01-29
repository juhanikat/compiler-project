from dataclasses import dataclass
from typing import Tuple

from compiler.tokenizer import SourceLocation


@dataclass(init=False)
class Expression:
    """Base class for AST nodes representing expressions."""
    source_loc: SourceLocation

    def __init__(self, *, source_loc: SourceLocation | None = None):
        self.source_loc = source_loc

    def __eq__(self, value) -> bool:
        if not isinstance(value, Expression):
            return False
        for self_field, other_field in zip(self.__dict__, value.__dict__):
            if getattr(self, self_field) != getattr(value, other_field):
                if self_field == "source_loc" and other_field == "source_loc":
                    # NOTE: We do not compare the source_loc values to make testing easier, might cause problems later
                    continue
                else:
                    return False
        return True


@dataclass(init=False)
class Literal(Expression):
    value: int | bool | None

    def __init__(self, value: int | bool | None, *, source_loc=None) -> None:
        super().__init__(source_loc=source_loc)
        self.value = value

    def __eq__(self, value):
        return super().__eq__(value)


@dataclass(init=False)
class Identifier(Expression):
    name: str

    def __init__(self, name, *, source_loc=None) -> None:
        super().__init__(source_loc=source_loc)
        self.name = name

    def __eq__(self, value):
        return super().__eq__(value)


@dataclass(init=False)
class Punctuation(Expression):
    name: str

    def __init__(self, value, *, source_loc=None):
        super().__init__(source_loc=source_loc)
        self.name = name

    def __eq__(self, value):
        return super().__eq__(value)


@dataclass(init=False)
class Variable(Expression):
    name: str
    value:  Expression

    def __init__(self, name, value, *, source_loc=None):
        super().__init__(source_loc=source_loc)
        self.name = name
        self.value = value

    def __eq__(self, value):
        return super().__eq__(value)


@dataclass(init=False)
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression

    def __init__(self, left, op, right, *, source_loc=None):
        super().__init__(source_loc=source_loc)
        self.left = left
        self.op = op
        self.right = right

    def __eq__(self, value):
        return super().__eq__(value)


@dataclass(init=False)
class UnaryOp(Expression):
    """AST node for an unary operation like `not A`"""
    op: str
    target: Expression

    def __init__(self, op, target, *, source_loc=None):
        super().__init__(source_loc=source_loc)
        self.op = op
        self.target = target

    def __eq__(self, value):
        return super().__eq__(value)


@dataclass(init=False)
class IfThen(Expression):
    """AST node for an if then conditional structure (without else)"""
    if_expr: Expression
    then_expr: Expression

    def __init__(self, if_expr, then_expr, *, source_loc=None):
        super().__init__(source_loc=source_loc)
        self.if_expr = if_expr
        self.then_expr = then_expr

    def __eq__(self, value):
        return super().__eq__(value)


@dataclass(init=False)
class IfThenElse(Expression):
    """AST node for an if then else conditional structure"""
    if_expr: Expression
    then_expr: Expression
    else_expr: Expression

    def __init__(self, if_expr, then_expr, else_expr, *, source_loc=None):
        super().__init__(source_loc=source_loc)
        self.if_expr = if_expr
        self.then_expr = then_expr
        self.else_expr = else_expr

    def __eq__(self, value):
        return super().__eq__(value)


@dataclass(init=False)
class Function(Expression):
    name: str
    args: Tuple[Expression, ...]

    def __init__(self, name: str, *args: Expression, source_loc: SourceLocation = None) -> None:
        super().__init__(source_loc=source_loc)
        self.name = name
        self.args = args

    def __eq__(self, value):
        return super().__eq__(value)


@dataclass(init=False)
class Block(Expression):
    expressions: Tuple[Expression, ...]
    result_expr: Expression

    def __init__(self, *expressions: Expression, result_expr: Expression, source_loc: SourceLocation = None) -> None:
        super().__init__(source_loc=source_loc)
        self.expressions = expressions
        self.result_expr = result_expr

    def __eq__(self, value):
        return super().__eq__(value)
