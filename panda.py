import sys
import os
import readline  # Python ki tarah Up-Arrow history ke liye
from lark import Lark, Tree
from rich.console import Console
from rich.panel import Panel

console = Console()

# ==========================================
# 🛡️ PANDA CORE SECURITY & INFO
# ==========================================
DEVELOPER = "Rizwan Ali"
VERSION = "0.3"

def verify_integrity():
    if DEVELOPER != "Rizwan Ali":
        console.print("[bold red]🛑 Engine Integrity Compromised![/bold red]")
        sys.exit()

def show_logo():
    # 🌈 Rainbow Colorful Cute Panda Logo
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
# 📝 PANDA GRAMMAR (MATH + VARIABLES + IF-ELSE)
# ==========================================
panda_grammar = r"""
    start: instruction+
    ?instruction: ("show" | "dikhao") expr             -> show_action
               | IDENTIFIER "=" expr                   -> assign_var
               | ("if" | "agar") condition ":" instruction+ [("else" | "warna") ":" instruction+] -> if_else
               | ("clear" | "saaf")                    -> clear_screen
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
    %ignore /#.*/
"""

# ==========================================
# ⚙️ INTERPRETER (LOGIC & MEMORY)
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
        for child in children:
            res = self.run(child)
        return res

    def show_action(self, children):
        val = self.run(children[0])
        console.print(f"[bold green]>>>[/bold green] [white]{val}[/white]")

    def direct_expr(self, children):
        val = self.run(children[0])
        if val is not None:
            console.print(f"[bold green]>>>[/bold green] [white]{val}[/white]")

    def assign_var(self, children):
        name = str(children[0])
        val = self.run(children[1])
        self.variables[name] = val
        return None

    def if_else(self, children):
        cond = self.run(children[0])
        if cond:
            # IF part execute karein
            for i in range(1, len(children)):
                if isinstance(children[i], Tree) and children[i].data != "warna":
                    self.run(children[i])
                else: break
        elif len(children) > 2:
             # ELSE part execute karein
             self.run(children[-1])

    # Comparisons
    def gt(self, c): return self.run(c[0]) > self.run(c[1])
    def lt(self, c): return self.run(c[0]) < self.run(c[1])
    def eq(self, c): return self.run(c[0]) == self.run(c[1])

    def clear_screen(self, _): os.system('clear')
    def add(self, a): return self.run(a[0]) + self.run(a[1])
    def sub(self, a): return self.run(a[0]) - self.run(a[1])
    def mul(self, a): return self.run(a[0]) * self.run(a[1])
    def div(self, a): return self.run(a[0]) / self.run(a[1])
    def number(self, a): return float(a[0])
    def string(self, a): return str(a[0]).strip('"')
    def get_var(self, a): return self.variables.get(str(a[0]), 0)

# ==========================================
# 🚀 CLI & REPL ENGINE (THE MAIN ENTRY)
# ==========================================
def start_repl():
    verify_integrity()
    show_logo()
    console.print("[bold cyan]Panda Interactive Shell v0.3[/bold cyan]")
    console.print("[dim white]Type 'niklo' to exit, 'saaf' to clear screen.[/dim white]\n")
    
    interpreter = PandaInterpreter()
    parser = Lark(panda_grammar, parser='lalr')

    while True:
        try:
            user_input = console.input("[bold pink]panda ❯ [/bold pink]")
            if user_input.lower() in ["exit", "niklo", "quit", "exit()"]:
                console.print("[bold yellow]🐼 Alvida, Rizwan![/bold yellow]")
                break
            if not user_input.strip(): continue
            
            tree = parser.parse(user_input)
            interpreter.run(tree)
        except Exception as e:
            console.print(f"[bold red]Ghalti:[/bold red] {e}")

if __name__ == "__main__":
    # Check for arguments correctly
    args = [a for a in sys.argv[1:] if a.strip()]
    
    if not args:
        start_repl()
    else:
        cmd = args[0]
        if cmd == "--version":
            console.print(Panel(f"PANDA 🐼 v{VERSION}\nDev: {DEVELOPER}", border_style="blue", expand=False))
        elif os.path.exists(cmd):
            p, i = Lark(panda_grammar, parser='lalr'), PandaInterpreter()
            with open(cmd, 'r') as f:
                try: i.run(p.parse(f.read()))
                except Exception as e: console.print(f"[bold red]Panda Error:[/bold red] {e}")
        else:
            start_repl()
