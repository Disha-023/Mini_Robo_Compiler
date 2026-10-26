import io
import sys
import traceback
from contextlib import redirect_stdout
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# IMPORT EXISTING COMPILER MODULES - STRICTLY UNTOUCHED
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.ir import IRGenerator
from compiler.codegen import CodeGenerator
from robot.executor import RobotExecutor
from robot.robot import Robot


app = FastAPI(
    title="RoboLang Studio API",
    description="Backend API exposing the RoboLang 2.0 Python compiler and robot simulation engine",
    version="2.0.0",
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all local dev origins (e.g. Vite on 5173, etc.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    source: str = Field(..., max_length=50000, description="RoboLang source code")


def serialize_ast(node: Any) -> Any:
    """Recursively convert AST nodes into a JSON-friendly dict structure."""
    if node is None:
        return None
    if isinstance(node, (int, float, str, bool)):
        return node
    if isinstance(node, (list, tuple)):
        return [serialize_ast(item) for item in node]
    if hasattr(node, "__dict__"):
        result = {"_type": node.__class__.__name__}
        for k, v in node.__dict__.items():
            result[k] = serialize_ast(v)
        return result
    return str(node)


def make_json_safe(obj: Any) -> Any:
    """Ensure all nested structures (including tuples from history) are JSON serializable."""
    if isinstance(obj, tuple):
        return [make_json_safe(x) for x in obj]
    if isinstance(obj, list):
        return [make_json_safe(x) for x in obj]
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    return str(obj)


SAMPLE_PROGRAMS = {
    "square": {
        "title": "Square Drawing (REPEAT Loop)",
        "description": "Uses REPEAT 4 with PEN_DOWN to draw a complete square.",
        "code": """START
PEN_DOWN
REPEAT 4 {
    MOVE 4
    TURN RIGHT
}
PEN_UP
POSITION
STOP"""
    },
    "basic_movement": {
        "title": "Basic Movement",
        "description": "Moves forward, turns, moves again, and reports final position.",
        "code": """START
PEN_DOWN
MOVE 5
TURN RIGHT
MOVE 3
PEN_UP
MOVE 2
POSITION
STOP"""
    },
    "variables": {
        "title": "Variables & Arithmetic",
        "description": "Declares variables, performs arithmetic operations, and uses them in commands.",
        "code": """START
LET side = 3
LET multiplier = 2
LET total_steps = side * multiplier
SPEED 2
PEN_DOWN
MOVE total_steps
TURN LEFT
MOVE side
PEN_UP
POSITION
STOP"""
    },
    "if_else": {
        "title": "Conditionals (IF / ELSE)",
        "description": "Evaluates conditional expressions and executes branches.",
        "code": """START
LET speed_mode = 2
IF speed_mode > 1 {
    PRINT "High speed navigation"
    SPEED 2
    PEN_DOWN
    MOVE 6
} ELSE {
    PRINT "Standard navigation"
    SPEED 1
    PEN_DOWN
    MOVE 3
}
TURN RIGHT
MOVE 2
PEN_UP
STOP"""
    },
    "while_loop": {
        "title": "WHILE Loop Spiral",
        "description": "Uses a WHILE loop with increasing steps to create an outward spiral.",
        "code": """START
LET steps = 1
PEN_DOWN
WHILE steps <= 5 {
    MOVE steps
    TURN RIGHT
    steps = steps + 1
}
PEN_UP
POSITION
STOP"""
    },
    "functions": {
        "title": "Function Definition & Calls",
        "description": "Defines a reusable geometric function and calls it with parameters.",
        "code": """START
FUNC draw_corner(length) {
    MOVE length
    TURN RIGHT
    MOVE length
}

PEN_DOWN
draw_corner(3)
TURN RIGHT
draw_corner(3)
PEN_UP
POSITION
STOP"""
    },
    "pen_art": {
        "title": "Pen UP / DOWN Stitched Line",
        "description": "Toggles the pen to draw a dashed path on the ground.",
        "code": """START
REPEAT 3 {
    PEN_DOWN
    MOVE 3
    PEN_UP
    MOVE 2
}
POSITION
STOP"""
    },
    "obstacle_avoidance": {
        "title": "Obstacle Sensor Check",
        "description": "Checks the robot's OBSTACLE_AHEAD sensor and branches accordingly.",
        "code": """START
IF OBSTACLE_AHEAD {
    PRINT "Obstacle detected ahead! Reversing..."
    BACK 2
    TURN RIGHT
} ELSE {
    PRINT "Path is clear. Proceeding forward."
    PEN_DOWN
    MOVE 4
    PEN_UP
}
POSITION
STOP"""
    }
}


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "version": "2.0.0",
        "service": "RoboLang Studio API",
        "compiler": "Mini Robo Compiler (RoboLang 2.0)",
    }


@app.get("/api/examples")
def get_examples():
    return {"examples": SAMPLE_PROGRAMS}


@app.post("/api/run")
def run_robolang(payload: RunRequest):
    source = payload.source
    if not source or not source.strip():
        return {
            "success": False,
            "tokens": [],
            "ast": None,
            "ir": [],
            "ir_formatted": [],
            "generated_code": [],
            "generated_code_raw": "",
            "output": "",
            "robot_history": [],
            "final_state": None,
            "errors": ["Source code cannot be empty."],
        }

    tokens_data: List[Dict[str, Any]] = []
    ast_data: Optional[Dict[str, Any]] = None
    ir_data: List[Any] = []
    ir_formatted: List[str] = []
    generated_code_lines: List[str] = []
    generated_code_raw = ""
    output_log = ""
    history_data: List[Dict[str, Any]] = []
    final_state = None
    errors: List[str] = []

    # Capture all stdout from compilation and execution
    stdout_buffer = io.StringIO()

    try:
        with redirect_stdout(stdout_buffer):
            # 1. Lexical Analysis
            try:
                lexer = Lexer(source)
                tokens = lexer.tokenize()
                for t in tokens:
                    tokens_data.append({
                        "type": t.token_type,
                        "value": str(t.value),
                        "line": t.line,
                        "column": t.column,
                    })
            except Exception as e:
                errors.append(f"Lexical Error: {str(e)}")
                return {
                    "success": False,
                    "tokens": tokens_data,
                    "ast": None,
                    "ir": [],
                    "ir_formatted": [],
                    "generated_code": [],
                    "generated_code_raw": "",
                    "output": stdout_buffer.getvalue(),
                    "robot_history": [],
                    "final_state": None,
                    "errors": errors,
                }

            # 2. Syntax Analysis & AST Construction
            try:
                parser = Parser(tokens)
                ast = parser.parse()
                ast_data = serialize_ast(ast)
            except Exception as e:
                errors.append(f"Syntax Error: {str(e)}")
                return {
                    "success": False,
                    "tokens": tokens_data,
                    "ast": None,
                    "ir": [],
                    "ir_formatted": [],
                    "generated_code": [],
                    "generated_code_raw": "",
                    "output": stdout_buffer.getvalue(),
                    "robot_history": [],
                    "final_state": None,
                    "errors": errors,
                }

            # 3. Semantic Analysis
            try:
                analyzer = SemanticAnalyzer()
                analyzer.analyze(ast)
            except Exception as e:
                errors.append(f"Semantic Error: {str(e)}")
                return {
                    "success": False,
                    "tokens": tokens_data,
                    "ast": ast_data,
                    "ir": [],
                    "ir_formatted": [],
                    "generated_code": [],
                    "generated_code_raw": "",
                    "output": stdout_buffer.getvalue(),
                    "robot_history": [],
                    "final_state": None,
                    "errors": errors,
                }

            # 4. Intermediate Representation Generation
            try:
                ir_gen = IRGenerator()
                instructions = ir_gen.generate(ast)
                ir_data = [list(instr) if isinstance(instr, (list, tuple)) else instr for instr in instructions]
                ir_formatted = [
                    " ".join(str(elem) for elem in instr) if isinstance(instr, (list, tuple)) else str(instr)
                    for instr in instructions
                ]
            except Exception as e:
                errors.append(f"IR Generation Error: {str(e)}")
                return {
                    "success": False,
                    "tokens": tokens_data,
                    "ast": ast_data,
                    "ir": [],
                    "ir_formatted": [],
                    "generated_code": [],
                    "generated_code_raw": "",
                    "output": stdout_buffer.getvalue(),
                    "robot_history": [],
                    "final_state": None,
                    "errors": errors,
                }

            # 5. Target Code Generation (Python)
            try:
                code_gen = CodeGenerator()
                generated_code_lines = code_gen.generate(instructions)
                generated_code_raw = "\n".join(generated_code_lines)
            except Exception as e:
                errors.append(f"Code Generation Error: {str(e)}")
                return {
                    "success": False,
                    "tokens": tokens_data,
                    "ast": ast_data,
                    "ir": ir_data,
                    "ir_formatted": ir_formatted,
                    "generated_code": [],
                    "generated_code_raw": "",
                    "output": stdout_buffer.getvalue(),
                    "robot_history": [],
                    "final_state": None,
                    "errors": errors,
                }

            # 6. Robot Execution
            try:
                executor = RobotExecutor()
                executor.execute(instructions)
                robot = executor.robot

                history_data = make_json_safe(robot.history)
                final_state = {
                    "x": robot.x,
                    "y": robot.y,
                    "direction": robot.direction,
                    "pen_down": robot.pen_down_state,
                    "speed": robot.speed_val,
                }
            except Exception as e:
                errors.append(f"Execution Error: {str(e)}")
                return {
                    "success": False,
                    "tokens": tokens_data,
                    "ast": ast_data,
                    "ir": ir_data,
                    "ir_formatted": ir_formatted,
                    "generated_code": generated_code_lines,
                    "generated_code_raw": generated_code_raw,
                    "output": stdout_buffer.getvalue(),
                    "robot_history": history_data,
                    "final_state": final_state,
                    "errors": errors,
                }

        output_log = stdout_buffer.getvalue()

        return {
            "success": True,
            "tokens": tokens_data,
            "ast": ast_data,
            "ir": ir_data,
            "ir_formatted": ir_formatted,
            "generated_code": generated_code_lines,
            "generated_code_raw": generated_code_raw,
            "output": output_log,
            "robot_history": history_data,
            "final_state": final_state,
            "errors": [],
        }

    except Exception as unexpected_err:
        return {
            "success": False,
            "tokens": tokens_data,
            "ast": ast_data,
            "ir": ir_data,
            "ir_formatted": ir_formatted,
            "generated_code": generated_code_lines,
            "generated_code_raw": generated_code_raw,
            "output": stdout_buffer.getvalue(),
            "robot_history": history_data,
            "final_state": final_state,
            "errors": [f"Unexpected Server Error: {str(unexpected_err)}"],
        }
