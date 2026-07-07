"""Streamlit UI for the AI Math Tutor."""

from __future__ import annotations

import io
from datetime import datetime

import matplotlib.pyplot as plt
import streamlit as st
import sympy as sp

from explainer import explain_solution
from image_utils import load_image, preprocess_for_ocr
from models import ProblemType
from ocr import extract_text_from_bytes, extract_text_from_image
from solver import solve_problem

st.set_page_config(
    page_title="AI Math Tutor",
    page_icon="📐",
    layout="wide",
)

st.title("📐 AI Math Tutor")
st.caption("Take a photo of a math problem — get a complete, verified solution with step-by-step explanation.")

col_upload, col_manual = st.columns(2)

with col_upload:
    uploaded = st.file_uploader(
        "Upload or take a picture",
        type=["png", "jpg", "jpeg", "webp"],
        help="Upload a photo of a handwritten or printed math problem.",
    )

with col_manual:
    manual_input = st.text_input(
        "Or type the equation directly",
        placeholder="e.g. 2x**2 + 5*x - 3 = 0",
    )

detected_text = manual_input.strip()

if uploaded is not None:
    file_bytes = uploaded.read()
    try:
        image = load_image(file_bytes)
        cropped, binary = preprocess_for_ocr(image)

        preview_col1, preview_col2 = st.columns(2)
        with preview_col1:
            st.image(cropped, caption="Detected & cropped region", use_container_width=True)
        with preview_col2:
            st.image(binary, caption="Preprocessed for OCR", use_container_width=True)

        with st.spinner("Extracting text with OCR..."):
            ocr_result = extract_text_from_bytes(file_bytes)
            detected_text = ocr_result.raw_text
            st.info(f"OCR confidence: {ocr_result.confidence:.0%}")
    except Exception as e:
        st.error(f"Image processing failed: {e}")

if detected_text:
    st.divider()
    st.subheader("Detected Problem")
    st.code(detected_text, language=None)

    if st.button("Solve", type="primary", use_container_width=True):
        try:
            with st.spinner("Solving with SymPy..."):
                solution = solve_problem(detected_text)

            st.divider()
            st.subheader("Problem Type")
            st.markdown(f"**{solution.problem_type.value}**")

            st.divider()
            st.subheader("Solution")
            for step in solution.steps:
                st.markdown(f"**{step.title}**")
                st.text(step.content)

            if solution.solutions:
                st.markdown("**Solutions**")
                for sol in solution.solutions:
                    st.markdown(f"- `{sol}`")

            st.divider()
            st.subheader("Verification")
            if solution.verified:
                st.success(f"✓ Verified\n\n{solution.verification_detail}")
            else:
                st.warning(f"Could not fully verify.\n\n{solution.verification_detail}")

            with st.spinner("Generating explanation..."):
                explanation = explain_solution(solution)
            st.divider()
            st.subheader("Explanation")
            st.markdown(explanation)

            if solution.graph_expression and solution.problem_type in (
                ProblemType.QUADRATIC,
                ProblemType.ALGEBRA,
            ):
                st.divider()
                st.subheader("Graph")
                try:
                    x_sym = sp.symbols("x")
                    expr = sp.sympify(solution.graph_expression)
                    f = sp.lambdify(x_sym, expr, "numpy")
                    import numpy as np

                    xs = np.linspace(-10, 10, 400)
                    ys = f(xs)
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.plot(xs, ys, "b-", linewidth=2)
                    ax.axhline(0, color="k", linewidth=0.5)
                    ax.axvline(0, color="k", linewidth=0.5)
                    ax.set_xlabel("x")
                    ax.set_ylabel("y")
                    ax.set_title(f"y = {solution.graph_expression}")
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
                    plt.close(fig)
                except Exception:
                    pass

            st.divider()
            if st.button("Download PDF Report"):
                try:
                    from fpdf import FPDF

                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Helvetica", size=12)
                    pdf.cell(0, 10, "AI Math Tutor - Solution Report", ln=True)
                    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
                    pdf.ln(5)
                    pdf.set_font("Helvetica", "B", 12)
                    pdf.cell(0, 10, "Problem", ln=True)
                    pdf.set_font("Helvetica", size=11)
                    pdf.multi_cell(0, 8, detected_text)
                    pdf.ln(3)
                    pdf.set_font("Helvetica", "B", 12)
                    pdf.cell(0, 10, f"Type: {solution.problem_type.value}", ln=True)
                    pdf.ln(3)
                    for step in solution.steps:
                        pdf.set_font("Helvetica", "B", 11)
                        pdf.cell(0, 8, step.title, ln=True)
                        pdf.set_font("Helvetica", size=10)
                        pdf.multi_cell(0, 7, step.content)
                        pdf.ln(2)
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.cell(0, 8, "Solutions", ln=True)
                    pdf.set_font("Helvetica", size=10)
                    for sol in solution.solutions:
                        pdf.cell(0, 7, f"  {sol}", ln=True)
                    pdf.ln(3)
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.cell(0, 8, "Explanation", ln=True)
                    pdf.set_font("Helvetica", size=10)
                    clean_exp = explanation.replace("**", "").replace("✓", "OK")
                    pdf.multi_cell(0, 7, clean_exp)
                    buf = io.BytesIO()
                    pdf.output(buf)
                    st.download_button(
                        "Save PDF",
                        data=buf.getvalue(),
                        file_name="math_solution.pdf",
                        mime="application/pdf",
                    )
                except ImportError:
                    st.warning("Install fpdf2 for PDF export: pip install fpdf2")

        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An error occurred: {e}")

else:
    st.info("Upload an image or type an equation to get started.")

    with st.expander("Try an example"):
        st.code("2*x**2 + 5*x - 3 = 0", language=None)
        st.markdown(
            """
            **Expected output:**
            - Problem Type: Quadratic Equation
            - Solutions: x = 1/2, x = -3
            - Step-by-step discriminant method
            - Verification ✓
            """
        )

st.divider()
st.caption("Powered by SymPy (exact math) + EasyOCR + optional OpenAI (explanations)")
