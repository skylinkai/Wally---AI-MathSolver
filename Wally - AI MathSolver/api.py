"""FastAPI backend for the Android Math Tutor client."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from explainer import explain_solution
from models import MathSolution
from solver import solve_problem

app = FastAPI(
    title="AI Math Tutor API",
    description="SymPy-powered math solver for the Android app",
    version="1.0.0",
    contact={
        "name": "Arindam Chakraborty",
        "email": "arindcha@gmail.com",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class StepResponse(BaseModel):
    title: str
    content: str


class SolveRequest(BaseModel):
    equation: str = Field(..., min_length=1, description="Math equation or expression")
    explain: bool = Field(True, description="Include plain-English explanation")


class SolveResponse(BaseModel):
    problem_type: str
    detected_problem: str
    normalized_expression: str
    steps: list[StepResponse]
    solutions: list[str]
    verified: bool
    verification_detail: str
    explanation: str = ""


class OCRResponse(BaseModel):
    text: str
    confidence: float


def _solution_to_response(solution: MathSolution, explain: bool) -> SolveResponse:
    explanation = explain_solution(solution) if explain else ""
    return SolveResponse(
        problem_type=solution.problem_type.value,
        detected_problem=solution.original_expression,
        normalized_expression=solution.normalized_expression,
        steps=[StepResponse(title=s.title, content=s.content) for s in solution.steps],
        solutions=solution.solutions,
        verified=solution.verified,
        verification_detail=solution.verification_detail,
        explanation=explanation,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/solve", response_model=SolveResponse)
def solve(req: SolveRequest) -> SolveResponse:
    try:
        solution = solve_problem(req.equation.strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Solver error: {e}") from e
    return _solution_to_response(solution, req.explain)


@app.post("/ocr", response_model=OCRResponse)
async def ocr_image(file: UploadFile = File(...)) -> OCRResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Upload a valid image file.")
    data = await file.read()
    try:
        from ocr import extract_text_from_bytes

        result = extract_text_from_bytes(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OCR failed: {e}") from e
    return OCRResponse(text=result.raw_text, confidence=result.confidence)


@app.post("/solve-image", response_model=SolveResponse)
async def solve_image(
    file: UploadFile = File(...),
    explain: bool = True,
) -> SolveResponse:
    data = await file.read()
    try:
        from ocr import extract_text_from_bytes

        ocr_result = extract_text_from_bytes(data)
        solution = solve_problem(ocr_result.raw_text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return _solution_to_response(solution, explain)
