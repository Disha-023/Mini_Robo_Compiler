# RoboLang Studio 2.0 — Web Setup & Architecture Guide

Welcome to **RoboLang Studio 2.0**, an interactive developer interface and 3D compiler playground for the **Mini Robo Compiler / RoboLang 2.0** Python compiler.

---

## 1. Architecture Overview & Backend Preservation

> **CRITICAL GUARANTEE:**
> The original Python compiler backend and Tkinter simulator were **100% preserved and untouched**.
> All original files in `compiler/`, `robot/`, `tests/`, and `main.py` remain read-only.
> All 161 existing unit tests continue to pass with 0 modifications.

```
Mini_Robo_Compiler/
│
├── compiler/                  # EXISTING — UNTOUCHED (Lexer, Parser, AST, Semantic, IR, Codegen)
├── robot/                     # EXISTING — UNTOUCHED (Robot, Executor, Simulator)
├── tests/                     # EXISTING — UNTOUCHED (161 unit tests passing)
├── main.py                    # EXISTING — UNTOUCHED
│
├── web_api/                   # NEW — FASTAPI INTEGRATION LAYER
│   ├── app.py                 # Exposes /api/health, /api/run, /api/examples
│   ├── requirements.txt       # Dependencies: fastapi, uvicorn, pydantic
│   └── __init__.py
│
├── frontend/                  # NEW — REACT + THREE.JS PLAYGROUND
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx              # Navigation, example selector, run/reset buttons, health pill
│   │   │   ├── CodeEditor.jsx          # Syntax highlighter, line numbers, shortcuts
│   │   │   ├── RobotScene.jsx          # 3D Three.js simulation, procedural rover, trails, camera controls
│   │   │   ├── RobotTelemetry.jsx      # Real-time coordinates, compass, pen state, action progress
│   │   │   ├── SimulationControls.jsx  # Play, pause, resume, replay, speed multipliers
│   │   │   ├── CompilerOutput.jsx      # Tabs: Tokens, AST, IR, Generated Python, Output, Errors
│   │   │   └── AboutModal.jsx          # Project overview & shortcuts
│   │   ├── services/
│   │   │   └── api.js                  # Fetch client connected via Vite proxy
│   │   ├── App.jsx                     # State orchestrator & layout
│   │   ├── index.css                   # Tailwind styles, glassmorphism, cyber neon accents
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js                  # Proxy configuration to http://127.0.0.1:8000
│   └── tailwind.config.js
│
├── test_web_api.py            # Automated integration test script for web_api
└── WEB_SETUP.md               # This setup and documentation file
```

---

## 2. Quickstart Instructions

### Terminal 1: Start Python FastAPI Backend

From the root project directory (`Mini_Robo_Compiler/`):

```bash
# 1. Ensure dependencies are installed
pip install fastapi uvicorn pydantic

# 2. Launch FastAPI server
python -m uvicorn web_api.app:app --host 127.0.0.1 --port 8000 --reload
```

*The backend will be live at `http://127.0.0.1:8000`. You can inspect the OpenAPI documentation at `http://127.0.0.1:8000/docs`.*

---

### Terminal 2: Start React + Vite Frontend

From the root project directory:

```bash
# 1. Change to frontend directory
cd frontend

# 2. Install dependencies (if not already installed)
npm install

# 3. Start development server
npm run dev
```

*Open your browser to `http://127.0.0.1:5173/`.*

---

## 3. Web Features

### 🖥️ 1. Left Panel — RoboLang Code Editor
- **Full Syntax Highlighting:** Keywords (`START`, `STOP`, `MOVE`, `TURN`, `LET`, `IF`, `ELSE`, `WHILE`, `REPEAT`, `FUNC`, etc.), numbers, strings, and operators.
- **Line Numbers & Gutter:** Dynamic tracking of line counts and character length.
- **Keyboard Shortcut:** Press <kbd>Ctrl + Enter</kbd> (or <kbd>Cmd + Enter</kbd>) to compile and run instantly.
- **Quick Actions:** Clear editor, Copy code, Reset program.
- **Built-in Tested Examples:**
  - Square Drawing (`REPEAT 4`)
  - Basic Movement & Coordinates
  - Variables & Arithmetic
  - Conditionals (`IF / ELSE`)
  - Outward Spiral (`WHILE`)
  - Function Definition & Calls
  - Pen Art (`PEN_DOWN` / `PEN_UP`)
  - Obstacle Sensor Check (`OBSTACLE_AHEAD`)

### 🤖 2. Center Panel — Interactive 3D Robot Simulator
- **Procedural 3D Robot Rover:** White & cyan futuristic chassis, swiveling head sensor with cyan LED visor eyes, rotating wheels, glowing forward direction arrow, antenna beacon, and headlight spot lights.
- **Glowing Neon Floor Grid:** Coordinate markings, North (+Y) cyan axis guide, East (+X) orange axis guide, and glowing launch pad at origin `(0, 0)`.
- **Dynamic Drawing Trail:** When `PEN_DOWN` is active, the robot draws a visible glowing cyan ribbon along its path. When `PEN_UP` is active, it moves without drawing.
- **Camera Controls:**
  - Orbit rotation (Left-click + drag)
  - Zoom (Scroll wheel)
  - Pan (Right-click + drag)
  - Camera presets: **Isometric**, **Top View**, **Follow Robot**.
- **Kinematic Playback Engine:**
  - Smooth interpolation between `from` and `to` coordinates.
  - Smooth 90° turns.
  - Controls: **Resume/Pause**, **Replay** (re-animates recorded history without calling the compiler backend again), **Reset Sim**, and **Speed Multiplier** (0.5x, 1x, 2x, 4x).

### 📊 3. Right Panel — Live Robot Telemetry
- Real-time **X and Y grid coordinates**.
- Rotating **Compass Needle & Direction Indicator** (`NORTH`, `EAST`, `SOUTH`, `WEST`).
- Active **Pen State** badge (`DOWN (Drawing)` vs `UP (Hover)`).
- **Speed Level** indicator.
- **Current Action** and execution progress bar.
- **Python Backend Final State Verification Badge** showing verified final coordinates and direction.

### 🔍 4. Bottom Panel — Compiler Output Tabs
- **Program Output:** Captures all standard output from `PRINT` statements and `POSITION` commands.
- **Tokens:** Filterable table showing Token Type, Lexeme Value, Line, and Column.
- **Abstract Syntax Tree (AST):** Formatted tree structure generated by the recursive descent parser.
- **Intermediate Representation (IR):** Quadruple instructions with line numbering.
- **Generated Python Code:** Exact target code generated by `CodeGenerator`.
- **Compiler Errors:** Structured error cards displaying lexical, syntax, semantic, or runtime errors with line numbers.

---

## 4. Verification and Testing

### Run All Original Python Unit Tests:
```bash
python -m unittest discover tests
```
*Expected: 161 tests pass (`OK`).*

### Run Web API Integration Test:
```bash
python test_web_api.py
```
*Expected: All endpoints and compilation stages pass.*

### Original Desktop Tkinter Simulator:
The original Tkinter GUI simulator remains fully functional:
```bash
python main.py
```
