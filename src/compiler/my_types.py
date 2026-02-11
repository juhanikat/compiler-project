from dataclasses import dataclass
from typing import Any, Dict, List, Self, Tuple, Type

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

    def __init__(self, *type_args: MyType, return_type: MyType):
        self.type_args = type_args
        self.return_type = return_type
