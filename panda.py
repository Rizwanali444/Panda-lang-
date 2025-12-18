import sys
import os
import time
import requests
import psutil  # Battery/RAM ke liye: pip install psutil
from datetime import datetime
from lark import Lark, Tree
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.progress import track
import base64

console = Console()

# ==========================================
# 🛡️ PANDA CORE INFO
# ==========================================
DEVELOPER = "Rizwan Ali"
VERSION = "1.5 (All-in-One Master)"

def show_logo():
    logo = (
        "[bold magenta]      _      _      [/bold magenta]\n"
        "[bold cyan]    m( )mm( )m    [/bold cyan]\n"
        "[bold white]   (  ●  ..  ●  )   [/bold white] [bold cyan]PANDA 🐼 v" + VERSION + "[/bold cyan]\n"
        "[bold pink]    >   ♥   <     [/bold pink] [bold yellow]By Rizwan Ali[/bold yellow]\n"
        "[bold blue]   (    ~~    )    [/bold blue]\n"
        "[bold yellow]    (  v  v  )     [/bold yellow]\n"
        "[bold red]     \"\"    \"\"      [/bold red]"
    )
    console.print(Panel(logo, border_style="bold green", padding=(0, 2), expand=False))

# ==========================================
# 📝 PANDA MASTER GRAMMAR
# ==========================================
panda_grammar = r"""
    start: instruction+
    ?instruction: ("show" | "dikhao") expr             -> show_action
               | ("speak" | "bolo") expr               -> speak_action
               | IDENTIFIER "=" expr                   -> assign_var
               | IDENTIFIER "=" ("pucho" | "ask") STRING -> ask_user
               | ("if" | "agar") condition ":" instruction+ [("else" | "warna") ":" instruction+] -> if_else
               | ("for" | "dohrao") IDENTIFIER "in" NUMBER "," NUMBER ":" instruction+ -> for_loop
               | ("while" | "jab_tak") condition ":" instruction+ -> while_loop
               | ("table" | "naqsha") expr "," expr    -> table_action
               | ("create" | "banao") STRING           -> file_create
               | ("write" | "likho") expr "," expr     -> file_write
               | ("read" | "parho") STRING             -> file_read
               | ("draw" | "tasveer") STRING "," STRING -> draw_shape
               | ("set_response" | "jawab_do") STRING "," STRING -> set_response
               | ("ask_bot" | "bot_se_pucho") STRING   -> ask_bot_action
               | ("think" | "socho") STRING            -> ai_think
               | ("status" | "halat")                  -> system_status
               | ("lock" | "chhupao") STRING           -> file_lock
               | ("unlock" | "dikhao_file") STRING     -> file_unlock
               | ("run" | "chalao") STRING             -> sys_run
               | ("get" | "le_ao") STRING              -> http_get
               | ("time" | "waqt")                     -> show_time
               | ("help" | "madad")                    -> show_help
               | ("clear" | "saaf")                    -> clear_screen
               | "load" NUMBER                         -> load_action
               | expr                                  -> direct_expr

    ?condition: expr ">" expr                          -> gt | expr "<" expr -> lt | expr "==" expr -> eq
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
    def __init__(self):
        self.variables = {}
        self.chatbot_responses = {}

    def run(self, tree):
        if isinstance(tree, Tree):
            method = getattr(self, tree.data, self.generic_run)
            return method(tree.children)
        return tree

    def generic_run(self, children):
        res = None
        for child in children: res = self.run(child)
        return res

    # AI & System Features
    def ai_think(self, children):
        query = str(children[0]).strip('"')
        try:
            r = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json", timeout=5)
            ans = r.json().get("AbstractText", "I don't know yet.")
            console.print(Panel(ans if ans else "No info found.", title="AI Result"))
            os.system(f'termux-tts-speak "{ans}"')
        except: console.print("[red]Internet error.[/red]")

    def system_status(self, _):
        battery = psutil.sensors_battery()
        ram = psutil.virtual_memory()
        t = Table(title="System Monitor")
        t.add_row("Battery", f"{battery.percent}%" if battery else "N/A")
        t.add_row("RAM Used", f"{ram.percent}%")
        console.print(t)

    def file_lock(self, children):
        fn = str(children[0]).strip('"')
        if os.path.exists(fn):
            with open(fn, 'rb') as f: data = f.read()
            with open(fn, 'wb') as f: f.write(base64.b64encode(data))
            console.print(f"[red]Locked: {fn}[/red]")

    def file_unlock(self, children):
        fn = str(children[0]).strip('"')
        if os.path.exists(fn):
            with open(fn, 'rb') as f: data = f.read()
            console.print(Panel(base64.b64decode(data).decode(), title="Unlocked"))

    # Core Logic & UI
    def speak_action(self, children):
        txt = self.run(children[0])
        os.system(f'termux-tts-speak "{txt}"')

    def draw_shape(self, children):
        s, c = str(children[0]).strip('"').lower(), str(children[1]).strip('"').lower()
        shapes = {"square": "\n████\n████\n", "panda": "\n m( )m \n( ● .. ● )\n"}
        console.print(Align.center(Text(shapes.get(s, "Error"), style=c)))

    def table_action(self, children):
        h, d = str(self.run(children[0])), str(self.run(children[1]))
        t = Table()
        for col in h.split(","): t.add_column(col.strip())
        t.add_row(*[val.strip() for val in d.split(",")])
        console.print(t)

    def for_loop(self, children):
        v, s, e = str(children[0]), int(float(children[1])), int(float(children[2]))
        for i in range(s, e):
            self.variables[v] = float(i)
            for node in children[3:]: self.run(node)

    def show_action(self, children): console.print(f"[green]>>>[/green] {self.run(children[0])}")
    def ask_user(self, children):
        v, p = str(children[0]), str(children[1]).strip('"')
        self.variables[v] = console.input(f"[yellow]{p}[/yellow] ")
    def assign_var(self, children): self.variables[str(children[0])] = self.run(children[1])
    def sys_run(self, children): os.system(str(children[0]).strip('"'))
    def show_time(self, _): console.print(f"[cyan]Time:[/cyan] {datetime.now()}")
    def load_action(self, children):
        for _ in track(range(int(float(children[0]))), description="Processing..."): time.sleep(0.05)
    def show_help(self, _): console.print(Panel("Commands: dikhao, bolo, dohrao, halat, socho, tasveer, chhupao"))
    def clear_screen(self, _): os.system('clear')

    # Math & Helper
    def add(self, a):
        l, r = self.run(a[0]), self.run(a[1])
        return str(l) + str(r) if isinstance(l, (str)) or isinstance(r, (str)) else l + r
    def number(self, a): return float(a[0])
    def string(self, a): return str(a[0]).strip('"')
    def get_var(self, a): return self.variables.get(str(a[0]), 0)
    def gt(self, c): return self.run(c[0]) > self.run(c[1])
    def lt(self, c): return self.run(c[0]) < self.run(c[1])
    def eq(self, c): return self.run(c[0]) == self.run(c[1])

def start_repl():
    os.system("clear"); show_logo()
    i, p = PandaInterpreter(), Lark(panda_grammar, parser='lalr')
    while True:
        try:
            inp = console.input("[bold pink]panda ❯ [/bold pink]")
            if inp.lower() in ["exit", "niklo"]: break
            i.run(p.parse(inp))
        except Exception as e: console.print(f"[red]Error:[/red] {e}")

if __name__ == "__main__":
    start_repl()
