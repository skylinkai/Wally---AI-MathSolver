"""Generate plain-English explanations for math solutions."""

from __future__ import annotations

import os

from models import MathSolution


def _build_solution_context(solution: MathSolution) -> str:
    steps_text = "\n\n".join(f"{s.title}\n{s.content}" for s in solution.steps)
    solutions_text = "\n".join(f"- {s}" for s in solution.solutions)
    return (
        f"Problem: {solution.normalized_expression}\n"
        f"Type: {solution.problem_type.value}\n\n"
        f"Steps:\n{steps_text}\n\n"
        f"Solutions:\n{solutions_text}\n\n"
        f"Verified: {solution.verified}\n"
        f"Verification: {solution.verification_detail}"
    )


def _template_explanation(solution: MathSolution) -> str:
    """Fallback explanation when no LLM API key is available."""
    lines = [
        f"This is a **{solution.problem_type.value}** problem.",
        "",
        "Here is how we solved it step by step:",
        "",
    ]
    for step in solution.steps:
        lines.append(f"**{step.title}**")
        lines.append(step.content)
        lines.append("")
    if solution.solutions:
        lines.append("**Final Answer**")
        for s in solution.solutions:
            lines.append(f"- x = {s}" if solution.problem_type.value != "Arithmetic" else f"- {s}")
        lines.append("")
    if solution.verified:
        lines.append("✓ The answer was verified by substituting back into the original equation.")
    return "\n".join(lines)


def explain_solution(solution: MathSolution, audience: str = "15-year-old student") -> str:
    """
    Explain a SymPy solution in plain English.
    Uses OpenAI if OPENAI_API_KEY is set; otherwise returns a template explanation.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return _template_explanation(solution)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        context = _build_solution_context(solution)
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a friendly math tutor explaining solutions to a {audience}. "
                        "Use the provided SymPy solution (which is mathematically correct). "
                        "Explain every step clearly in plain English. Use simple language. "
                        "Do not change the math — only explain it. Format with markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Explain this solution:\n\n{context}",
                },
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        return response.choices[0].message.content or _template_explanation(solution)
    except Exception:
        return _template_explanation(solution)
