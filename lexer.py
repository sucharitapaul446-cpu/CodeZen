import io
import keyword
import tokenize
from dataclasses import dataclass
from typing import Any
from dialects import get_dialect

@dataclass
class Token:
    type: str
    value: Any
    line: int

class Lexer:
    def __init__(self, source, dialect="nova"):
        self.source = source
        self.dialect = get_dialect(dialect)

    def tokenize(self):
        result = []
        try:
            stream = tokenize.tokenize(io.BytesIO(self.source.encode("utf-8")).readline)
            raw = []
            for t in stream:
                if t.type in (tokenize.ENCODING, tokenize.COMMENT, tokenize.ENDMARKER):
                    continue
                raw.append(t)
        except tokenize.TokenError as exc:
            raise SyntaxError(str(exc))
        # Collapse the two-name spelling "warna agar" into elif.
        i = 0
        while i < len(raw):
            t = raw[i]
            if (t.type == tokenize.NAME and t.string == "warna" and i + 1 < len(raw)
                    and raw[i+1].type == tokenize.NAME and raw[i+1].string == "agar"):
                result.append(Token("KEYWORD", "elif", t.start[0]))
                i += 2
                continue
            if t.type == tokenize.NL:
                if not result or result[-1].type != "NEWLINE":
                    result.append(Token("NEWLINE", "\n", t.start[0]))
            elif t.type == tokenize.NEWLINE:
                if not result or result[-1].type != "NEWLINE":
                    result.append(Token("NEWLINE", "\n", t.start[0]))
            elif t.type == tokenize.INDENT:
                result.append(Token("INDENT", t.string, t.start[0]))
            elif t.type == tokenize.DEDENT:
                result.append(Token("DEDENT", "", t.start[0]))
            elif t.type == tokenize.NUMBER:
                value = float(t.string) if any(c in t.string.lower() for c in ".e") else int(t.string, 0)
                result.append(Token("NUMBER", value, t.start[0]))
            elif t.type == tokenize.STRING:
                import ast
                try: value = ast.literal_eval(t.string)
                except Exception: value = t.string[1:-1]
                result.append(Token("STRING", value, t.start[0]))
            elif t.type == tokenize.NAME:
                canonical = self.dialect.get(t.string, t.string)
                if canonical in ("True", "False"):
                    result.append(Token("BOOL", canonical == "True", t.start[0]))
                elif canonical == "None":
                    result.append(Token("NONE", None, t.start[0]))
                elif canonical in ("if","elif","else","while","for","in","print"):
                    result.append(Token("KEYWORD", canonical, t.start[0]))
                else:
                    result.append(Token("NAME", canonical if t.string in self.dialect else t.string, t.start[0]))
            elif t.type == tokenize.OP:
                result.append(Token(t.string, t.string, t.start[0]))
            i += 1
        if not result or result[-1].type != "NEWLINE":
            result.append(Token("NEWLINE", "\n", max(1, len(self.source.splitlines()))))
        result.append(Token("EOF", None, max(1, len(self.source.splitlines()) + 1)))
        return result
