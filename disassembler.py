from .opcodes import Opcode as O
from .lexer import Lexer
from .parser import Parser
from .compiler import Compiler

JUMPS={O.POP_JUMP_IF_FALSE,O.POP_JUMP_IF_TRUE,O.JUMP_ABSOLUTE}
def disassemble(instructions):
    lines=["ADDR  OPCODE                 ARGUMENT / TARGET","----  ---------------------  --------------------"]
    for i,ins in enumerate(instructions):
        if ins.opcode in JUMPS: arg="to {:04d}".format(ins.arg)
        elif ins.opcode==O.CALL_BUILTIN:
            n,c=ins.arg; arg="{}() with {} arg(s)".format(n,c)
        else: arg=repr(ins.arg) if ins.arg is not None else ""
        lines.append("{:04d}  {:<21}  {}".format(i,ins.opcode.name,arg))
    return "\n".join(lines)
def disassemble_source(source_code,dialect="nova"):
    tree=Parser(Lexer(source_code,dialect).tokenize()).parse()
    return disassemble(Compiler().compile(tree))
