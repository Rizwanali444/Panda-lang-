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
VERSION = "0.1"

def verify_integrity():
    if DEVELOPER != "Rizwan Ali":
        console.print("[bold red]🛑 SECURITY ALERT: Engine Integrity Compromised![/bold red]")
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

def show_branding_banner():
    verify_integrity()
    console.print(f"[bold yellow]( 🐼 )[/bold yellow] [bold cyan]PANDA ENGINE v{VERSION}[/bold cyan] | [bold white]By: {DEVELOPER}[/bold white]")
    console.print("[dim white]──────────────────────────────────────────────────[/dim white]")

# ==========================================
# 📝 PANDA GRAMMAR
# ==========================================
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
    %ignore /#.*/
"""

# ==========================================
# ⚙️ INTERPRETER WITH SESSION MEMORY
# ==========================================
class PandaInterpreter:
    def __init__(self):
        self.variables = {} # Yeh memory commands ke darmiyan variables yaad rakhti hai

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
        name = str(children[0])
        val = self.run(children[1])
        self.variables[name] = val
        return val

    def clear_screen(self, _):
        os.system('clear')

    def add(self, a): return self.run(a[0]) + self.run(a[1])
    def sub(self, a): return self.run(a[0]) - self.run(a[1])
    def mul(self, a): return self.run(a[0]) * self.run(a[1])
    def div(self, a): return self.run(a[0]) / self.run(a[1])
    def number(self, a): return float(a[0])
    def string(self, a): return str(a[0]).strip('"')
    def get_var(self, a): return self.variables.get(str(a[0]), 0)

# ==========================================
# 🚀 CLI & REPL ENGINE
# ==========================================
def start_repl():
    show_logo()
    console.print("[bold cyan]Panda Interactive Shell (REPL)[/bold cyan]")
    console.print("[dim white]Type 'niklo' to exit, 'saaf' to clear screen.[/dim white]\n")
    
    interpreter = PandaInterpreter()
    parser = Lark(panda_grammar, parser='lalr')

    while True:
        try:
            user_input = console.input("[bold pink]panda ❯ [/bold pink]")
            
            if user_input.lower() in ["exit", "niklo", "quit", "exit()"]:
                console.print("[bold yellow]🐼 Alvida, Rizwan! Panda Shell band ho raha hai.[/bold yellow]")
                break
                
            if not user_input.strip(): continue
            
            tree = parser.parse(user_input)
            interpreter.run(tree)
            
        except EOFError:
            break
        except Exception as e:
            console.print(f"[bold red]Ghalti:[/bold red] {e}")

if __name__ == "__main__":
    verify_integrity()
    
    # CASE 1: Sirf 'panda' (REPL Mode)
    if len(sys.argv) < 2:
        start_repl()
    
    else:
        arg = sys.argv[1]
        
        # CASE 2: Version Check
        if arg == "--version":
            version_box = f"[bold green]PANDA 🐼[/bold green]\n[white]Version: {VERSION}[/white]\n[bold yellow]Dev: {DEVELOPER}[/bold yellow]"
            console.print(Panel(version_box, border_style="blue", title="System Info", expand=False))
        
        # CASE 3: File Run
        elif os.path.exists(arg):
            show_branding_banner()
            parser = Lark(panda_grammar, parser='lalr')
            interpreter = PandaInterpreter()
            with open(arg, 'r') as f:
                try:
                    tree = parser.parse(f.read())
                    interpreter.run(tree)
                except Exception as e:
                    console.print(f"[bold red]Panda Error:[/bold red] {e}")
        
        # CASE 4: File Not Found
        else:
            show_logo()
            console.print(f"[bold red]Ghalti:[/bold red] File '{arg}' nahi mili!")
