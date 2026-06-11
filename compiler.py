import sys
import os
import subprocess

def optimize(code):
    # split by space, throw out everything that isn't a command
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

    # read source - just crash if file doesn't exist, user's problem
    with open(infile, "r") as f:
        src = f.read()

    tokens = optimize(src)
    
    # literally just brainf*** with words lol
    c_src = [
        "#include <stdio.h>",
        "int main() {",
        "    char mem[30000] = {0};",
        "    char *ptr = mem;"
    ]

    for tok, n in tokens:
        if tok == "NEXT":   c_src.append(f"    ptr += {n};")
        elif tok == "PREV": c_src.append(f"    ptr -= {n};")
        elif tok == "INCR": c_src.append(f"    *ptr += {n};")
        elif tok == "DECR": c_src.append(f"    *ptr -= {n};")
        elif tok == "ECHO": c_src.append("    putchar(*ptr);")
        elif tok == "SCAN": c_src.append("    *ptr = getchar();")
        elif tok == "LOOP": c_src.append("    while (*ptr) {")
        elif tok == "ENDL": c_src.append("    }")
        elif tok == "NL":   c_src.append("    putchar('\\n');")

    c_src.append("    return 0;")
    c_src.append("}")

    # dump to temporary file and compile
    tmp_name = f"_temp_{outfile}.c"
    with open(tmp_name, "w") as f:
        f.write("\n".join(c_src))

    cmd = ["gcc", "-O3", tmp_name, "-o", outfile]
    res = subprocess.run(cmd)
    
    # cleanup temp file
    if os.path.exists(tmp_name):
        os.remove(tmp_name)

    if res.returncode == 0:
        print(f"compiled -> {outfile}")
    else:
        print("gcc threw an error.")

if __name__ == "__main__":
    main()