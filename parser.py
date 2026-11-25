from dataclasses import dataclass, field
from typing import Any, List
from .lexer import Token

@dataclass
class ASTNode: pass
@dataclass
class ConstExpr(ASTNode): value: Any
@dataclass
class VarExpr(ASTNode): name: str
@dataclass
class UnaryOpExpr(ASTNode): op: str; operand: ASTNode
@dataclass
class BinOpExpr(ASTNode): left: ASTNode; op: str; right: ASTNode
@dataclass
class CallExpr(ASTNode): name: str; args: List[ASTNode]
@dataclass
class AssignStmt(ASTNode): name: str; value: ASTNode
@dataclass
class PrintStmt(ASTNode): value: ASTNode
@dataclass
class IfStmt(ASTNode):
    condition: ASTNode
    then_body: List[ASTNode]
    elif_blocks: List[Any] = field(default_factory=list)
    else_body: List[ASTNode] = field(default_factory=list)
@dataclass
class WhileStmt(ASTNode): condition: ASTNode; body: List[ASTNode]
@dataclass
class ForStmt(ASTNode): name: str; start: ASTNode; stop: ASTNode; body: List[ASTNode]
@dataclass
class Program(ASTNode): statements: List[ASTNode]

class Parser:
    def __init__(self, tokens): self.tokens=tokens; self.pos=0
    def cur(self): return self.tokens[min(self.pos, len(self.tokens)-1)]
    def take(self): t=self.cur(); self.pos+=1; return t
    def match(self, typ, val=None):
        if self.cur().type==typ and (val is None or self.cur().value==val): return self.take()
        return None
    def expect(self, typ, val=None):
        t=self.match(typ,val)
        if t is None: raise SyntaxError("Line {}: expected {}, got {!r}".format(self.cur().line, val or typ, self.cur().value))
        return t
    def parse(self):
        stmts=[]
        while self.cur().type!="EOF":
            if self.match("NEWLINE"): continue
            if self.cur().type=="DEDENT": self.take(); continue
            stmts.append(self.parse_statement())
        return Program(stmts)
    def parse_block(self):
        self.expect(":",)
        self.expect("NEWLINE")
        self.expect("INDENT")
        body=[]
        while self.cur().type not in ("DEDENT","EOF"):
            if self.match("NEWLINE"): continue
            body.append(self.parse_statement())
        self.expect("DEDENT")
        return body
    def parse_statement(self):
        t=self.cur()
        if t.type=="KEYWORD" and t.value=="if":
            self.take(); cond=self.parse_expression(); body=self.parse_block()
            elifs=[]; other=[]
            while self.cur().type=="KEYWORD" and self.cur().value=="elif":
                self.take(); c=self.parse_expression(); elifs.append((c,self.parse_block()))
            if self.cur().type=="KEYWORD" and self.cur().value=="else":
                self.take(); other=self.parse_block()
            return IfStmt(cond,body,elifs,other)
        if t.type=="KEYWORD" and t.value=="while":
            self.take(); c=self.parse_expression(); return WhileStmt(c,self.parse_block())
        if t.type=="KEYWORD" and t.value=="for":
            self.take(); name=self.expect("NAME").value; self.expect("KEYWORD","in")
            call=self.parse_expression()
            if not isinstance(call,CallExpr) or call.name!="range" or not (1<=len(call.args)<=2):
                raise SyntaxError("Line {}: PVM for-loops require range(stop) or range(start, stop)".format(t.line))
            start=ConstExpr(0) if len(call.args)==1 else call.args[0]
            stop=call.args[-1]
            return ForStmt(name,start,stop,self.parse_block())
        if t.type=="KEYWORD" and t.value=="print":
            self.take()
            if self.match("("):
                value=self.parse_expression(); self.expect(")")
            else: value=self.parse_expression()
            self.match("NEWLINE")
            return PrintStmt(value)
        if t.type=="NAME":
            name=self.take().value; self.expect("="); value=self.parse_expression(); self.match("NEWLINE")
            return AssignStmt(name,value)
        raise SyntaxError("Line {}: unexpected token {!r}".format(t.line,t.value))
    def parse_expression(self): return self.parse_comparison()
    def parse_comparison(self):
        node=self.parse_addition()
        while self.cur().type in ("==","!=","<","<=",">",">="):
            op=self.take().type; node=BinOpExpr(node,op,self.parse_addition())
        return node
    def parse_addition(self):
        node=self.parse_multiplication()
        while self.cur().type in ("+","-"):
            op=self.take().type; node=BinOpExpr(node,op,self.parse_multiplication())
        return node
    def parse_multiplication(self):
        node=self.parse_unary()
        while self.cur().type in ("*","/","%"):
            op=self.take().type; node=BinOpExpr(node,op,self.parse_unary())
        return node
    def parse_unary(self):
        if self.cur().type in ("-","+"):
            op=self.take().type; return UnaryOpExpr(op,self.parse_unary())
        return self.parse_primary()
    def parse_primary(self):
        t=self.cur()
        if t.type in ("NUMBER","STRING","BOOL","NONE"): self.take(); return ConstExpr(t.value)
        if t.type=="NAME":
            name=self.take().value
            if self.match("("):
                args=[]
                if not self.match(")"):
                    args.append(self.parse_expression())
                    while self.match(","): args.append(self.parse_expression())
                    self.expect(")")
                return CallExpr(name,args)
            return VarExpr(name)
        if self.match("("):
            node=self.parse_expression(); self.expect(")"); return node
        raise SyntaxError("Line {}: expected expression, got {!r}".format(t.line,t.value))
