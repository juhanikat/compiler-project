import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict

from compiler import my_ast
from compiler.interpreter import DEFAULT_LOCALS, SymTable, Value
from compiler.my_types import Bool, Int, Unit
from compiler.parser import parse
from compiler.tokenizer import SourceLocation, tokenize


@dataclass(frozen=True)
class IRVar:
    """Represents the name of a memory location or built-in."""
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Instruction():
    """Base class for IR instructions."""
    loc: SourceLocation | None = field(kw_only=True, default=None)

    def __str__(self) -> str:
        """Returns a string representation similar to
        our IR code examples, e.g. 'LoadIntConst(3, x1)'"""
        def format_value(v: Any) -> str:
            if isinstance(v, list):
                return f'[{", ".join(format_value(e) for e in v)}]'
            else:
                return str(v)
        args = ', '.join(
            format_value(getattr(self, field.name))
            for field in dataclasses.fields(self)
            if field.name != 'location'
        )
        return f'{type(self).__name__}({args})'

    def __eq__(self, value: Any) -> bool:
        if not isinstance(value, Instruction):
            return False
        for self_field, other_field in zip(self.__dict__, value.__dict__):
            if getattr(self, self_field) != getattr(value, other_field):
                if self_field == "loc" and other_field == "loc":
                    # NOTE: We do not compare the loc values to make testing easier, might cause problems later
                    continue
                else:
                    return False
        return True


@dataclass(frozen=True)
class Label(Instruction):
    """Marks the destination of a jump instruction."""
    name: str

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(frozen=True)
class LoadBoolConst(Instruction):
    """Loads a boolean constant value to `dest`."""
    value: bool
    dest: IRVar

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(frozen=True)
class LoadIntConst(Instruction):
    """Loads a constant value to `dest`."""
    value: int
    dest: IRVar

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(frozen=True)
class Copy(Instruction):
    """Copies a value from one variable to another."""
    source: IRVar
    dest: IRVar

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(frozen=True)
class Call(Instruction):
    """Calls a function or built-in."""
    fun: IRVar
    args: list[IRVar]
    dest: IRVar

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(frozen=True)
class Jump(Instruction):
    """Unconditionally continues execution from the given label."""
    label: Label

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)


@dataclass(frozen=True)
class CondJump(Instruction):
    """Continues execution from `then_label` if `cond` is true, otherwise from `else_label`."""
    cond: IRVar
    then_label: Label
    else_label: Label

    def __eq__(self, value: Any) -> bool:
        return super().__eq__(value)
