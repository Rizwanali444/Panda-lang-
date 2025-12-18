import sys, os, time, requests, psutil, json, base64
from datetime import datetime
from lark import Lark, Tree
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track

console = Console()
DEVELOPER = "Rizwan Ali"
VERSION = "3.2 (Level-3 Complete)"

# ==========================================
# 🧠 GRAMMAR (LEVEL 3)
# ==========================================
panda_grammar = r"""
start: (instruction | _comment)*

?instruction:
      ("show" | "dikhao") expr
    | IDENTIFIER "=" expr
    | IDENTIFIER "=" ("ask" | "pucho") STRING

    | "def" IDENTIFIER "(" [params] ")" ":" instruction+
    | IDENTIFIER "(" [args] ")"
    | "return" expr

    | ("if" | "agar") condition ":" instruction+
      [("else" | "warna") ":" instruction+]

    | ("for" | "dohrao") IDENTIFIER "in" expr ":" instruction+

    | expr

params: IDENTIFIER ("," IDENTIFIER)*
args: expr ("," expr)*

?condition:
      expr ">" expr
    | expr "<" expr
    | expr "==" expr

?expr:
      term
    | expr "+" term
    | expr "-" term

?term:
      factor
    | term "*" factor
    | term "/" factor

?factor:
      NUMBER
    | STRING
    | IDENTIFIER
    | list_expr
    | dict_expr
    | expr "[" expr "]"
    | expr "." IDENTIFIER "(" [args] ")"
    | IDENTIFIER "(" [args] ")"
    | "(" expr ")"

list_expr: "[" [args] "]"
dict_expr: "{" [dict_items] "}"
dict_items: STRING ":" expr ("," STRING ":" expr)*

_comment: COMMENT | MULTILINE_COMMENT
COMMENT: /#.*/
MULTILINE_COMMENT: /\"\"\"[\s\S]*?\"\"\"/

IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
STRING: /"[^"]*"/

%import common.NUMBER
%import common.WS
%ignore WS
%ignore COMMENT
%ignore MULTILINE_COMMENT
"""

# ==========================================
# ⚙️ INTERPRETER
# ==========================================
class PandaInterpreter:
    def __init__(self):
        self.globals = {"dev": DEVELOPER, "ver": VERSION}
        self.functions = {}
        self.scopes = [self.globals]
        self.return_value = None

    def scope(self):
        return self.scopes[-1]

    def run(self, tree):
        if isinstance(tree, Tree):
            return getattr(self, tree.data)(tree.children)
        return tree

    # -------- VARIABLES --------
    def IDENTIFIER(self, c):
        for s in reversed(self.scopes):
            if c[0] in s:
                return s[c[0]]
        return 0

    def assign_var(self, c):
        self.scope()[str(c[0])] = self.run(c[1])

    # -------- FUNCTIONS --------
    def def_func(self, c):
        name = str(c[0])
        params = [str(p) for p in c[1].children] if len(c)>2 and isinstance(c[1],Tree) else []
        body = c[2:] if params else c[1:]
        self.functions[name] = (params, body)

    def call_func(self, c):
        name = str(c[0])
        args = [self.run(a) for a in c[1:]]
        params, body = self.functions[name]
        local = dict(zip(params, args))
        self.scopes.append(local)
        self.return_value = None
        for stmt in body:
            self.run(stmt)
            if self.return_value is not None:
                break
        self.scopes.pop()
        rv = self.return_value
        self.return_value = None
        return rv

    def return_stmt(self, c):
        self.return_value = self.run(c[0])
        return self.return_value

    # -------- LIST / DICT --------
    def list_expr(self, c):
        return [self.run(x) for x in c]

    def dict_expr(self, c):
        d = {}
        for i in range(0, len(c), 2):
            d[str(c[i]).strip('"')] = self.run(c[i+1])
        return d

    def expr_index(self, c):
        return self.run(c[0])[int(self.run(c[1]))]

    def expr_method(self, c):
        obj = self.run(c[0])
        method = str(c[1])
        args = [self.run(a) for a in c[2:]]
        return getattr(obj, method)(*args)

    # -------- LOOP --------
    def for_loop(self, c):
        var = str(c[0])
        iterable = self.run(c[1])
        for x in iterable:
            self.scope()[var] = x
            for s in c[2:]:
                self.run(s)

    # -------- EXPRESSIONS --------
    def add(self, c):
        a,b = self.run(c[0]), self.run(c[1])
        return a+b

    def sub(self,c): return self.run(c[0])-self.run(c[1])
    def mul(self,c): return self.run(c[0])*self.run(c[1])
    def div(self,c): return self.run(c[0])/self.run(c[1])

    def number(self,c): return float(c[0])
    def string(self,c): return str(c[0]).strip('"')

    # -------- CONDITIONS --------
    def gt(self,c): return self.run(c[0])>self.run(c[1])
    def lt(self,c): return self.run(c[0])<self.run(c[1])
    def eq(self,c): return self.run(c[0])==self.run(c[1])

    # -------- IO --------
    def show(self,c):
        console.print(self.run(c[0]))

# ==========================================
# 🚀 RUNNER
# ==========================================
def start():
    parser = Lark(panda_grammar, parser="lalr")
    engine = PandaInterpreter()
    console.print(Panel(f"PANDA ENGINE 🐼\n{VERSION}\nBy {DEVELOPER}"))
    while True:
        try:
            cmd = console.input("panda ❯ ")
            if cmd in ("exit","niklo"): break
            engine.run(parser.parse(cmd))
        except Exception as e:
            console.print(f"[red]{e}[/red]")

if __name__ == "__main__":
    start()
