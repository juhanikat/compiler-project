from dataclasses import dataclass, field
from typing import Any, Tuple

from compiler.my_types import Type, Unit
from compiler.tokenizer import SourceLocation


@dataclass
class Expression:
    """Base class for AST nodes representing expressions."""
    type: Type | Unit = field(kw_only=True, default_factory=lambda: Unit())
    source_loc: SourceLocation | None = field(kw_only=True, default=None)

    def __eq__(self, value: Any) -> bool:
        if not isinstance(value, Expression):
            return False
        for self_field, other_field in zip(self.__dict__, value.__dict__):
            if getattr(self, self_field) != getattr(value, other_field):
                if (self_field == "source_loc" and other_field == "source_loc") or (self_field == "type" and other_field == "type"):
                    # NOTE: We do not compare the source_loc or type values to make testing easier, might cause problems later
                    continue
                else:
                    return False
        return True


@dataclass
class EmptyExpression(Expression):
    """Used when the input for parse() is empty."""


@dataclass
class Literal(Expression):
    value: int | bool | None

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)

    def __repr__(self) -> str:
        return f"Literal({self.value}) at loc {self.source_loc}"


@dataclass
class Identifier(Expression):
    name: str

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)

    def __repr__(self) -> str:
        return f"Identifier({self.name}) at loc {self.source_loc}"


@dataclass
class BinaryOp(Expression):
    """AST node for a binary operation like `A + B`"""
    left: Expression
    op: str
    right: Expression

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass
class UnaryOp(Expression):
    """AST node for an unary operation like `not A`"""
    op: str
    target: Expression

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass
class IfThen(Expression):
    """AST node for an if then conditional structure (without else)"""
    if_expr: Expression
    then_expr: Expression

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass
class IfThenElse(Expression):
    """AST node for an if then else conditional structure"""
    if_expr: Expression
    then_expr: Expression
    else_expr: Expression

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass
class WhileDo(Expression):
    condition: Expression
    do_expr: Expression

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(init=False)
class FunctionCall(Expression):
    """Identical to Function, except params have been renamed to args.
    Used for function calls as opposed to function definitions."""
    name: str
    args: Tuple[Expression, ...]

    def __init__(self, name: str, *args: Expression, source_loc: SourceLocation | None = None) -> None:
        super().__init__(source_loc=source_loc)
        self.name = name
        self.args = args

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(init=False)
class Block(Expression):
    expressions: Tuple[Expression, ...]
    returns_last: bool

    def __init__(self, *expressions: Expression, returns_last: bool = False, source_loc: SourceLocation | None = None) -> None:
        super().__init__(source_loc=source_loc)
        self.expressions = expressions
        self.returns_last = returns_last

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(init=False)
class Function(Expression):
    """Used for function definitions as opposed to function calls."""
    name: str
    params: Tuple[Identifier, ...]
    expr: Block

    def __init__(self, name: str, *params: Identifier, expr: Block, source_loc: SourceLocation | None = None) -> None:
        super().__init__(source_loc=source_loc)
        self.name = name
        self.params = params
        self.expr = expr

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(init=False)
class TopLevel(Expression):
    """This is identical to a Block, except it does not start and end with brackets {}, and it doesn't have the returns_last flag."""
    expressions: Tuple[Expression, ...]
    returns_last: bool

    def __init__(self, *expressions: Expression, returns_last: bool = False, source_loc: SourceLocation | None = None):
        super().__init__(source_loc=source_loc)
        self.expressions = expressions
        self.returns_last = returns_last

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass
class Variable(Expression):
    name: str
    value:  Expression

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)
