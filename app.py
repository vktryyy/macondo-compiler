import streamlit as st
import subprocess
import tempfile
import os
import shutil

def optimize(code):
    valid = {"NEXT", "PREV", "INCR", "DECR", "ECHO", "SCAN", "LOOP", "ENDL", "NL"}
    clean_lines = [line.split('#')[0] for line in code.splitlines()]
    tokens = [t for line in clean_lines for t in line.split() if t in valid]
    
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

st.set_page_config(
    page_title="Macondo Compiler IDE", 
    page_icon="👨‍💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; height: 3em; }
    stTextArea textarea { font-family: 'Courier New', Courier, monospace; }
    </style>
""", unsafe_allow_html=True)

st.title("Macondo Compiler")
st.caption("Highly optimized Brainf***-to-C IDE & runtime written in Python.")
st.hr()

with st.sidebar:
    st.header("📖 Language Syntax")
    st.markdown("""
    **Macondo** is a verbose, highly readable mapping of Esoteric Brainf***:
    
    * `NEXT` : Move pointer right (`>`)
    * `PREV` : Move pointer left (`<`)
    * `INCR` : Increment byte (`+`)
    * `DECR` : Decrement byte (`-`)
    * `ECHO` : Output current byte (`.`)
    * `SCAN` : Input current byte (`,`)
    * `LOOP` : Start loop (`[`)
    * `ENDL` : End loop (`]`)
    * `NL`   : Print a newline character
    * `#`    : Comments are completely ignored
    """)
    st.success("⚙️ Compiler optimization rolls consecutive matching tokens automatically!")

examples = {
    "Hello World": """# Hello World in Macondo
INCR INCR INCR INCR INCR INCR INCR INCR LOOP
    NEXT INCR INCR INCR INCR LOOP
        NEXT INCR INCR NEXT INCR INCR INCR NEXT INCR INCR INCR NEXT INCR PREV PREV PREV PREV DECR
    ENDL
    NEXT INCR NEXT INCR NEXT DECR NEXT NEXT INCR LOOP PREV ENDL PREV DECR
ENDL
NEXT NEXT ECHO NEXT DECR DECR DECR ECHO INCR INCR INCR INCR INCR INCR INCR ECHO ECHO INCR INCR INCR ECHO
NEXT NEXT ECHO PREV DECR ECHO PREV ECHO INCR INCR INCR ECHO DECR DECR DECR DECR DECR DECR ECHO
DECR DECR DECR DECR DECR DECR DECR DECR ECHO NEXT NEXT INCR ECHO NEXT INCR INCR ECHO NL""",
    "Print 'A'": """# Simple program to print capital A (ASCII 65)
INCR INCR INCR INCR INCR INCR LOOP
    NEXT INCR INCR INCR INCR INCR INCR INCR INCR INCR INCR PREV DECR
ENDL
NEXT INCR INCR INCR INCR INCR ECHO NL"""
}

col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    st.subheader("🖥️ Source Code Editor")
    
    selected_example = st.selectbox("Load a sample Macondo program:", list(examples.keys()))
    
    user_code = st.text_area(
        "Write or modify your Macondo script:", 
        value=examples[selected_example], 
        height=420,
        help="Type or paste your Macondo code here. Use '#' for line comments."
    )
    
    compile_btn = st.button("🚀 Compile & Execute Program", type="primary")

with col2:
    st.subheader("📦 Build & Output Panel")
    
    tab_c, tab_run = st.tabs(["📄 Generated C Code", "🗣 Execution Output"])
    
    if user_code.strip():
        c_output = generate_c_code(user_code)
        with tab_c:
            st.code(c_output, language="c", line_numbers=True)
            
        with tab_run:
            if compile_btn:
                with st.spinner("Compiling C binary with GCC..."):
                    compiler_path = shutil.which("gcc") or shutil.which("clang")
                    
                    if not compiler_path:
                        st.error("❌ No native C compiler (gcc/clang) detected in this host environment.")
                    else:
                        with tempfile.TemporaryDirectory() as tmpdir:
                            c_file_path = os.path.join(tmpdir, "main.c")
                            exe_file_path = os.path.join(tmpdir, "app.out")
                            
                            with open(c_file_path, "w") as f:
                                f.write(c_output)
                            
                            compile_proc = subprocess.run(
                                [compiler_path, "-O3", c_file_path, "-o", exe_file_path],
                                capture_output=True, text=True
                            )
                            
                            if compile_proc.returncode != 0:
                                st.error("💥 C Compilation Error:")
                                st.code(compile_proc.stderr, language="bash")
                            else:
                                try:
                                    run_proc = subprocess.run(
                                        [exe_file_path],
                                        capture_output=True, text=True, timeout=4
                                    )
                                    st.info("💡 Program Return Status: Success")
                                    
                                    output_text = run_proc.stdout if run_proc.stdout else "[Program completed successfully with blank output]"
                                    st.code(output_text, language="text")
                                    
                                except subprocess.TimeoutExpired:
                                    st.error("⏳ Execution timed out! Your script might contain an infinite loop block.")
            else:
                st.info("Click **'Compile & Execute Program'** to run code.")
    else:
        st.warning("Please input some code in the workspace to preview compilation pipelines.")
