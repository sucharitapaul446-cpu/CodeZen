"""Token-safe transpiler, REPL and command-line interface."""
import argparse, io, os, sys, tokenize
from dialects import DIALECTS, get_dialect
from pvm import run_source, Lexer, Parser, Compiler, MiniPVM, disassemble

def transpile(source,dialect="nova"):
    mapping=get_dialect(dialect)
    lines=source.splitlines(True)
    edits=[]
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type==tokenize.NAME and tok.string in mapping and mapping[tok.string]!=tok.string:
                edits.append((tok.start[0]-1,tok.start[1],tok.end[1],mapping[tok.string]))
    except tokenize.TokenError as e:
        raise SyntaxError(str(e))
    for row,col,end,repl in sorted(edits,reverse=True):
        line=lines[row]
        lines[row]=line[:col]+repl+line[end:]
    return "".join(lines)

def parse_cli_args(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in ("run","dis","transpile","repl","-h","--help"):
        argv.insert(0,"run")
    p=argparse.ArgumentParser(prog="codenest",description="Run and transpile custom-keyword Python.")
    sub=p.add_subparsers(dest="command")
    r=sub.add_parser("run"); r.add_argument("file"); r.add_argument("--mode",choices=("pvm","transpile"),default="pvm"); r.add_argument("--dialect",default="nova")
    d=sub.add_parser("dis"); d.add_argument("file"); d.add_argument("--dialect",default="nova")
    t=sub.add_parser("transpile"); t.add_argument("file"); t.add_argument("-o","--output"); t.add_argument("--dialect",default="nova")
    q=sub.add_parser("repl"); q.add_argument("--mode",choices=("pvm","transpile"),default="pvm"); q.add_argument("--dialect",default="nova")
    return p.parse_args(argv)

def _read_block(first):
    lines=[first]
    if first.rstrip().endswith(":"):
        while True:
            try: line=input("... ")
            except EOFError: break
            if not line.strip(): break
            lines.append(line)
    return "\n".join(lines)

def repl(mode="pvm",dialect="nova"):
    env={}
    print("CodeNest REPL ({}, {} mode). Type exit to quit.".format(dialect,mode))
    while True:
        try: first=input(">>> ")
        except EOFError: break
        if first.strip() in ("exit","quit"): break
        if not first.strip(): continue
        source=_read_block(first)
        try:
            if mode=="pvm": run_source(source,environment=env,dialect=dialect)
            else:
                code=transpile(source,dialect)
                exec(compile(code,"<codenest-repl>","exec"),env,env)
        except Exception as exc: print("{}: {}".format(type(exc).__name__,exc))

def interactive_menu():
    while True:
        print("\nCodeNest")
        print("1. Run file\n2. Create and run file\n3. Launch REPL\n4. Disassemble file\n5. Exit")
        choice=input("Choose: ").strip()
        if choice=="5": return
        if choice=="3": repl(); continue
        if choice=="1" or choice=="4":
            path=input("File path: ").strip()
            try:
                src=open(path,encoding="utf-8").read()
                if choice=="4":
                    tree=Parser(Lexer(src).tokenize()).parse(); print(disassemble(Compiler().compile(tree)))
                else: run_source(src)
            except Exception as e: print("Error:",e)
        elif choice=="2":
            path=input("New .mypy file name: ").strip() or "hello.mypy"
            print("Enter source; finish with a line containing only END.")
            data=[]
            while True:
                line=input()
                if line=="END": break
                data.append(line)
            open(path,"w",encoding="utf-8").write("\n".join(data)+"\n")
            try: run_source("\n".join(data))
            except Exception as e: print("Error:",e)

def main(argv=None):
    args=parse_cli_args(argv)
    if not args.command: return interactive_menu()
    if args.command=="repl": return repl(args.mode,args.dialect)
    source=open(args.file,encoding="utf-8").read()
    if args.command=="run":
        if args.mode=="pvm": run_source(source,dialect=args.dialect)
        else:
            code=transpile(source,args.dialect); exec(compile(code,args.file,"exec"),{})
    elif args.command=="dis":
        tree=Parser(Lexer(source,args.dialect).tokenize()).parse()
        print(disassemble(Compiler().compile(tree)))
    elif args.command=="transpile":
        output=transpile(source,args.dialect)
        if args.output: open(args.output,"w",encoding="utf-8").write(output)
        else: print(output,end="")
    return 0

if __name__=="__main__": main()
