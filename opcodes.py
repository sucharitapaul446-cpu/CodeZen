from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional

class Opcode(Enum):
    LOAD_CONST = auto()
    LOAD_NAME = auto()
    STORE_NAME = auto()
    BINARY_ADD = auto()
    BINARY_SUB = auto()
    BINARY_MUL = auto()
    BINARY_DIV = auto()
    BINARY_MOD = auto()
    COMPARE_OP = auto()
    POP_JUMP_IF_FALSE = auto()
    POP_JUMP_IF_TRUE = auto()
    JUMP_ABSOLUTE = auto()
    CALL_BUILTIN = auto()
    PRINT_VALUE = auto()
    HALT = auto()

@dataclass
class Instruction:
    opcode: Opcode
    arg: Optional[Any] = None
    line_num: int = 1
