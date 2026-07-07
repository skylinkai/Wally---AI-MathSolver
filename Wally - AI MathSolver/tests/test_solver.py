"""Tests for the AI Math Tutor solver."""

import pytest

from models import ProblemType
from text_utils import normalize_ocr_text
from solver import solve_problem, verify_solution
import sympy as sp
from sympy import Eq, symbols

x = symbols("x")


class TestNormalizeOCR:
    def test_superscript(self):
        result = normalize_ocr_text("2x\u00b2 + 5x")
        assert "2**2" in result or "**2" in result

    def test_multiplication(self):
        assert normalize_ocr_text("2x + 3") == "2*x+3"

    def test_minus_sign(self):
        assert normalize_ocr_text("5 − 3") == "5-3"


class TestQuadraticSolver:
    def test_quadratic_roots(self):
        result = solve_problem("2*x**2 + 5*x - 3 = 0")
        assert result.problem_type == ProblemType.QUADRATIC
        assert result.verified
        assert len(result.solutions) == 2
        assert len(result.steps) >= 3

    def test_simple_algebra(self):
        result = solve_problem("3*x + 5 = 20")
        assert result.problem_type == ProblemType.ALGEBRA
        assert result.verified

    def test_arithmetic(self):
        result = solve_problem("15 + 27")
        assert result.problem_type == ProblemType.ARITHMETIC
        assert result.verified


class TestVerification:
    def test_verify_quadratic(self):
        eq = Eq(2 * x**2 + 5 * x - 3, 0)
        roots = [sp.Rational(1, 2), -3]
        ok, _ = verify_solution(eq, None, roots)
        assert ok

    def test_empty_solutions(self):
        eq = Eq(x - 1, 0)
        ok, detail = verify_solution(eq, None, [])
        assert not ok
