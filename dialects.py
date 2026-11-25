"""Keyword dictionaries for CodeNest's custom Python dialect."""
BASE = {
    "if":"if", "elif":"elif", "else":"else", "while":"while", "for":"for",
    "in":"in", "print":"print", "True":"True", "False":"False", "None":"None",
    "and":"and", "or":"or", "not":"not", "def":"def", "return":"return",
    "class":"class", "try":"try", "except":"except", "finally":"finally",
    "raise":"raise", "import":"import", "from":"from", "with":"with", "as":"as",
    "break":"break", "continue":"continue", "pass":"pass", "lambda":"lambda",
}
NOVA = {
    "check":"if", "elsecheck":"elif", "otherwise":"else", "repeat":"while",
    "foreach":"for", "within":"in", "show":"print", "yes":"True",
    "no":"False", "empty":"None", "both":"and", "either":"or",
    "invert":"not", "create":"def", "give":"return",
    "attempt":"try", "catch":"except", "finallydo":"finally",
    "stop":"break", "skip":"continue", "nothing":"pass",
}
DIALECTS = {"python": {**BASE}, "nova": {**BASE, **NOVA}}
MULTIWORD = {}
def get_dialect(name="nova"):
    try:
        return DIALECTS[name.lower()].copy()
    except (KeyError, AttributeError):
        raise ValueError("Unknown dialect {!r}. Available: {}".format(name, ", ".join(sorted(DIALECTS))))
