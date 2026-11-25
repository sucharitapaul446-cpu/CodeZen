import sys
from .opcodes import Opcode as O
from .lexer import Lexer
from .parser import Parser
from .compiler import Compiler

class MiniPVM:
    def __init__(self, stdout=None):
        self.stdout=stdout or sys.stdout
        self.operand_stack=[]; self.environment={}; self.ip=0; self.instructions=[]
    def run(self,instructions,environment=None):
        self.instructions=instructions; self.ip=0; self.operand_stack=[]
        if environment is not None: self.environment=environment
        while self.ip<len(self.instructions):
            ins=self.instructions[self.ip]; self.ip+=1; op=ins.opcode; arg=ins.arg
            if op==O.LOAD_CONST: self.operand_stack.append(arg)
            elif op==O.LOAD_NAME:
                if arg not in self.environment: raise NameError("name {!r} is not defined".format(arg))
                self.operand_stack.append(self.environment[arg])
            elif op==O.STORE_NAME: self.environment[arg]=self.operand_stack.pop()
            elif op in (O.BINARY_ADD,O.BINARY_SUB,O.BINARY_MUL,O.BINARY_DIV,O.BINARY_MOD):
                b=self.operand_stack.pop(); a=self.operand_stack.pop()
                if op==O.BINARY_ADD: v=a+b
                elif op==O.BINARY_SUB: v=a-b
                elif op==O.BINARY_MUL: v=a*b
                elif op==O.BINARY_MOD: v=a%b
                elif isinstance(a,int) and isinstance(b,int) and b!=0 and a%b==0: v=a//b
                else: v=a/b
                self.operand_stack.append(v)
            elif op==O.COMPARE_OP:
                b=self.operand_stack.pop(); a=self.operand_stack.pop()
                funcs={"==":lambda:a==b,"!=":lambda:a!=b,"<":lambda:a<b,"<=":lambda:a<=b,">":lambda:a>b,">=":lambda:a>=b}
                if arg not in funcs: raise ValueError("invalid comparison operator: "+str(arg))
                self.operand_stack.append(funcs[arg]())
            elif op==O.POP_JUMP_IF_FALSE:
                if not self.operand_stack.pop(): self.ip=arg
            elif op==O.POP_JUMP_IF_TRUE:
                if self.operand_stack.pop(): self.ip=arg
            elif op==O.JUMP_ABSOLUTE: self.ip=arg
            elif op==O.CALL_BUILTIN:
                name,count=arg; args=self.operand_stack[-count:] if count else []
                if count: del self.operand_stack[-count:]
                funcs={"str":str,"int":int,"float":float,"len":len,"abs":abs}
                if name not in funcs: raise NameError("unknown built-in {!r}".format(name))
                self.operand_stack.append(funcs[name](*args))
            elif op==O.PRINT_VALUE: print(self.operand_stack.pop(),file=self.stdout)
            elif op==O.HALT: break
            else: raise RuntimeError("unknown opcode: {!r}".format(op))
        return self.environment

def run_source(source_code,stdout=None,environment=None,dialect="nova"):
    from .disassembler import disassemble
    tokens=Lexer(source_code,dialect).tokenize()
    tree=Parser(tokens).parse()
    code=Compiler().compile(tree)
    return MiniPVM(stdout).run(code,environment)
