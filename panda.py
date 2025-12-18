import sys, os, time, requests, psutil, socket, json, base64
from datetime import datetime
from lark import Lark, Tree
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.progress import track

console = Console()
DEVELOPER = "Rizwan Ali"
VERSION = "1.8 (Final Master)"

# ==========================================
# 📝 PANDA MASTER GRAMMAR (Full Syntax)
# ==========================================
panda_grammar = r"""
    start: instruction+
    ?instruction: ("show" | "dikhao") expr             -> show_action
               | ("speak" | "bolo") expr               -> speak_action
               | IDENTIFIER "=" expr                   -> assign_var
               | IDENTIFIER "=" ("pucho" | "ask") STRING -> ask_user
               | ("if" | "agar") condition ":" instruction+ [("else" | "warna") ":" instruction+] -> if_else
               | ("for" | "dohrao") IDENTIFIER "in" NUMBER "," NUMBER ":" instruction+ -> for_loop
               | ("draw" | "tasveer") STRING "," STRING -> draw_shape
               | ("think" | "socho") STRING            -> ai_think
               | ("status" | "halat")                  -> system_status
               | ("lock" | "chhupao") STRING           -> file_lock
               | ("unlock" | "dikhao_file") STRING     -> file_unlock
               | ("light" | "bijli") STRING            -> flash_light
               | ("camera" | "khencho") STRING         -> take_photo
               | ("location" | "kahan")                -> get_gps
               | ("vibrate" | "hilao") NUMBER          -> vibrate_mob
               | ("whatsapp" | "paighaam") STRING "," STRING -> send_wa
               | ("port_scan" | "check_port") STRING   -> scan_port
               | ("ip_info" | "shinaakht") STRING      -> ip_info
               | ("notify" | "khabar") STRING "," STRING -> send_notif
               | ("volume" | "awaaz") NUMBER           -> set_volume
               | ("brightness" | "roshni") NUMBER      -> set_bright
               | ("copy" | "copy_kar") STRING          -> set_clip
               | ("paste" | "paste_kar")               -> get_clip
               | ("run" | "chalao") STRING             -> sys_run
               | ("time" | "waqt")                     -> show_time
               | ("clear" | "saaf")                    -> clear_screen
               | "load" NUMBER                         -> load_action
               | expr                                  -> direct_expr

    ?condition: expr ">" expr -> gt | expr "<" expr -> lt | expr "==" expr -> eq
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
# ⚙️ INTERPRETER CENTER
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

    # --- 🛠️ Networking & Hacking ---
    def send_wa(self, children):
        num, msg = str(children[0]).strip('"'), str(children[1]).strip('"')
        os.system(f"termux-telephony-sms -d {num} {msg}")
        console.print(f"[bold green]✔ Message sent to {num}[/bold green]")

    def scan_port(self, children):
        host = str(children[0]).strip('"')
        console.print(f"[yellow]Scanning {host}...[/yellow]")
        for port in [21, 22, 80, 443]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((host, port)) == 0:
                console.print(f"[green]Port {port} is OPEN[/green]")
            s.close()

    def ip_info(self, children):
        ip = str(children[0]).strip('"')
        try:
            data = requests.get(f"http://ip-api.com/json/{ip}").json()
            console.print(Panel(json.dumps(data, indent=4), title=f"IP Info: {ip}"))
        except: console.print("[red]Connection Error![/red]")

    # --- 📱 Hardware Control ---
    def flash_light(self, children):
        state = str(children[0]).strip('"').lower()
        os.system(f"termux-flashlight {state}")

    def take_photo(self, children):
        fn = str(children[0]).strip('"')
        os.system(f"termux-camera-photo -c 0 {fn}")
        console.print(f"[cyan]Photo saved: {fn}[/cyan]")

    def vibrate_mob(self, children):
        d = int(float(children[0]))
        os.system(f"termux-vibrate -d {d}")

    def set_volume(self, children):
        v = int(float(children[0]))
        os.system(f"termux-volume music {v}")

    def set_bright(self, children):
        b = int(float(children[0]))
        os.system(f"termux-brightness {b}")

    # --- 🧠 AI & Logic ---
    def ai_think(self, children):
        q = str(children[0]).strip('"')
        try:
            r = requests.get(f"https://api.duckduckgo.com/?q={q}&format=json", timeout=5)
            ans = r.json().get("AbstractText", "Mujhe iska ilm nahi.")
            console.print(Panel(ans, title="Panda AI Result", border_style="blue"))
            os.system(f'termux-tts-speak "{ans}"')
        except: console.print("[red]Internet connection required for AI.[/red]")

    def system_status(self, _):
        t = Table(title="Panda Status Monitor")
        t.add_column("Resource")
        t.add_column("Usage")
        t.add_row("CPU", f"{psutil.cpu_percent()}%")
        t.add_row("RAM", f"{psutil.virtual_memory().percent}%")
        console.print(t)

    # --- 📂 Security & Files ---
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
            console.print(Panel(base64.b64decode(data).decode(), title="Unlocked Content"))

    # --- ⚙️ Core Basics ---
    def show_action(self, children): console.print(f"[green]>>>[/green] {self.run(children[0])}")
    def speak_action(self, children): os.system(f'termux-tts-speak "{self.run(children[0])}"')
    def assign_var(self, children): self.variables[str(children[0])] = self.run(children[1])
    def ask_user(self, children):
        v, p = str(children[0]), str(children[1]).strip('"')
        val = console.input(f"[yellow]{p}[/yellow] ")
        try: self.variables[v] = float(val)
        except: self.variables[v] = val
    def for_loop(self, children):
        v, s, e = str(children[0]), int(float(children[1])), int(float(children[2]))
        for i in range(s, e):
            self.variables[v] = float(i)
            for node in children[3:]: self.run(node)
    def draw_shape(self, children):
        s, c = str(children[0]).strip('"').lower(), str(children[1]).strip('"').lower()
        shapes = {"panda": "\n m( )m \n( ● .. ● )\n >  ♥  <\n", "square": "████\n████"}
        console.print(Align.center(Text(shapes.get(s, "Not Found"), style=c)))
    def clear_screen(self, _): os.system('clear')
    def show_time(self, _): console.print(f"[cyan]Time:[/cyan] {datetime.now().strftime('%H:%M:%S')}")
    def load_action(self, children):
        for _ in track(range(int(float(children[0]))), description="Processing..."): time.sleep(0.05)

    # Math Helpers
    def add(self, a):
        l, r = self.run(a[0]), self.run(a[1])
        return str(l) + str(r) if isinstance(l, str) or isinstance(r, str) else l + r
    def sub(self, a): return self.run(a[0]) - self.run(a[1])
    def mul(self, a): return self.run(a[0]) * self.run(a[1])
    def div(self, a): return self.run(a[0]) / self.run(a[1])
    def number(self, a): return float(a[0])
    def string(self, a): return str(a[0]).strip('"')
    def get_var(self, a): return self.variables.get(str(a[0]), 0)

# ==========================================
# 🚀 REPL START
# ==========================================
def start_repl():
    os.system("clear")
    logo = f"[bold magenta]PANDA 🐼 {VERSION}[/bold magenta]\n[bold cyan]Developer: {DEVELOPER}[/bold cyan]"
    console.print(Panel(logo, border_style="bold green", expand=False))
    i, p = PandaInterpreter(), Lark(panda_grammar, parser='lalr')
    while True:
        try:
            inp = console.input("[bold pink]panda ❯ [/bold pink]")
            if inp.lower() in ["exit", "niklo"]: break
            i.run(p.parse(inp))
        except Exception as e: console.print(f"[red]Error:[/red] {e}")

if __name__ == "__main__":
    start_repl()
