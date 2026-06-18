# macondo-compiler
A compiler/transpiler written in Python that turns a Brainf***-like language (Macondo) into highly optimized C.

If you would like to try a quick little demo, head over to https://macondo-compiler-v3.streamlit.app/

(AI NOTICE: the only file that contains ANY sort of AI generated or assisted code incldudes the 'app.py' file over in the 'streamlit' branch to provide the styling and frontend of the website with my own polish inlcuded)

Command Reference:

NEXT - Moves the memory pointer one cell to the right. (Like > in Brainf***)

PREV - Moves the memory pointer one cell to the left. (Like < in Brainf***)

INCR - Adds 1 to the value at the current memory cell. (Like + in Brainf***)

DECR - Subtracts 1 from the value at the current memory cell. (Like - in Brainf***)

ECHO - Prints the ASCII character of the current cell to the screen. (Like . in Brainf***)

SCAN - Takes a single character of input from the user. (Like , in Brainf***)

LOOP - Starts a loop. If the current cell is 0, skips to the matching ENDL. (Like [ in Brainf***)

ENDL - Ends a loop. If the current cell isn't 0, jumps back to the matching LOOP. (Like ] in Brainf***)

NL - A custom shortcut that instantly prints a newline character (\n).

Comments/#: Anything after a # is ignored by the compiler, so you can use it to write notes and track your math.

<img width="1828" height="230" alt="program" src="https://github.com/user-attachments/assets/37806b55-48be-4237-9ddb-af24bbc25257" />
