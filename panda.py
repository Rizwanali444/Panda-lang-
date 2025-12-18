import sys
import os
import readline
from lark import Lark, Tree
from rich.console import Console
from rich.panel import Panel

console = Console()

DEVELOPER = "Rizwan Ali"
VERSION = "0.2"

def verify_integrity():
    if DEVELOPER != "Rizwan Ali":
        console.print("[bold red]🛑 SECURITY ALERT: Engine Integrity Compromised![/bold red]")
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

# --- Grammar and Interpreter remains same ---
panda_grammar = r"""
    start: instruction+
    ?instruction: ("show" | "dikhao") expr             -> show_action
               | IDENTIFIER "=" expr                   -> assign_var
               | ("clear" | "saaf")                    -> clear_screen
    ?expr: term | expr "+" term -> add | expr "-" term -> sub
    ?term: factor | term "*" factor -> mul | term "/" factor -> div
    ?factor: NUMBER -> number | IDENTIFIER -> get_var | STRING -> string | "(" expr ")"
    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    STRING: /"[^"]*"/
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

class PandaInterpreter:
    def __init__(self): self.variables = {} 
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
        console.print(f"[bold green]>>>[/bold green] [white]{val}[/white]")
    def assign_var(self, children):
        name = str(children[0]); val = self.run(children[1])
        self.variables[name] = val; return val
    def clear_screen(self, _): os.system('clear')
    def add(self, a): return self.run(a[0]) + self.run(a[1])
    def sub(self, a): return self.run(a[0]) - self.run(a[1])
    def mul(self, a): return self.run(a[0]) * self.run(a[1])
    def div(self, a): return self.run(a[0]) / self.run(a[1])
    def number(self, a): return float(a[0])
    def string(self, a): return str(a[0]).strip('"')
    def get_var(self, a): return self.variables.get(str(a[0]), 0)

def start_repl():
    show_logo()
    console.print("[bold cyan]Panda Shell Active[/bold cyan] [dim](niklo to exit)[/dim]\n")
    interpreter = PandaInterpreter()
    parser = Lark(panda_grammar, parser='lalr')
    while True:
        try:
            user_input = console.input("[bold pink]panda ❯ [/bold pink]")
            if user_input.lower() in ["exit", "niklo", "quit"]: break
            if not user_input.strip(): continue
            tree = parser.parse(user_input)
            interpreter.run(tree)
        except Exception as e:
            console.print(f"[bold red]Ghalti:[/bold red] {e}")

# ==========================================
# 🚀 FINAL CLI LOGIC (THE FIX)
# ==========================================
if __name__ == "__main__":
    verify_integrity()
    
    # Check if we have a real filename (not just an empty string or nothing)
    args = [a for a in sys.argv[1:] if a.strip()]
    
    if not args:
        # AGAR KUCH NAHI LIKHA TO SEEDHA REPL
        start_repl()
    else:
        cmd = args[0]
        if cmd == "--version":
            console.print(Panel(f"PANDA 🐼 v{VERSION}\nDev: {DEVELOPER}", border_style="blue"))
        elif os.path.exists(cmd):
            # FILE RUN KARO
            parser = Lark(panda_grammar, parser='lalr')
            interpreter = PandaInterpreter()
            with open(cmd, 'r') as f:
                try:
                    tree = parser.parse(f.read())
                    interpreter.run(tree)
                except Exception as e: console.print(f"[bold red]Error:[/bold red] {e}")
        else:
            # AGAR FILE NAME GHALAT HAI TAB BHI REPL START KAR DO TAKAY ERROR NA AYE
            console.print(f"[bold red]Ghalti:[/bold red] '{cmd}' nahi mili. REPL start kar raha hoon...")
            start_repl()
