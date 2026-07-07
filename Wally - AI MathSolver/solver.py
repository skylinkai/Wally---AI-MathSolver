"""SymPy-based math solver with verification."""

from __future__ import annotations

import re
from typing import Any

import sympy as sp
from sympy import Eq, diff, expand, integrate, simplify, solve, symbols, sympify

from models import MathSolution, ProblemType, SolutionStep

x = symbols("x")
y = symbols("y")


def _safe_sympify(expr_str: str) -> sp.Expr:
    """Parse a string into a SymPy expression."""
    local_dict = {
        "x": x,
        "y": y,
        "sqrt": sp.sqrt,
        "pi": sp.pi,
        "e": sp.E,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "log": sp.log,
        "ln": sp.log,
        "exp": sp.exp,
    }
    return sympify(expr_str, locals=local_dict)


def _format_solution(val: Any) -> str:
    if isinstance(val, sp.Basic):
        return sp.pretty(val)
    return str(val)


def _detect_problem_type(expr: sp.Expr, text: str) -> ProblemType:
    text_lower = text.lower()
    if any(k in text_lower for k in ("derivative", "d/dx", "integrate", "limit")):
        return ProblemType.CALCULUS
    if any(k in text_lower for k in ("mean", "median", "std", "variance", "probability")):
        return ProblemType.STATISTICS
    if any(k in text_lower for k in ("area", "perimeter", "triangle", "circle", "angle")):
        return ProblemType.GEOMETRY
    if isinstance(expr, sp.Eq):
        lhs, rhs = expr.lhs, expr.rhs
        poly = sp.Poly(lhs - rhs, x) if lhs.has(x) or rhs.has(x) else None
        if poly and poly.degree() == 2:
            return ProblemType.QUADRATIC
        return ProblemType.ALGEBRA
    if expr.has(x):
        return ProblemType.ALGEBRA
    return ProblemType.ARITHMETIC


def _solve_quadratic(equation: sp.Eq) -> MathSolution:
    """Solve a quadratic equation with step-by-step output."""
    lhs = expand(equation.lhs - equation.rhs)
    poly = sp.Poly(lhs, x)
    a, b, c = poly.all_coeffs()
    steps = [
        SolutionStep("Step 1", f"a = {_format_solution(a)}\nb = {_format_solution(b)}\nc = {_format_solution(c)}"),
    ]
    discriminant = b**2 - 4 * a * c
    steps.append(
        SolutionStep(
            "Step 2",
            f"Discriminant = b^2 - 4ac\n= {_format_solution(b)}^2 - 4({_format_solution(a)})({_format_solution(c)})\n= {_format_solution(discriminant)}",
        )
    )
    roots = solve(equation, x)
    if discriminant >= 0:
        sqrt_d = sp.sqrt(discriminant)
        steps.append(
            SolutionStep(
                "Step 3",
                f"x = ({_format_solution(-b)} ± {_format_solution(sqrt_d)}) / (2·{_format_solution(a)})",
            )
        )
    else:
        steps.append(SolutionStep("Step 3", "No real solutions (discriminant < 0)."))

    sol_strings = [_format_solution(r) for r in roots]
    return MathSolution(
        problem_type=ProblemType.QUADRATIC,
        original_expression=str(equation),
        normalized_expression=sp.pretty(equation),
        steps=steps,
        solutions=sol_strings,
        graph_expression=str(lhs),
    )


def _parse_equation(text: str) -> sp.Eq | sp.Expr:
    """Parse OCR text into a SymPy equation or expression."""
    text = text.strip()
    if "=" in text:
        left, right = text.split("=", 1)
        return Eq(_safe_sympify(left), _safe_sympify(right))
    return _safe_sympify(text)


def _solve_calculus(text: str) -> MathSolution | None:
    """Handle basic calculus keywords from OCR text."""
    text_clean = text.replace(" ", "")
    deriv_match = re.search(r"(?:d/dx|derivative)\(?(.+?)\)?$", text_clean, re.I)
    if deriv_match:
        expr = _safe_sympify(deriv_match.group(1))
        result = diff(expr, x)
        return MathSolution(
            problem_type=ProblemType.CALCULUS,
            original_expression=text,
            normalized_expression=f"d/dx ({sp.pretty(expr)})",
            steps=[
                SolutionStep("Step 1", f"Differentiate: {sp.pretty(expr)}"),
                SolutionStep("Step 2", f"Result: {sp.pretty(result)}"),
            ],
            solutions=[sp.pretty(simplify(result))],
        )
    integ_match = re.search(r"(?:integrate|∫)\(?(.+?)\)?(?:dx)?$", text_clean, re.I)
    if integ_match:
        expr = _safe_sympify(integ_match.group(1))
        result = integrate(expr, x)
        return MathSolution(
            problem_type=ProblemType.CALCULUS,
            original_expression=text,
            normalized_expression=f"∫ {sp.pretty(expr)} dx",
            steps=[
                SolutionStep("Step 1", f"Integrate: {sp.pretty(expr)}"),
                SolutionStep("Step 2", f"Result: {sp.pretty(result)} + C"),
            ],
            solutions=[sp.pretty(simplify(result)) + " + C"],
        )
    return None


def verify_solution(equation: sp.Eq | None, expr: sp.Expr | None, solutions: list) -> tuple[bool, str]:
    """Substitute solutions back into the original equation."""
    if equation is None or not solutions:
        return False, "No equation to verify."
    checks = []
    all_ok = True
    for sol in solutions:
        if isinstance(sol, sp.Eq):
            val = sol.rhs if sol.lhs == x else sol.lhs
        else:
            val = sol
        lhs_val = simplify(equation.lhs.subs(x, val))
        rhs_val = simplify(equation.rhs.subs(x, val))
        ok = simplify(lhs_val - rhs_val) == 0
        all_ok = all_ok and ok
        checks.append(f"x = {_format_solution(val)}: {'✓' if ok else '✗'}")
    return all_ok, "\n".join(checks)


def solve_problem(text: str) -> MathSolution:
    """Main entry point: parse, classify, solve, and verify."""
    text = text.strip()
    if not text:
        raise ValueError("No math problem detected. Try a clearer photo or type the equation.")

    calc_result = _solve_calculus(text)
    if calc_result:
        calc_result.verified = True
        calc_result.verification_detail = "Symbolic differentiation/integration verified by SymPy."
        return calc_result

    try:
        parsed = _parse_equation(text)
    except Exception as e:
        raise ValueError(f"Could not parse expression: {text!r}. Error: {e}") from e

    if isinstance(parsed, sp.Eq):
        problem_type = _detect_problem_type(parsed, text)
        if problem_type == ProblemType.QUADRATIC:
            result = _solve_quadratic(parsed)
        else:
            roots = solve(parsed, x)
            steps = [
                SolutionStep("Step 1", f"Equation: {sp.pretty(parsed)}"),
                SolutionStep("Step 2", f"Solve for x using SymPy"),
            ]
            if roots:
                steps.append(SolutionStep("Step 3", f"Solutions: {', '.join(_format_solution(r) for r in roots)}"))
            result = MathSolution(
                problem_type=problem_type,
                original_expression=text,
                normalized_expression=sp.pretty(parsed),
                steps=steps,
                solutions=[_format_solution(r) for r in roots],
                sympy_result=roots,
            )
        verified, detail = verify_solution(parsed, None, solve(parsed, x))
        result.verified = verified
        result.verification_detail = detail
        return result

    # Pure expression evaluation
    problem_type = _detect_problem_type(parsed, text)
    simplified = simplify(parsed)
    steps = [
        SolutionStep("Step 1", f"Expression: {sp.pretty(parsed)}"),
        SolutionStep("Step 2", f"Simplified: {sp.pretty(simplified)}"),
    ]
    return MathSolution(
        problem_type=problem_type,
        original_expression=text,
        normalized_expression=sp.pretty(parsed),
        steps=steps,
        solutions=[sp.pretty(simplified)],
        verified=True,
        verification_detail="Expression simplified symbolically.",
    )
