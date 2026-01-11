import streamlit as st
from C_learning_gap_analyzer import analyze_c_code, feedback_engine

st.set_page_config(
    page_title="C Learning Gap Analyzer",
    layout="centered"
)

st.title("C Learning Gap Analyzer")

mode=st.radio(
    "choose question type:",
    ["Practical (Write C code)","Theory (Conceptual answer)"]
)

st.caption(
    "Rule-based semantic analyzer • Explainable feedback • Beginner-focused"
)


# ---------------- PRACTICAL MODE ----------------

if mode == "Practical (Write C code)":
    st.subheader("💻 Practical question")
    st.write(
    "👉 **Question:** Write a C Program to take two integers from the user" 
    " and display them using `printf`."
)
    code_input=st.text_area(
        "Write your C code here:",
        height=300,
        placeholder=(
            "#include <stdio.h>\n"
                "int main() {\n"
                "    int a, b;\n"
                "    scanf(\"%d %d\", &a, &b);\n"
                "    printf(\"%d %d\", a, b);\n"
                "    return 0;\n"
                "}"
        )
    )

    if st.button("Analyze Practical Answer"):
        if not code_input.strip():
            st.warning("Please input some C code before analyzing")
        else:
            raw_issues = analyze_c_code(code_input)
            feedback = feedback_engine(raw_issues)

            if not feedback:
                st.success("✅ No issues found. Good job!")
            else:
                st.subheader("🔍 Analysis Results")

                for msg in feedback:
                    if msg.startswith("Error"):
                        st.error(msg)
                    elif msg.startswith("Warning"):
                        st.warning(msg)
                    else:
                        st.info(msg)


# ---------------- THEORY MODE ----------------

if mode == "Theory (Conceptual answer)":
    st.subheader("📘 Theory Question")

    st.write(
        "👉 **Question:** Which header file is required for input and output"
        "functons in C, and why?"
    )

    answer = st.text_area(
        "Write your answer",
        height=150,
        placeholder="Example: math.h is required because pow is defined in it."
    )
    
    if st.button("Check Theory Answer"):
        keywords = ["stdio.h","printf","scanf"]
        score = sum(1 for k in keywords if k.lower() in answer.lower())

        if score == len(keywords):
            st.success("✅ Good answer. You covered the key points.")
        elif score>0:
            st.warning(
                "⚠️ Partial answer. Mention why printf/scanf require  stdio.h."
            )
        else:
            st.error(
                "❌ Incomplete answer. You did not mention the correct header file."
            )