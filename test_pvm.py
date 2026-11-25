import io, unittest
from pvm import Lexer, Parser, Compiler, run_source, disassemble
from pvm.opcodes import Opcode as O
from pvm.parser import Program, AssignStmt

class PVMTests(unittest.TestCase):
    def execute(self, src):
        out = io.StringIO()
        env = run_source(src, stdout=out)
        return out.getvalue(), env
    def test_lexer(self):
        ts = Lexer('x = 12\nshow("hi")').tokenize()
        self.assertIn("NUMBER", [t.type for t in ts])
        self.assertIn("KEYWORD", [t.type for t in ts])
    def test_parser(self):
        tree = Parser(Lexer("x = 1\n").tokenize()).parse()
        self.assertIsInstance(tree, Program)
        self.assertIsInstance(tree.statements[0], AssignStmt)
    def test_arithmetic(self):
        out, _ = self.execute("x = 8 - 3 * 2\nshow(x)\n")
        self.assertEqual(out, "2\n")
    def test_while(self):
        out, _ = self.execute("i=1\nt=0\nrepeat i<=5:\n    t=t+i\n    i=i+1\nshow(t)\n")
        self.assertEqual(out, "15\n")
    def test_if_else(self):
        out, _ = self.execute('x=8\ncheck x<5:\n    show("a")\notherwise:\n    show("b")\n')
        self.assertEqual(out, "b\n")
    def test_for_loop(self):
        out, _ = self.execute("t=0\nforeach i within range(1,4):\n    t=t+i\nshow(t)\n")
        self.assertEqual(out, "6\n")
    def test_disassembler(self):
        text = disassemble(Compiler().compile(Parser(Lexer("x=1\n").tokenize()).parse()))
        self.assertIn("ADDR", text)
        self.assertIn("LOAD_CONST", text)

if __name__ == "__main__":
    unittest.main()
