# Panda 🐼 Interpreter v0.1
import sys

def run_code(code: str):
    for line in code.splitlines():
        parts = line.strip().split()
        if not parts:
            continue

        cmd = parts[0].upper()

        if cmd == "SAY":
            print(" ".join(parts[1:]))
        elif cmd == "COLOR":
            # simple demo: just show color name + text
            color = parts[1].upper()
            text = " ".join(parts[2:])
            print(f"[{color}] {text}")
        else:
            print(f"Unknown command: {line}")

def run_file(path: str):
    with open(path, "r") as f:
        code = f.read()
    run_code(code)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/panda/interpreter.py <script.pd>")
    else:
        run_file(sys.argv[1])
