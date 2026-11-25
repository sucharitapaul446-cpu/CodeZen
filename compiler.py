from .opcodes import Opcode as O, Instruction as I
from .parser import *

BIN={"+":O.BINARY_ADD,"-":O.BINARY_SUB,"*":O.BINARY_MUL,"/":O.BINARY_DIV,"%":O.BINARY_MOD}
class Compiler:
    def __init__(self): self.code=[]
    def emit(self,op,arg=None,line=1): self.code.append(I(op,arg,line)); return len(self.code)-1
    def patch(self,idx,target): self.code[idx].arg=target
    def compile(self, tree):
        self.code=[]
        self.visit(tree)
        self.emit(O.HALT)
        return self.code
    def visit(self,node):
        method=getattr(self,"visit_"+type(node).__name__,None)
        if method is None: raise TypeError("Unsupported AST node: "+type(node).__name__)
        return method(node)
    def visit_Program(self,n):
        for s in n.statements: self.visit(s)
    def visit_ConstExpr(self,n): self.emit(O.LOAD_CONST,n.value)
    def visit_VarExpr(self,n): self.emit(O.LOAD_NAME,n.name)
    def visit_UnaryOpExpr(self,n):
        if n.op=="-": self.emit(O.LOAD_CONST,0); self.visit(n.operand); self.emit(O.BINARY_SUB)
        else: self.visit(n.operand)
    def visit_BinOpExpr(self,n):
        self.visit(n.left); self.visit(n.right)
        if n.op in BIN: self.emit(BIN[n.op])
        else: self.emit(O.COMPARE_OP,n.op)
    def visit_CallExpr(self,n):
        for a in n.args: self.visit(a)
        self.emit(O.CALL_BUILTIN,(n.name,len(n.args)))
    def visit_AssignStmt(self,n): self.visit(n.value); self.emit(O.STORE_NAME,n.name)
    def visit_PrintStmt(self,n): self.visit(n.value); self.emit(O.PRINT_VALUE)
    def visit_IfStmt(self,n):
        end_jumps=[]
        branches=[(n.condition,n.then_body)]+n.elif_blocks
        for cond,body in branches:
            self.visit(cond); jf=self.emit(O.POP_JUMP_IF_FALSE,-1)
            for s in body: self.visit(s)
            end_jumps.append(self.emit(O.JUMP_ABSOLUTE,-1))
            self.patch(jf,len(self.code))
        for s in n.else_body: self.visit(s)
        for j in end_jumps: self.patch(j,len(self.code))
    def visit_WhileStmt(self,n):
        start=len(self.code); self.visit(n.condition); out=self.emit(O.POP_JUMP_IF_FALSE,-1)
        for s in n.body: self.visit(s)
        self.emit(O.JUMP_ABSOLUTE,start); self.patch(out,len(self.code))
    def visit_ForStmt(self,n):
        it="__iter_"+n.name; stop="__stop_"+n.name
        self.visit(n.start); self.emit(O.STORE_NAME,it)
        self.visit(n.stop); self.emit(O.STORE_NAME,stop)
        start=len(self.code)
        self.emit(O.LOAD_NAME,it); self.emit(O.LOAD_NAME,stop); self.emit(O.COMPARE_OP,"<")
        out=self.emit(O.POP_JUMP_IF_FALSE,-1)
        self.emit(O.LOAD_NAME,it); self.emit(O.STORE_NAME,n.name)
        for s in n.body: self.visit(s)
        self.emit(O.LOAD_NAME,it); self.emit(O.LOAD_CONST,1); self.emit(O.BINARY_ADD); self.emit(O.STORE_NAME,it)
        self.emit(O.JUMP_ABSOLUTE,start); self.patch(out,len(self.code))
