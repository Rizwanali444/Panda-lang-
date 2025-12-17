# Panda 🐼 Interpreter v0.1 
# Author: Rizwan Ali — License: MIT

import sys, math, random, datetime, json, os
import requests   # for HTTPGET/HTTPPOST

VARS = {}

COLORS = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "BLUE": "\033[94m",
    "YELLOW": "\033[93m",
    "CYAN": "\033[96m",
    "MAGENTA": "\033[95m",
    "RESET": "\033[0m"
}

def say(text, color=None):
    if color and color.upper() in COLORS:
        print(COLORS[color.upper()] + str(text) + COLORS["RESET"])
    else:
        print(text)

def run_lines(lines):
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        cmd = parts[0].upper()

        # SAY
        if cmd == "SAY":
            say(" ".join(parts[1:]))
        elif cmd == "COLOR":
            color = parts[1]
            if parts[2].upper() == "SAY":
                say(" ".join(parts[3:]), color)

        # LET / SET
        elif cmd in ("LET", "SET"):
            name = parts[1]
            if "=" in line:
                expr = line.split("=",1)[1].strip()
                VARS[name] = eval_expr(expr)
            else:
                VARS[name] = " ".join(parts[2:])

        # MATH
        elif cmd == "ADD":
            a, b = eval_expr(parts[1]), eval_expr(parts[2])
            say(a+b)
        elif cmd == "SUB":
            a, b = eval_expr(parts[1]), eval_expr(parts[2])
            say(a-b)
        elif cmd == "MUL":
            a, b = eval_expr(parts[1]), eval_expr(parts[2])
            say(a*b)
        elif cmd == "DIV":
            a, b = eval_expr(parts[1]), eval_expr(parts[2])
            say(a/b if b!=0 else "Error: Division by zero")
        elif cmd == "SIN":
            say(math.sin(math.radians(float(parts[1]))))
        elif cmd == "COS":
            say(math.cos(math.radians(float(parts[1]))))
        elif cmd == "LOG":
            say(math.log(float(parts[1])))
        elif cmd == "ROUND":
            say(round(float(parts[1]), int(parts[2])))

        # RANDOM
        elif cmd == "RANDOM":
            a, b = int(parts[1]), int(parts[2])
            say(random.randint(a,b))

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

        # FILE IO
        elif cmd == "WRITEFILE":
            path = parts[1]
            content = " ".join(parts[2:])
            with open(path,"w",encoding="utf-8") as f:
                f.write(content)
        elif cmd == "READFILE":
            path = parts[1]
            with open(path,encoding="utf-8") as f:
                say(f.read())

        # NETWORK
        elif cmd == "HTTPGET":
            url = parts[1]
            r = requests.get(url)
            say(r.text[:200]+"...")  # preview
        elif cmd == "HTTPPOST":
            url = parts[1]
            data = " ".join(parts[2:])
            r = requests.post(url,data=data)
            say(r.text[:200]+"...")

        # SYSTEM
        elif cmd == "SHELL":
            os.system(" ".join(parts[1:]))
        elif cmd == "CLEAR":
            print("\033[2J\033[H", end="")
        elif cmd == "EXIT":
            sys.exit(0)

        else:
            say("Unknown command: "+cmd)

def eval_expr(expr):
    try:
        return eval(expr, {"__builtins__": {}}, VARS)
    except:
        return VARS.get(expr, expr)

def run_file(filename):
    with open(filename,encoding="utf-8") as f:
        run_lines(f.readlines())
