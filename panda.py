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

console = Console()

# ==========================================
# 🛡️ PANDA CORE SECURITY
# ==========================================
DEVELOPER = "Rizwan Ali"
VERSION = "0.1"
COPYRIGHT = f"© 2024-2025 {DEVELOPER}"

def show_security_alert():
    # Warning in a small red box
    alert_text = "[bold white]🛑 SECURITY ALERT[/bold white]\n[white]Engine Integrity Compromised!\nModification not allowed.[/white]"
    console.print(Panel(alert_text, border_style="red", title="[bold red]Error[/bold red]", expand=False))
    sys.exit()

def verify_integrity():
    # Simple check: Agar naam 'Rizwan Ali' nahi hai to block
    if DEVELOPER != "Rizwan Ali":
        show_security_alert()

def show_branding_banner():
    verify_integrity()
    banner_text = f"[bold cyan]🐼 PANDA ENGINE v{VERSION}[/bold cyan]\n[bold yellow]By: {DEVELOPER}[/bold yellow]"
    console.print(Panel(banner_text, border_style="magenta", expand=False))

def show_logo():
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
# PANDA GRAMMAR & INTERPRETER
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

class PandaInterpreter:
    def __init__(self): self.memory = {}
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
    def system_cmd(self, children): os.system(str(self.run(children[0])))
    def add(self, args):
        l, r = self.run(args[0]), self.run(args[1])
        if str(r) in ["green", "red", "blue", "yellow", "bold"]: return f"[{r}]{l}[/{r}]"
        try: return float(l) + float(r)
        except: return str(l) + str(r)
    def number(self, a): return float(a[0])
    def string(self, a): return str(a[0]).strip('"')
    def get_var(self, a): return self.memory.get(str(a[0]), 0)

# ==========================================
# COMMAND LINE INTERFACE
# ==========================================
if __name__ == "__main__":
    verify_integrity()
    
    if len(sys.argv) < 2:
        show_logo()
        console.print(f"[bold cyan]Panda Language v{VERSION}[/bold cyan]")
        console.print("[white]Usage: panda <filename.pd> | panda --version[/white]")
        sys.exit()

    arg = sys.argv[1]

    if arg == "--version":
        console.print(Panel(f"[bold green]Panda 🐼 Version:[/bold green] {VERSION}\n[bold yellow]Developer:[/bold yellow] {DEVELOPER}", border_style="blue", expand=False))
    else:
        if os.path.exists(arg):
            show_branding_banner()
            try:
                with open(arg, 'r') as f:
                    code = f.read()
                    parser = Lark(panda_grammar, parser='lalr')
                    tree = parser.parse(code)
                    PandaInterpreter().run(tree)
            except Exception as e:
                console.print(f"[bold red]Panda Error:[/bold red] {e}")
        else:
            console.print(f"[bold red]Error:[/bold red] File '{arg}' not found.")
