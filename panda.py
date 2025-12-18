import sys
import random
import time
import os
import requests
import base64
import threading
import socket
import hashlib
from lark import Lark, Tree
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Console initialization
console = Console()

# ==========================================
# 🛡️ PANDA CORE SECURITY (RIZWAN'S LOCK)
# ==========================================
DEVELOPER = "Rizwan Ali"
VERSION = "0.1"
COPYRIGHT = f"© 2024-2025 {DEVELOPER}. All Rights Reserved."
# MD5 Hash of "Rizwan Ali" to prevent name tampering
SIG_HASH = "8e95c1d6368c4d289053c7c25c345b5c"

def verify_integrity():
    """Checks if someone tried to change the developer name"""
    check = hashlib.md5(DEVELOPER.encode()).hexdigest()
    if check != SIG_HASH:
        console.print("[bold red]🛑 SECURITY ALERT: Engine Integrity Compromised![/bold red]")
        console.print("[red]Modification of Developer Name or Copyright is strictly prohibited.[/red]")
        sys.exit()

def show_branding_banner():
    """Colorful Branding that shows every time a script runs"""
    verify_integrity()
    banner_text = f"[bold cyan]🐼 PANDA ENGINE v{VERSION}[/bold cyan]\n[bold yellow]Developed by: {DEVELOPER}[/bold yellow]\n[dim white]{COPYRIGHT}[/dim white]"
    console.print(Panel(banner_text, border_style="magenta", expand=False))

def show_logo():
    """Large Logo for Help Screen"""
    logo = r"""
    [bold green]  .--.      .--.   [/bold green][bold white]PANDA 🐼[/bold white]
    [bold green] / _  \    /  _ \  [/bold green][bold yellow]By Rizwan Ali[/bold yellow]
    [bold green]| ( \  \__/  / ) | [/bold green]
    [bold green] \  \ [bold white](  o)  (o  )[/bold white]  / /  [/bold green]
    [bold green]  \  \    [bold pink]__[/bold pink]    / /   [/bold green]
    [bold green]   \  \  [bold red](__)[/bold red]  / /    [/bold green]
    """
    console.print(logo)

# ==========================================
# PANDA 🐼 GRAMMAR v0.1
# ==========================================
panda_grammar = r"""
    start: instruction+
    ?instruction: ("show" | "dikhao") expr             -> show_action
               | ("table" | "naqsha") expr "|" expr    -> table_action
               | IDENTIFIER = ("ask" | "pucho") VAL    -> ask_user
               | IDENTIFIER = expr                     -> assign_var
               | ("if" | "agar") condition ":" instruction+ [("else" | "warna") ":" instruction+] -> if_else
               | ("while" | "jab_tak") condition ":" instruction+ -> while_loop
               | "system" expr                         -> system_cmd
               | "file_likho" expr "," expr            -> file_write
               | "api_fetch" IDENTIFIER expr           -> api_fetch
               | "port_scan" IDENTIFIER expr "," expr  -> port_scan
               | "secret_lock" IDENTIFIER expr         -> encode_data
               | "wait" expr                           -> wait_action
               | "thread" IDENTIFIER                   -> start_thread
    ?condition: expr ">" expr  -> gt | expr "<" expr -> lt | expr "==" expr -> eq
    ?expr: term | expr "+" term -> add | expr "-" term -> sub | "file_parho" expr -> file_read
    ?term: factor | term "*" factor -> mul | term "/" factor -> div
    ?factor: NUMBER -> number | IDENTIFIER -> get_var | STRING -> string | "(" expr ")"
    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    STRING: /"[^"]*"/
    VAL: /"[^"]*"/ | NUMBER
    %import common.NUMBER
    %import common.WS
    %ignore WS
    %ignore /#.*/
"""

# ==========================================
# PANDA INTERPRETER
# ==========================================
class PandaInterpreter:
    def __init__(self):
        self.memory = {}

    def run(self, tree):
        if isinstance(tree, Tree):
            method = getattr(self, tree.data, self.generic_run)
            return method(tree.children)
        return tree

    def generic_run(self, children):
        for child in children: self.run(child)

    def show_action(self, children): console.print(self.run(children[0]))

    def table_action(self, children):
        headers = str(self.run(children[0])).split(",")
        rows = str(self.run(children[1])).split(",")
        t = Table(show_header=True, header_style="bold magenta", border_style="blue")
        for h in headers: t.add_column(h.strip())
        t.add_row(*[r.strip() for r in rows])
        console.print(t)

    def ask_user(self, children):
        var_name, prompt = str(children[0]), str(children[1]).strip('"')
        res = console.input(f"[bold yellow]{prompt}[/bold yellow] ")
        self.memory[var_name] = float(res) if res.replace('.','',1).isdigit() else res

    def assign_var(self, children): self.memory[str(children[0])] = self.run(children[1])
    def if_else(self, children):
        if self.run(children[0]): self.run(children[1])
        elif len(children) > 2: self.run(children[2])
    def while_loop(self, children):
        while self.run(children[0]):
            for i in range(1, len(children)): self.run(children[i])
    def system_cmd(self, children): os.system(str(self.run(children[0])))
    def file_write(self, children):
        fname, content = str(self.run(children[0])), str(self.run(children[1]))
        with open(fname, "w") as f: f.write(content)
    def file_read(self, children):
        fname = str(self.run(children[0]))
        if os.path.exists(fname):
            with open(fname, "r") as f: return f.read()
        return "[red]Error: File nahi mili![/red]"
    def api_fetch(self, children):
        var_name, url = str(children[0]), str(self.run(children[1]))
        try:
            res = requests.get(url, timeout=5)
            self.memory[var_name] = res.text[:300] + "..."
        except: self.memory[var_name] = "Network Error"
    def port_scan(self, children):
        var_name = str(children[0])
        ip, port = str(self.run(children[1])), int(self.run(children[2]))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        res = s.connect_ex((ip, port))
        self.memory[var_name] = "OPEN" if res == 0 else "CLOSED"
        s.close()
    def encode_data(self, children):
        var_name, data = str(children[0]), str(self.run(children[1]))
        encoded = base64.b64encode(data.encode()).decode()
        self.memory[var_name] = encoded
    def start_thread(self, children):
        t_name = str(children[0])
        threading.Thread(target=lambda: console.print(f"\n[blue]Thread {t_name} is running...[/blue]")).start()
    def wait_action(self, children): time.sleep(float(self.run(children[0])))
    def add(self, args):
        l, r = self.run(args[0]), self.run(args[1])
        if str(r) in ["green", "red", "blue", "yellow", "bold"]: return f"[{r}]{l}[/{r}]"
        try: return float(l) + float(r)
        except: return str(l) + str(r)
    def sub(self, a): return float(self.run(a[0])) - float(self.run(a[1]))
    def mul(self, a): return float(self.run(a[0])) * float(self.run(a[1]))
    def div(self, a): return float(self.run(a[0])) / float(self.run(a[1]))
    def gt(self, a): return self.run(a[0]) > self.run(a[1])
    def lt(self, a): return self.run(a[0]) < self.run(a[1])
    def eq(self, a): return self.run(a[0]) == self.run(a[1])
    def number(self, a): return float(a[0])
    def string(self, a): return str(a[0]).strip('"')
    def get_var(self, a): return self.memory.get(str(a[0]), 0)

# ==========================================
# COMMAND LINE INTERFACE
# ==========================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_logo()
        console.print(f"[bold cyan]Panda Language v{VERSION}[/bold cyan] - Created by [bold yellow]{DEVELOPER}[/bold yellow]")
        console.print("[white]Usage: panda <filename.pd>[/white]")
        console.print("[white]Version check: panda --version[/white]")
        sys.exit()

    arg = sys.argv[1]

    if arg == "--version":
        verify_integrity()
        console.print(f"[bold green]Panda Language 🐼 Version:[/bold green] [bold white]{VERSION}[/bold white]")
        console.print(f"[bold yellow]Developer:[/bold yellow] {DEVELOPER}")
    else:
        show_branding_banner() # Har script ke start mein aayega
        try:
            if os.path.exists(arg):
                with open(arg, 'r') as f:
                    code = f.read()
                    parser = Lark(panda_grammar, parser='lalr')
                    tree = parser.parse(code)
                    PandaInterpreter().run(tree)
            else:
                console.print(f"[bold red]Panda Error 🐼:[/bold red] File '{arg}' nahi mili!")
        except Exception as e:
            console.print(f"[bold red]Panda Error 🐼:[/bold red] {e}")
