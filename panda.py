import sys
import os
import readline
import time
import requests
from datetime import datetime
from lark import Lark, Tree
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track

console = Console()

# ==========================================
# 🛡️ PANDA CORE INFO & SECURITY
# ==========================================
DEVELOPER = "Rizwan Ali"
VERSION = "1.0 (Stable)"

def verify_integrity():
    if DEVELOPER != "Rizwan Ali":
        console.print("[bold red]🛑 Engine Integrity Compromised! Access Denied.[/bold red]")
        sys.exit()

def show_logo():
    logo = (
        "[bold magenta]      _      _      [/bold magenta]\n"
        "[bold cyan]    m( )mm( )m    [/bold cyan]\n"
        "[bold white]   (  [black]●[/black]  ..  [black]●[/black]  )   [/bold white] [bold cyan]PANDA 🐼 v" + VERSION + "[/bold cyan]\n"
        "[bold pink]    >   ♥   <     [/bold pink] [bold yellow]By Rizwan Ali[/bold yellow]\n"
        "[bold blue]   (    ~~    )    [/bold blue]\n"
        "[bold yellow]    (  v  v  )     [/bold yellow]\n"
        "[bold red]     \"\"    \"\"      [/bold red]"
    )
    console.print(Panel(logo, border_style="bold green", padding=(0, 2), expand=False))

# ==========================================
# 📝 PANDA MASTER GRAMMAR (v0.1 - v1.0)
# ==========================================
panda_grammar = r"""
    start: instruction+
    ?instruction: ("show" | "dikhao") expr             -> show_action
               | IDENTIFIER "=" expr                   -> assign_var
               | IDENTIFIER "=" ("pucho" | "ask") STRING -> ask_user
               | ("if" | "agar") condition ":" instruction+ [("else" | "warna") ":" instruction+] -> if_else
               | ("while" | "jab_tak") condition ":" instruction+ -> while_loop
               | ("table" | "naqsha") STRING "," STRING -> table_action
               | ("create" | "banao") STRING           -> file_create
               | ("write" | "likho") STRING "," STRING -> file_write
               | ("read" | "parho") STRING             -> file_read
               | ("run" | "chalao") STRING             -> sys_run
               | ("get" | "le_ao") STRING              -> http_get
               | ("time" | "waqt")                     -> show_time
               | ("clear" | "saaf")                    -> clear_screen
               | "load" NUMBER                         -> load_action
               | expr                                  -> direct_expr

    ?condition: expr ">" expr                          -> gt
               | expr "<" expr                         -> lt
               | expr "==" expr                        -> eq

    ?expr: term | expr "+" term -> add | expr "-" term -> sub
    ?term: factor | term "*" factor -> mul | term "/" factor -> div
    ?factor: NUMBER -> number | IDENTIFIER -> get_var | STRING -> string | "(" expr ")"

    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    STRING: /"[^"]*"/
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

# ==========================================
# ⚙️ INTERPRETER (LOGIC CENTER)
# ==========================================
class PandaInterpreter:
    def __init__(self):
        self.variables = {}

    def run(self, tree):
        if isinstance(tree, Tree):
            method = getattr(self, tree.data, self.generic_run)
            return method(tree.children)
        return tree

    def generic_run(self, children):
        res = None
        for child in children: res = self.run(child)
        return res

    def show_action(self, children):
        val = self.run(children[0])
        console.print(f"[bold green]>>>[/bold green] {val}")

    def direct_expr(self, children):
        val = self.run(children[0])
        if val is not None: console.print(f"[bold green]>>>[/bold green] {val}")

    def ask_user(self, children):
        var_name, prompt = str(children[0]), str(children[1]).strip('"')
        val = console.input(f"[bold yellow]{prompt}[/bold yellow] ")
        try: self.variables[var_name] = float(val)
        except: self.variables[var_name] = val

    def assign_var(self, children):
        name, val = str(children[0]), self.run(children[1])
        self.variables[name] = val

    def if_else(self, children):
        if self.run(children[0]):
            for i in range(1, len(children)):
                if isinstance(children[i], Tree) and children[i].data != "warna": self.run(children[i])
                else: break
        elif len(children) > 2: self.run(children[-1])

    def while_loop(self, children):
        cond, body = children[0], children[1:]
        while self.run(cond):
            for node in body: self.run(node)

    def http_get(self, children):
        url = str(children[0]).strip('"')
        console.print(f"[dim]Fetching from {url}...[/dim]")
        try:
            r = requests.get(url, timeout=5)
            console.print(Panel(r.text[:300] + "...", title="Web Content", border_style="green"))
        except: console.print("[bold red]Ghalti:[/bold red] Internet connection check karein.")

    def sys_run(self, children):
        os.system(str(children[0]).strip('"'))

    def show_time(self, _):
        console.print(f"[bold cyan]Waqt:[/bold cyan] {datetime.now().strftime('%H:%M:%S')}")

    def file_create(self, children):
        with open(str(children[0]).strip('"'), 'w') as f: f.write("")
    
    def file_write(self, children):
        with open(str(children[0]).strip('"'), 'a') as f: f.write(str(children[1]).strip('"') + "\n")

    def file_read(self, children):
        fn = str(children[0]).strip('"')
        if os.path.exists(fn):
            with open(fn, 'r') as f: console.print(Panel(f.read(), title=fn))
        else: console.print("[bold red]File nahi mili![/bold red]")

    def table_action(self, children):
        h, d = str(children[0]).strip('"').split(","), str(children[1]).strip('"').split(",")
        t = Table(header_style="bold magenta")
        for col in h: t.add_column(col.strip())
        t.add_row(*[val.strip() for val in d])
        console.print(t)

    def load_action(self, children):
        for _ in track(range(int(float(children[0]))), description="[cyan]Working..."): time.sleep(0.05)

    def gt(self, c): return self.run(c[0]) > self.run(c[1])
    def lt(self, c): return self.run(c[0]) < self.run(c[1])
    def eq(self, c): return self.run(c[0]) == self.run(c[1])
    def add(self, a):
        l, r = self.run(a[0]), self.run(a[1])
        if isinstance(l, str) or isinstance(r, str): return str(l) + str(r)
        return l + r
    def sub(self, a): return self.run(a[0]) - self.run(a[1])
    def mul(self, a): return self.run(a[0]) * self.run(a[1])
    def div(self, a): return self.run(a[0]) / self.run(a[1])
    def number(self, a): return float(a[0])
    def string(self, a): return str(a[0]).strip('"')
    def get_var(self, a): return self.variables.get(str(a[0]), 0)
    def clear_screen(self, _): os.system('clear')

# ==========================================
# 🚀 MAIN LAUNCHER
# ==========================================
def start_repl():
    verify_integrity(); show_logo()
    console.print("[bold cyan]Panda Master v1.0[/bold cyan] | Rizwan's Power Engine\n")
    i, p = PandaInterpreter(), Lark(panda_grammar, parser='lalr')
    while True:
        try:
            inp = console.input("[bold pink]panda ❯ [/bold pink]")
            if inp.lower() in ["exit", "niklo"]: break
            if not inp.strip(): continue
            i.run(p.parse(inp))
        except Exception as e: console.print(f"[bold red]Ghalti:[/bold red] {e}")

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a.strip()]
    if not args: start_repl()
    else:
        cmd = args[0]
        if os.path.exists(cmd):
            p, i = Lark(panda_grammar, parser='lalr'), PandaInterpreter()
            with open(cmd, 'r') as f: i.run(p.parse(f.read()))
        else: start_repl()
