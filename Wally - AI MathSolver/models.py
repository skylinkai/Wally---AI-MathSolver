"""Data models for the AI Math Tutor."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProblemType(str, Enum):
    ARITHMETIC = "Arithmetic"
    ALGEBRA = "Algebra"
    QUADRATIC = "Quadratic Equation"
    CALCULUS = "Calculus"
    GEOMETRY = "Geometry"
    STATISTICS = "Statistics"
    UNKNOWN = "Unknown"


@dataclass
class SolutionStep:
    title: str
    content: str


@dataclass
class MathSolution:
    problem_type: ProblemType
    original_expression: str
    normalized_expression: str
    steps: list[SolutionStep] = field(default_factory=list)
    solutions: list[str] = field(default_factory=list)
    verified: bool = False
    verification_detail: str = ""
    sympy_result: Any = None
    graph_expression: str | None = None


@dataclass
class OCRResult:
    raw_text: str
    confidence: float
    cropped_image: Any = None
