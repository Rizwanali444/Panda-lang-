# Panda 🐼 Interpreter v0.1 
# Author: Rizwan Ali — License: MIT

import sys, math, random, datetime, json, os, statistics, asyncio
import requests

VARS = {}

COLORS = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "BLUE": "\033[94m",
    "YELLOW": "\033[93m",
    "CYAN": "\033[96m",
    "MAGENTA": "\033[95m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
    "ITALIC": "\033[3m",
    "RESET": "\033[0m"
}

def say(text, style=None):
    if style and style.upper() in COLORS:
        print(COLORS[style.upper()] + str(text) + COLORS["RESET"])
    else:
        print(text)

def eval_expr(expr):
    try:
        return eval(expr, {"__builtins__": {}}, VARS)
    except:
        return VARS.get(expr, expr)

def run_lines(lines):
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        cmd = parts[0].upper()

        # SAY / COLOR / STYLING
        if cmd == "SAY":
            say(" ".join(parts[1:]))
        elif cmd == "COLOR":
            color = parts[1]
            if parts[2].upper() == "SAY":
                say(" ".join(parts[3:]), color)
        elif cmd in ("BOLD","UNDERLINE","ITALIC"):
            if parts[1].upper() == "SAY":
                say(" ".join(parts[2:]), cmd)

        # VARIABLES
        elif cmd in ("LET","SET"):
            name = parts[1]
            if "=" in line:
                expr = line.split("=",1)[1].strip()
                VARS[name] = eval_expr(expr)
            else:
                VARS[name] = " ".join(parts[2:])

        # CONTROL FLOW
        elif cmd == "BREAK":
            break
        elif cmd == "CONTINUE":
            continue

        # MATH
        elif cmd == "ADD":
            say(eval_expr(parts[1]) + eval_expr(parts[2]))
        elif cmd == "SUB":
            say(eval_expr(parts[1]) - eval_expr(parts[2]))
        elif cmd == "MUL":
            say(eval_expr(parts[1]) * eval_expr(parts[2]))
        elif cmd == "DIV":
            b = eval_expr(parts[2])
            say(eval_expr(parts[1]) / b if b!=0 else "Error: Division by zero")
        elif cmd == "SQRT":
            say(math.sqrt(float(parts[1])))
        elif cmd == "POW":
            say(math.pow(float(parts[1]), float(parts[2])))
        elif cmd == "EXP":
            say(math.exp(float(parts[1])))
        elif cmd == "PI":
            say(math.pi)
        elif cmd == "E":
            say(math.e)
        elif cmd == "STATMEAN":
            nums = [float(x) for x in parts[1:]]
            say(statistics.mean(nums))
        elif cmd == "STATMEDIAN":
            nums = [float(x) for x in parts[1:]]
            say(statistics.median(nums))
        elif cmd == "STDEV":
            nums = [float(x) for x in parts[1:]]
            say(statistics.stdev(nums))

        # RANDOM
        elif cmd == "RANDOM":
            say(random.randint(int(parts[1]), int(parts[2])))
        elif cmd == "CHOICE":
            say(random.choice(parts[1:]))

        # DATE/TIME
        elif cmd == "NOW":
            say(datetime.datetime.now())
        elif cmd == "DATE":
            say(datetime.date.today())
        elif cmd == "TIME":
            say(datetime.datetime.now().strftime("%H:%M:%S"))

        # STRING
        elif cmd == "UPPER":
            say(" ".join(parts[1:]).upper())
        elif cmd == "LOWER":
            say(" ".join(parts[1:]).lower())
        elif cmd == "REPLACE":
            s, old, new = parts[1], parts[2], parts[3]
            say(s.replace(old,new))
        elif cmd == "SPLIT":
            s, sep = parts[1], parts[2]
            say(s.split(sep))
        elif cmd == "JOIN":
            sep = parts[1]
            say(sep.join(parts[2:]))

        # FILE IO
        elif cmd == "WRITEFILE":
            path = parts[1]; content = " ".join(parts[2:])
            with open(path,"w",encoding="utf-8") as f: f.write(content)
        elif cmd == "APPENDFILE":
            path = parts[1]; content = " ".join(parts[2:])
            with open(path,"a",encoding="utf-8") as f: f.write(content)
        elif cmd == "READFILE":
            path = parts[1]
            with open(path,encoding="utf-8") as f: say(f.read())
        elif cmd == "DELETEFILE":
            os.remove(parts[1])
        elif cmd == "MKDIR":
            os.makedirs(parts[1], exist_ok=True)
        elif cmd == "LISTDIR":
            say(os.listdir(parts[1]))

        # NETWORK
        elif cmd == "HTTPGET":
            url = parts[1]; r = requests.get(url)
            say(r.text[:200]+"...")
        elif cmd == "HTTPPOST":
            url = parts[1]; data = " ".join(parts[2:])
            r = requests.post(url,data=data)
            say(r.text[:200]+"...")
        elif cmd == "DOWNLOAD":
            url, path = parts[1], parts[2]
            r = requests.get(url)
            with open(path,"wb") as f: f.write(r.content)
            say(f"Downloaded {path}")
        elif cmd == "PING":
            host = parts[1]
            response = os.system(f"ping -c 1 {host}")
            say("Ping success" if response==0 else "Ping failed")

        # SYSTEM
        elif cmd == "SHELL":
            os.system(" ".join(parts[1:]))
        elif cmd == "CLEAR":
            print("\033[2J\033[H", end="")
        elif cmd == "EXIT":
            sys.exit(0)

        # CONCURRENCY
        elif cmd == "WAIT":
            import time; time.sleep(int(parts[1]))
        elif cmd == "ASYNC":
            if parts[1].upper()=="HTTPGET":
                url = parts[2]
                asyncio.run(async_httpget(url))

        else:
            say("Unknown command: "+cmd)

async def async_httpget(url):
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, requests.get, url)
    r = await future
    say(r.text[:200]+"...")

def run_file(filename):
    with open(filename,encoding="utf-8") as f:
        run_lines(f.readlines())
