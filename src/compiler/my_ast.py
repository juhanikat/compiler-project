from dataclasses import dataclass
from typing import Any, Tuple

from compiler.tokenizer import SourceLocation


@dataclass(init=False)
class Expression:
    """Base class for AST nodes representing expressions."""
    source_loc: SourceLocation | None

    def __init__(self, *, source_loc: SourceLocation | None = None):
        self.source_loc = source_loc

    def __eq__(self, value: Any) -> bool:
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

    def __init__(self, value: int | bool | None, *, source_loc: SourceLocation | None = None) -> None:
        super().__init__(source_loc=source_loc)
        self.value = value

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)

    def __repr__(self) -> str:
        return f"Literal({self.value}) at loc {self.source_loc}"


@dataclass(init=False)
class Identifier(Expression):
    name: str

    def __init__(self, name: str, *, source_loc: SourceLocation | None = None) -> None:
        super().__init__(source_loc=source_loc)
        self.name = name

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)

    def __repr__(self) -> str:
        return f"Identifier({self.name}) at loc {self.source_loc}"


@dataclass(init=False)
class Boolean(Expression):
    value: bool

    def __init__(self, value: bool, *, source_loc: SourceLocation | None = None) -> None:
        super().__init__(source_loc=source_loc)
        self.value = value

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)

    def __repr__(self) -> str:
        return f"Boolean({self.value}) at loc {self.source_loc}"


@dataclass(init=False)
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression

    def __init__(self, left: Expression, op: str, right: Expression, *, source_loc: SourceLocation | None = None):
        super().__init__(source_loc=source_loc)
        self.left = left
        self.op = op
        self.right = right

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(init=False)
class UnaryOp(Expression):
    """AST node for an unary operation like `not A`"""
    op: str
    target: Expression

    def __init__(self, op: str, target: Expression, *, source_loc: SourceLocation | None = None):
        super().__init__(source_loc=source_loc)
        self.op = op
        self.target = target

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(init=False)
class IfThen(Expression):
    """AST node for an if then conditional structure (without else)"""
    if_expr: Expression
    then_expr: Expression

    def __init__(self, if_expr: Expression, then_expr: Expression, *, source_loc: SourceLocation | None = None):
        super().__init__(source_loc=source_loc)
        self.if_expr = if_expr
        self.then_expr = then_expr

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(init=False)
class IfThenElse(Expression):
    """AST node for an if then else conditional structure"""
    if_expr: Expression
    then_expr: Expression
    else_expr: Expression

    def __init__(self, if_expr: Expression, then_expr: Expression, else_expr: Expression, *, source_loc: SourceLocation | None = None):
        super().__init__(source_loc=source_loc)
        self.if_expr = if_expr
        self.then_expr = then_expr
        self.else_expr = else_expr

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(init=False)
class WhileDo(Expression):
    condition: Expression
    do_expr: Expression

    def __init__(self, condition: Expression, do_expr: Expression, source_loc: SourceLocation | None = None) -> None:
        super().__init__(source_loc=source_loc)
        self.condition = condition
        self.do_expr = do_expr

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(init=False)
class Function(Expression):
    name: str
    params: Tuple[Expression, ...]

    def __init__(self, name: str, *params: Expression, source_loc: SourceLocation | None = None) -> None:
        super().__init__(source_loc=source_loc)
        self.name = name
        self.params = params

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(init=False)
class Block(Expression):
    expressions: Tuple[Expression, ...]
    # set to True if the last expression inside the block does not end with a semicolon
    returns_last: bool

    def __init__(self, *expressions: Expression, returns_last: bool = False, source_loc: SourceLocation | None = None) -> None:
        super().__init__(source_loc=source_loc)
        self.expressions = expressions
        self.returns_last = returns_last

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(init=False)
class TopLevel(Expression):
    """This is identical to a Block, except it does not start and end with brackets {}"""
    expressions: Tuple[Expression, ...]

    def __init__(self, *expressions: Expression, source_loc: SourceLocation | None = None) -> None:
        super().__init__(source_loc=source_loc)
        self.expressions = expressions

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(init=False)
class Variable(Expression):
    name: str | Function
    value:  Expression

    def __init__(self, name: str | Function, value: Expression, *, source_loc: SourceLocation | None = None):
        super().__init__(source_loc=source_loc)
        self.name = name
        self.value = value

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)
