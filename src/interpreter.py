# Panda 🐼 Interpreter — v0.1 
# Author: Rizwan Ali — License: MIT

def run_lines(lines):
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("SAY"):
            print(line[4:])
        elif line.startswith("LET"):
            parts = line[4:].split("=")
            if len(parts) == 2:
                name = parts[0].strip()
                value = parts[1].strip()
                globals()[name] = value
        elif line.startswith("COLOR"):
            color, rest = line[6:].split("SAY", 1)
            color = color.strip().upper()
            text = rest.strip()
            codes = {"RED": "\033[91m", "GREEN": "\033[92m", "BLUE": "\033[94m", "YELLOW": "\033[93m"}
            print(codes.get(color, "") + text + "\033[0m")
        else:
            print("Unknown command:", line)

def run_file(filename):
    with open(filename, encoding="utf-8") as f:
        run_lines(f.readlines())
