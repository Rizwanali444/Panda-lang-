import sys
from .interpreter import run_file

def main():
    if len(sys.argv) < 2:
        print("Usage: panda <file.pd>")
        sys.exit(1)
    run_file(sys.argv[1])
