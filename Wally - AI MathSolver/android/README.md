# Android App — AI Math Tutor

Native Android app (Kotlin + Jetpack Compose) that connects to the Python SymPy backend.

## Architecture

```
┌─────────────────────┐         HTTP          ┌──────────────────────┐
│   Android App       │  ──────────────────►  │  FastAPI (api.py)    │
│                     │                       │                      │
│  • Camera / Gallery │                       │  • SymPy solver      │
│  • ML Kit OCR       │                       │  • EasyOCR (server)  │
│  • Compose UI       │  ◄──────────────────  │  • LLM explainer     │
└─────────────────────┘      JSON response    └──────────────────────┘
```

- **On-device**: ML Kit reads text from photos (fast, works offline for OCR)
- **Server**: SymPy solves and verifies exactly (same logic as the web app)

## Prerequisites

- [Android Studio](https://developer.android.com/studio) (Hedgehog or newer)
- Python 3.10+ with project dependencies installed
- Android phone or emulator (API 26+)

## 1. Start the API server

From the project root:

```powershell
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Verify: open http://localhost:8000/docs

## 2. Open the Android project

1. Open Android Studio → **Open** → select the `android/` folder
2. Wait for Gradle sync to finish
3. Run on an emulator or connected phone

## 3. Configure server URL

| Device | Server URL |
|--------|------------|
| Android Emulator | `http://10.0.2.2:8000` (default) |
| Physical phone | `http://YOUR_PC_LAN_IP:8000` |

Find your PC IP: `ipconfig` → look for IPv4 (e.g. `192.168.1.42`)

Phone and PC must be on the **same Wi‑Fi network**.

In the app: tap **Settings** (gear icon) → enter URL → **Save** → **Test**.

## 4. Use the app

1. **Camera** or **Gallery** — take/select a photo of a math problem
2. ML Kit extracts the equation (editable in the text field)
3. Tap **Solve** — SymPy returns steps, answers, and verification
4. Or type an equation directly (e.g. `2*x**2 + 5*x - 3 = 0`)

## Build APK

In Android Studio: **Build → Build Bundle(s) / APK(s) → Build APK(s)**

Output: `android/app/build/outputs/apk/debug/app-debug.apk`

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Server status |
| POST | `/solve` | `{"equation": "3*x+5=20", "explain": true}` |
| POST | `/ocr` | Upload image → extracted text |
| POST | `/solve-image` | Upload image → full solve pipeline |

## Project layout

```
android/
├── app/src/main/java/com/wally/mathtutor/
│   ├── MainActivity.kt
│   ├── data/           # Retrofit API + settings
│   ├── ocr/            # ML Kit + text normalization
│   └── ui/             # Compose screens + ViewModel
└── app/build.gradle.kts
```

## Troubleshooting

**"Cannot reach server"**
- API running? `uvicorn api:app --host 0.0.0.0 --port 8000`
- Correct URL in Settings?
- Windows Firewall: allow port 8000 for private networks

**OCR reads wrong text**
- Use clearer photos, good lighting
- Edit the equation manually before tapping Solve
- For best OCR accuracy, use server `/solve-image` (EasyOCR) — can be added as a toggle

**Emulator can't connect**
- Use `10.0.2.2`, not `localhost`

## Production deployment

Deploy `api.py` to Railway, Render, or Fly.io, then set the app Server URL to your HTTPS endpoint. Remove cleartext HTTP from `network_security_config.xml` for release builds.

## Why not pure on-device Python?

SymPy + EasyOCR + OpenCV on Android would require Chaquopy (~50MB+ APK) and PyTorch for EasyOCR. The API approach keeps the APK small (~15MB), reuses your Python solver, and is easier to maintain.
