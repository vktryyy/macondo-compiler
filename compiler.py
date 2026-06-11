import sys
import os
import subprocess
import tempfile

def optimize(code):
    # split by space, throw out everything that isnt a command
    valid = {"NEXT", "PREV", "INCR", "DECR", "ECHO", "SCAN", "LOOP", "ENDL", "NL"}
    tokens = [t for t in code.split() if t in valid]
    
    # squash repeating instructions so gcc doesn't choke on huge files
    compressed = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ["NEXT", "PREV", "INCR", "DECR"]:
            run = 1
            while i + 1 < len(tokens) and tokens[i+1] == t:
                run += 1
                i += 1
            compressed.append((t, run))
        else:
            compressed.append((t, 1))
        i += 1
    return compressed

def main():
    if len(sys.argv) < 2:
        print("need a file. usage: python compiler.py <src.macondo> [out]")
        sys.exit(1)
        
    infile = sys.argv[1]
    outfile = sys.argv[2] if len(sys.argv) > 2 else "a.out"

    clean_lines = []
    try:
        with open(infile, "r") as f:
            for line in f:
                clean_content = line.split('#')[0]
                clean_lines.append(clean_content)
    except FileNotFoundError:
        print(f"Error: File '{infile}' not found.")
        sys.exit(1)
            
    src = " ".join(clean_lines)
    tokens = optimize(src)
    
    # literally just brainf*** with words lol
    c_src = [
        "#include <stdio.h>",
        "int main() {",
        "    char mem[65536] = {0};",
        "    char *ptr = mem;"
    ]

    indent = 4
    for tok, n in tokens:
        if tok == "ENDL": 
            indent -= 4
            
        space = " " * indent
        
        if tok == "NEXT":   c_src.append(f"{space}ptr += {n};")
        elif tok == "PREV": c_src.append(f"{space}ptr -= {n};")
        elif tok == "INCR": c_src.append(f"{space}*ptr += {n};")
        elif tok == "DECR": c_src.append(f"{space}*ptr -= {n};")
        elif tok == "ECHO": c_src.append(f"{space}putchar(*ptr);")
        elif tok == "SCAN": c_src.append(f"{space}*ptr = getchar();")
        elif tok == "LOOP": 
            c_src.append(f"{space}while (*ptr) {{")
            indent += 4
        elif tok == "ENDL": c_src.append(f"{space}}}")
        elif tok == "NL":   c_src.append(f"{space}putchar('\\n');")

    c_src.append("    return 0;")
    c_src.append("}")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as tmp:
        tmp.write("\n".join(c_src))
        tmp_name = tmp.name

    try:
        cmd = ["gcc", "-O3", tmp_name, "-o", outfile]
        res = subprocess.run(cmd)
        
        if res.returncode == 0:
            print(f"compiled -> {outfile}")
        else:
            print("gcc threw an error.")
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)

if __name__ == "__main__":
    main()
