# AI Math Tutor

Take a photo of a math problem and get a complete, verified solution with step-by-step explanation.

**Author:** Arindam Chakraborty — [arindcha@gmail.com](mailto:arindcha@gmail.com)

## Features

- Upload or photograph a math problem
- Automatic image preprocessing (crop, deskew, contrast)
- OCR text extraction (EasyOCR on server, ML Kit on Android)
- Problem type detection (arithmetic, algebra, quadratic, calculus, and more)
- Exact symbolic solving with **SymPy** (no LLM hallucinations on answers)
- Step-by-step solution with verification
- Plain-English explanation (OpenAI optional, template fallback built in)
- Graph plotting for equations (web)
- PDF export (web)
- Native **Android app** (Kotlin + Jetpack Compose)

## Architecture

### Web app

```
Image → OpenCV preprocessing → EasyOCR → SymPy solver → LLM explainer → Streamlit UI
```

### Android app

```
Camera / Gallery → ML Kit OCR (on-device) → FastAPI → SymPy solver → Compose UI
```

| Component | Role |
|-----------|------|
| **SymPy** | Exact mathematical solutions and verification |
| **EasyOCR** | Server-side text extraction from photos |
| **ML Kit** | On-device OCR in the Android app |
| **OpenCV** | Crop, rotate, shadow removal, contrast |
| **OpenAI** | Optional plain-English explanations |
| **FastAPI** | REST API shared by the Android client |

## Quick Start (Web)

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit web app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

### Web usage

1. **Upload** a photo of a math problem, or **type** the equation directly
2. Click **Solve**
3. View the detected problem, step-by-step solution, verification, and explanation
4. Optionally **download a PDF** report

### Example

Input: `2*x**2 + 5*x - 3 = 0`

Output:

- Problem Type: Quadratic Equation
- Step 1: a = 2, b = 5, c = -3
- Step 2: Discriminant = 49
- Step 3: x = (-5 ± 7) / 4
- Solutions: x = 1/2, x = -3
- Verification ✓

## Quick Start (Android)

**Prerequisites:** [Android Studio](https://developer.android.com/studio), Python 3.10+

```powershell
# Terminal 1 — start the API server
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Then open the `android/` folder in Android Studio and run on an emulator or device.

| Device | API server URL (in app Settings) |
|--------|----------------------------------|
| Android Emulator | `http://10.0.2.2:8000` |
| Physical phone | `http://YOUR_PC_LAN_IP:8000` |

Phone and PC must be on the same Wi‑Fi network. Full Android setup: **[android/README.md](android/README.md)**

## API Server

The FastAPI backend powers the Android app and can be used standalone.

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Interactive docs: http://localhost:8000/docs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server health check |
| POST | `/solve` | Solve from equation string |
| POST | `/ocr` | Extract text from image |
| POST | `/solve-image` | OCR + solve in one request |

**Example — solve an equation:**

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d "{\"equation\": \"2*x**2 + 5*x - 3 = 0\", \"explain\": true}"
```

## Optional: LLM Explanations

Set your OpenAI API key for richer explanations:

```bash
set OPENAI_API_KEY=sk-...     # Windows
export OPENAI_API_KEY=sk-...  # macOS/Linux
```

Without an API key, the app uses a built-in template explanation.

## Project Structure

```
├── app.py              # Streamlit web UI
├── api.py              # FastAPI backend (Android + REST clients)
├── solver.py           # SymPy solver + verification
├── explainer.py        # LLM / template explanations
├── ocr.py              # EasyOCR text extraction
├── image_utils.py      # OpenCV preprocessing
├── text_utils.py       # OCR text normalization
├── models.py           # Shared data models
├── pyproject.toml      # Python package metadata
├── AUTHORS.md          # Author information
├── requirements.txt
├── android/            # Kotlin + Jetpack Compose Android app
├── assets/
└── tests/
```

## Supported Problem Types

| Type | Examples |
|------|----------|
| Arithmetic | `15 + 27 * 3` |
| Algebra | `3*x + 5 = 20` |
| Quadratic | `2*x**2 + 5*x - 3 = 0` |
| Calculus | `derivative(x**2 + 3*x)` |
| Geometry | Keyword detection |
| Statistics | Keyword detection |

## Tests

```bash
pip install pytest
pytest tests/ -v
```

## Roadmap (v2)

- [x] Android app (Kotlin + Compose)
- [ ] Canvas drawing input
- [ ] Voice narration
- [ ] Quiz mode with hints
- [ ] Multi-problem worksheet detection
- [ ] LaTeX rendering with MathJax
- [ ] Similar practice questions (Easy / Medium / Hard)
- [ ] Cloud API deployment (Railway / Render)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web UI | Streamlit |
| Android UI | Jetpack Compose |
| API | FastAPI + Uvicorn |
| Mobile OCR | Google ML Kit |
| Server OCR | EasyOCR |
| Computer vision | OpenCV |
| Solver | SymPy |
| Explanation | OpenAI (optional) |
| Graphs | Matplotlib |
| PDF export | fpdf2 |
| Android networking | Retrofit |
| Android storage | DataStore |

## License

See [AUTHORS.md](AUTHORS.md) for author and contact details.
