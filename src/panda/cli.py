# Panda 🐼 CLI v0.1
import sys
from .interpreter import run_file

def main():
    if len(sys.argv) < 2:
        print("Usage: panda <script.pd>")
        return
    script = sys.argv[1]
    run_file(script)
