import streamlit as st
import subprocess
import tempfile
import os
import shutil

# --- Copying your exact Compiler Logic (Streamlined for Web) ---
def optimize(code):
    valid = {"NEXT", "PREV", "INCR", "DECR", "ECHO", "SCAN", "LOOP", "ENDL", "NL"}
    tokens = [t for t in code.split() if t in valid]
    compressed = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ["NEXT", "PREV", "INCR", "DECR"]:
            run = 1
            while i + 1 < len(tokens) and tokens[i + 1] == t:
                run += 1
                i += 1
            compressed.append((t, run))
        else:
            compressed.append((t, 1))
        i += 1
    return compressed

def generate_c_code(macondo_code):
    tokens = optimize(macondo_code)
    c_src = [
        "#include <stdio.h>",
        "int main() {",
        "    char mem[65536] = {0};",
        "    char *ptr = mem;"
    ]
    indent = 4
    for tok, n in tokens:
        if tok == "ENDL": indent -= 4
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
    return "\n".join(c_src)

# --- Streamlit UI App ---
st.set_page_config(page_title="Macondo Compiler Showcase", layout="wide")

st.title("🇨🇴 The Macondo Language Compiler")
st.subheader("A Brainfuck-to-C Compiler Written in Python")

# Sidebar Guide
with st.sidebar:
    st.header("📖 Macondo Syntax Guide")
    st.markdown("""
    Macondo is a verbose, readable alternative to Brainfuck. Here is the mapping:
    * `NEXT` : Move pointer right (`>`)
    * `PREV` : Move pointer left (`<`)
    * `INCR` : Increment byte (`+`)
    * `DECR` : Decrement byte (`-`)
    * `ECHO` : Output current byte (`.`)
    * `SCAN` : Input current byte (`,`)
    * `LOOP` : Start loop (`[`)
    * `ENDL` : End loop (`]`)
    * `NL`   : Print a newline character
    * `#`    : Comments are ignored
    """)
    st.info("The compiler optimizes repeated instructions (e.g., 5 `INCR` tokens become `*ptr += 5;` in C).")

# Layout columns
col1, col2 = st.columns(2)

with col1:
    st.header("1. Write Macondo Code")
    
    # Default Hello World Example in Macondo
    default_code = """# Hello World in Macondo
INCR INCR INCR INCR INCR INCR INCR INCR LOOP
    NEXT INCR INCR INCR INCR LOOP
        NEXT INCR INCR NEXT INCR INCR INCR NEXT INCR INCR INCR NEXT INCR PREV PREV PREV PREV DECR
    ENDL
    NEXT INCR NEXT INCR NEXT DECR NEXT NEXT INCR LOOP PREV ENDL PREV DECR
ENDL
NEXT NEXT ECHO NEXT DECR DECR DECR ECHO INCR INCR INCR INCR INCR INCR INCR ECHO ECHO INCR INCR INCR ECHO
NEXT NEXT ECHO PREV DECR ECHO PREV ECHO INCR INCR INCR ECHO DECR DECR DECR DECR DECR DECR ECHO
DECR DECR DECR DECR DECR DECR DECR DECR ECHO NEXT NEXT INCR ECHO NEXT INCR INCR ECHO NL"""

    user_code = st.text_area("Enter your code here:", value=default_code, height=350)
    compile_btn = st.button("Compile & Run Code", type="primary")

with col2:
    st.header("2. Compiler Outputs")
    
    if compile_btn or user_code:
        # 1. Generate C code
        c_output = generate_c_code(user_code)
        
        st.subheader("Generated C Source")
        st.code(c_output, language="c")
        
        # 2. Compile and Run using System GCC
        if compile_btn:
            st.subheader("Execution Output")
            compiler_path = shutil.which("gcc") or shutil.which("clang")
            
            if not compiler_path:
                st.error("Error: No C compiler found on the server environment. Ensure packages.txt includes 'gcc'.")
            else:
                # Use temp files to compile and run safely
                with tempfile.TemporaryDirectory() as tmpdir:
                    c_file_path = os.path.join(tmpdir, "main.c")
                    exe_file_path = os.path.join(tmpdir, "app.out")
                    
                    with open(c_file_path, "w") as f:
                        f.write(c_output)
                    
                    # Compile
                    compile_proc = subprocess.run(
                        [compiler_path, "-O3", c_file_path, "-o", exe_file_path],
                        capture_output=True, text=True
                    )
                    
                    if compile_proc.returncode != 0:
                        st.error("GCC Compilation Failed:")
                        st.code(compile_proc.stderr)
                    else:
                        # Run binary
                        try:
                            run_proc = subprocess.run(
                                [exe_file_path],
                                capture_output=True, text=True, timeout=5
                            )
                            st.success("Program executed successfully!")
                            st.code(run_proc.stdout if run_proc.stdout else "[Program executed with no output text]")
                        except subprocess.TimeoutExpired:
                            st.error("Execution timed out (Possible infinite loop in your Macondo code).")
