import sys, os, time, requests, psutil, socket, json, base64, webbrowser, subprocess
from datetime import datetime
from lark import Lark, Tree
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.progress import track

# ==========================================
# 🛠️ SYSTEM CONFIGURATION
# ==========================================
console = Console()
DEVELOPER = "Rizwan Ali"
VERSION = "3.0 (Ultimate Master Edition)"

# ==========================================
# 📝 MASTER GRAMMAR (Full Syntax)
# ==========================================
panda_grammar = r"""
    start: (instruction | _comment)*
    
    ?instruction: ("show" | "dikhao") expr             -> show_action
               | ("speak" | "bolo") expr               -> speak_action
               | IDENTIFIER "=" expr                   -> assign_var
               | IDENTIFIER "=" ("pucho" | "ask") STRING -> ask_user
               
               | "def" IDENTIFIER "(" ")" ":" instruction+ -> def_func
               | IDENTIFIER "(" ")"                    -> call_func
               
               | ("if" | "agar") condition ":" instruction+ [("else" | "warna") ":" instruction+] -> if_else
               | ("for" | "dohrao") IDENTIFIER "in" NUMBER "," NUMBER ":" instruction+ -> for_loop
               
               | ("draw" | "tasveer") STRING "," STRING -> draw_shape
               | ("think" | "socho") STRING            -> ai_think
               | ("status" | "halat")                  -> system_status
               
               | ("write" | "likho") STRING "," STRING -> write_file
               | ("read" | "parho") STRING             -> read_file
               | ("lock" | "chhupao") STRING           -> file_lock
               | ("unlock" | "dikhao_file") STRING     -> file_unlock
               
               | ("music" | "gana") STRING             -> play_music
               | ("youtube" | "yt") STRING             -> search_yt
               | ("open" | "kholo") STRING             -> open_anything
               | ("gallery" | "tasveerein")            -> open_gallery
               | ("manager" | "files")                 -> open_manager
               
               | ("light" | "bijli") STRING            -> flash_light
               | ("camera" | "khencho") STRING         -> take_photo
               | ("vibrate" | "hilao") NUMBER          -> vibrate_mob
               | ("guard" | "pehra")                   -> security_guard
               
               | ("whatsapp" | "paighaam") STRING "," STRING -> send_wa
               | ("port_scan" | "check_port") STRING   -> scan_port
               | ("ip_info" | "shinaakht") STRING      -> ip_info
               
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
# ⚙️ INTERPRETER CENTER
# ==========================================
class PandaInterpreter:
    def __init__(self):
        self.variables = {"dev": DEVELOPER, "ver": VERSION}
        self.functions = {}

    def run(self, tree):
        if isinstance(tree, Tree):
            method = getattr(self, tree.data, self.generic_run)
            return method(tree.children)
        return tree

    def generic_run(self, children):
        res = None
        for child in children:
            if isinstance(child, Tree): res = self.run(child)
        return res

    # --- 🏗️ Functions & Logic ---
    def def_func(self, children):
        name = str(children[0]); body = children[1:]
        self.functions[name] = body
        console.print(f"[bold cyan]◈ Function Stored: {name}[/bold cyan]")

    def call_func(self, children):
        name = str(children[0])
        if name in self.functions:
            for node in self.functions[name]: self.run(node)
        else: console.print(f"[red]Error: '{name}' missing![/red]")

    def if_else(self, children):
        cond = self.run(children[0])
        if cond:
            for instr in children[1:2]: self.run(instr)
        elif len(children) > 2:
            for instr in children[2:]: self.run(instr)

    def for_loop(self, children):
        var, s, e = str(children[0]), int(float(children[1])), int(float(children[2]))
        for i in range(s, e):
            self.variables[var] = float(i)
            for instr in children[3:]: self.run(instr)

    # --- 🎵 Media & Android ---
    def play_music(self, children):
        q = str(children[0]).strip('"')
        console.print(f"[bold green]Searching YT Music: {q}[/bold green]")
        url = f"https://music.youtube.com/search?q={q.replace(' ', '+')}"
        os.system(f"termux-open-url '{url}'")

    def search_yt(self, children):
        q = str(children[0]).strip('"')
        os.system(f"termux-open-url 'https://youtube.com/results?search_query={q}'")

    def open_anything(self, children):
        path = str(children[0]).strip('"')
        os.system(f"termux-open '{path}'")

    def open_gallery(self, _):
        os.system("am start -a android.intent.action.VIEW -t image/*")

    def open_manager(self, _):
        os.system("am start -n com.android.documentsui/.files.FilesActivity")

    # --- 🛡️ Security & Files ---
    def write_file(self, children):
        fn, txt = str(children[0]).strip('"'), str(children[1]).strip('"')
        with open(fn, 'w') as f: f.write(txt)
        console.print(f"[green]File '{fn}' saved.[/green]")

    def read_file(self, children):
        fn = str(children[0]).strip('"')
        if os.path.exists(fn):
            with open(fn, 'r') as f: console.print(Panel(f.read(), title=fn))

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

    # --- 📱 Hardware & AI ---
    def system_status(self, _):
        t = Table(title="Panda System Report", show_lines=True)
        t.add_column("Monitor", style="cyan"); t.add_column("Usage", style="green")
        t.add_row("RAM", f"{psutil.virtual_memory().percent}%")
        try:
            bat = json.loads(os.popen("termux-battery-status").read())
            t.add_row("Battery", f"{bat['percentage']}% ({bat['status']})")
        except: t.add_row("Battery", "N/A")
        console.print(t)

    def ai_think(self, children):
        q = str(children[0]).strip('"')
        console.print(f"[cyan]Panda AI is thinking: {q}...[/cyan]")
        try:
            r = requests.get(f"https://api.duckduckgo.com/?q={q}&format=json").json()
            ans = r.get("AbstractText", "Ilm nahi hai.")
            console.print(Panel(ans, title="AI Response"))
        except: console.print("[red]Internet check karein![/red]")

    def flash_light(self, children):
        s = str(children[0]).strip('"').lower()
        os.system(f"termux-flashlight {s}")

    def vibrate_mob(self, children):
        d = int(float(children[0]))
        os.system(f"termux-vibrate -d {d}")

    # --- ⚙️ Core Operations ---
    def show_action(self, children): console.print(f"[bold green]>>>[/bold green] {self.run(children[0])}")
    def speak_action(self, children): os.system(f'termux-tts-speak "{self.run(children[0])}"')
    def clear_screen(self, _): os.system('clear')
    def show_time(self, _): console.print(f"[yellow]Waqt:[/yellow] {datetime.now().strftime('%H:%M:%S')}")
    def load_action(self, children):
        for _ in track(range(int(float(children[0]))), description="Panda working..."): time.sleep(0.05)

    def draw_shape(self, children):
        s, c = str(children[0]).strip('"').lower(), str(children[1]).strip('"').lower()
        if s == "panda": console.print(Align.center(Text("\n m( )m \n( ● .. ● )\n >  ♥  <\n", style=c)))

    def assign_var(self, children): self.variables[str(children[0])] = self.run(children[1])
    def add(self, a):
        l, r = self.run(a[0]), self.run(a[1])
        return str(l) + str(r) if isinstance(l, str) or isinstance(r, str) else l + r
    def sub(self, a): return self.run(a[0]) - self.run(a[1])
    def mul(self, a): return self.run(a[0]) * self.run(a[1])
    def div(self, a): return self.run(a[0]) / self.run(a[1])
    def gt(self, a): return self.run(a[0]) > self.run(a[1])
    def lt(self, a): return self.run(a[0]) < self.run(a[1])
    def eq(self, a): return self.run(a[0]) == self.run(a[1])
    def number(self, a): return float(a[0])
    def string(self, a): return str(a[0]).strip('"')
    def get_var(self, a): return self.variables.get(str(a[0]), 0)

# ==========================================
# 🚀 RUNNER
# ==========================================
def start_repl():
    os.system("clear")
    logo = f"[bold white]PANDA ENGINE 🐼[/bold white]\n[bold green]{VERSION}[/bold green]\n[bold cyan]Developer: {DEVELOPER}[/bold cyan]"
    console.print(Panel(Align.center(logo), border_style="bold green"))
    i, p = PandaInterpreter(), Lark(panda_grammar, parser='lalr')
    while True:
        try:
            inp = console.input("[bold magenta]panda ❯ [/bold magenta]")
            if not inp.strip(): continue
            if inp.lower() in ["exit", "niklo"]: break
            i.run(p.parse(inp))
        except Exception as e: console.print(f"[bold red]❌ ERROR:[/bold red] {e}")

def run_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f: script = f.read()
        i, p = PandaInterpreter(), Lark(panda_grammar, parser='lalr')
        try: i.run(p.parse(script))
        except Exception as e: console.print(f"[red]Error in {filename}:[/red] {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1: run_file(sys.argv[1])
    else: start_repl()
