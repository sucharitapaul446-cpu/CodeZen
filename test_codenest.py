import unittest
from codenest import transpile

class TranspilerTests(unittest.TestCase):
    def test_keywords(self):
        self.assertIn("if x:", transpile("check x:\n    show(x)\n"))
    def test_strings_comments_substrings(self):
        src='checklist = "check"; # otherwise\ncheck yes:\n    show("show")\n'
        out=transpile(src)
        self.assertIn('checklist = "check"; # otherwise', out)
        self.assertIn("if True:", out)
    def test_function_and_range(self):
        src="create add(a, b):\n    give a + b\nforeach i within range(3):\n    show(i)\n"
        out=transpile(src, "nova")
        self.assertIn("def add", out)
        self.assertIn("for i in range", out)
    def test_python_dialect(self):
        self.assertIn("if True:", transpile("if True:\n    print(1)\n", "python"))
    def test_bad_dialect(self):
        with self.assertRaises(ValueError):
            transpile("x=1", "not-a-dialect")

if __name__ == "__main__":
    unittest.main()
