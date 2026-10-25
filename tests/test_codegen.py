import unittest

from compiler.codegen import CodeGenerator


class MockRobot:
    def __init__(self):
        self.log = []
        self.x = 0
        self.y = 0

    def move(self, steps):
        self.log.append(f"move({steps})")

    def back(self, steps):
        self.log.append(f"back({steps})")

    def turn_left(self):
        self.log.append("turn_left()")

    def turn_right(self):
        self.log.append("turn_right()")

    def speed(self, val):
        self.log.append(f"speed({val})")

    def pen_up(self):
        self.log.append("pen_up()")

    def pen_down(self):
        self.log.append("pen_down()")

    def position(self):
        self.log.append("position()")

    def obstacle_ahead(self):
        return False


class TestCodeGenerator(unittest.TestCase):

    def setUp(self):
        self.codegen = CodeGenerator()

    # Backwards compatibility
    def test_backwards_compatibility(self):
        instructions = [
            ("MOVE", 3),
            ("TURN", "RIGHT"),
            ("MOVE", 5),
            ("TURN", "LEFT"),
        ]
        code = self.codegen.generate(instructions)
        self.assertEqual(code, [
            "robot.move(3)",
            "robot.turn_right()",
            "robot.move(5)",
            "robot.turn_left()",
        ])

    # A. Robot instructions
    def test_all_robot_instructions(self):
        instructions = [
            ("MOVE", "steps"),
            ("BACK", 2),
            ("TURN", "LEFT"),
            ("TURN", "RIGHT"),
            ("SPEED", "sp"),
            ("PEN_UP", None),
            ("PEN_DOWN", None),
            ("POSITION", None),
        ]
        code = self.codegen.generate(instructions)
        expected = [
            "robot.move(steps)",
            "robot.back(2) if hasattr(robot, 'back') else robot.move(-(2))",
            "robot.turn_left()",
            "robot.turn_right()",
            "robot.speed(sp) if hasattr(robot, 'speed') else None",
            "robot.pen_up() if hasattr(robot, 'pen_up') else None",
            "robot.pen_down() if hasattr(robot, 'pen_down') else None",
            "robot.position() if hasattr(robot, 'position') else robot.show_status()",
        ]
        self.assertEqual(code, expected)

    # B. Variables, expressions, and output
    def test_variables_and_arithmetic(self):
        instructions = [
            ("DECLARE", "x", 5),
            ("DECLARE", "s", "'hello'"),
            ("ADD", "t0", "x", 3),
            ("MUL", "t1", "t0", 2),
            ("DIV", "t2", 1, 1),
            ("SUB", "t3", "t1", "t2"),
            ("ASSIGN", "x", "t3"),
            ("PRINT", "'done'"),
            ("PRINT", "x"),
        ]
        code = self.codegen.generate(instructions)
        expected = [
            "x = 5",
            "s = 'hello'",
            "t0 = x + 3",
            "t1 = t0 * 2",
            "t2 = 1 / 1",
            "t3 = t1 - t2",
            "x = t3",
            "print('done')",
            "print(x)",
        ]
        self.assertEqual(code, expected)

    def test_comparisons_and_logicals(self):
        instructions = [
            ("GT", "t0", "x", 3),
            ("OBSTACLE_AHEAD", "t1"),
            ("NOT", "t2", "t1"),
            ("AND", "t3", "t0", "t2"),
            ("OR", "t4", "t3", "t0"),
            ("NEG", "t5", 5),
            ("POS", "t6", 5),
        ]
        code = self.codegen.generate(instructions)
        expected = [
            "t0 = x > 3",
            "t1 = robot.obstacle_ahead() if hasattr(robot, 'obstacle_ahead') else False",
            "t2 = not t1",
            "t3 = t0 and t2",
            "t4 = t3 or t0",
            "t5 = -5",
            "t6 = +5",
        ]
        self.assertEqual(code, expected)

    # C. Conditional statements
    def test_if_else_indentation(self):
        instructions = [
            ("GT", "t0", "x", 3),
            ("JUMP_IF_FALSE", "t0", "ELSE_1"),
            ("MOVE", 2),
            ("JUMP", "END_IF_1"),
            ("LABEL", "ELSE_1"),
            ("BACK", 2),
            ("LABEL", "END_IF_1"),
        ]
        code = self.codegen.generate(instructions)
        expected = [
            "t0 = x > 3",
            "if t0:",
            "    robot.move(2)",
            "else:",
            "    robot.back(2) if hasattr(robot, 'back') else robot.move(-(2))",
        ]
        self.assertEqual(code, expected)

    def test_if_without_else(self):
        instructions = [
            ("LT", "t0", "steps", 5),
            ("JUMP_IF_FALSE", "t0", "END_IF_1"),
            ("TURN", "LEFT"),
            ("LABEL", "END_IF_1"),
        ]
        code = self.codegen.generate(instructions)
        expected = [
            "t0 = steps < 5",
            "if t0:",
            "    robot.turn_left()",
        ]
        self.assertEqual(code, expected)

    def test_nested_conditionals(self):
        instructions = [
            ("GT", "t0", "x", 0),
            ("JUMP_IF_FALSE", "t0", "END_IF_1"),
            ("GT", "t1", "y", 0),
            ("JUMP_IF_FALSE", "t1", "ELSE_2"),
            ("MOVE", 1),
            ("JUMP", "END_IF_2"),
            ("LABEL", "ELSE_2"),
            ("BACK", 1),
            ("LABEL", "END_IF_2"),
            ("LABEL", "END_IF_1"),
        ]
        code = self.codegen.generate(instructions)
        expected = [
            "t0 = x > 0",
            "if t0:",
            "    t1 = y > 0",
            "    if t1:",
            "        robot.move(1)",
            "    else:",
            "        robot.back(1) if hasattr(robot, 'back') else robot.move(-(1))",
        ]
        self.assertEqual(code, expected)

    # D. Loops
    def test_while_loop(self):
        instructions = [
            ("LABEL", "WHILE_START_1"),
            ("LT", "t0", "steps", 10),
            ("JUMP_IF_FALSE", "t0", "WHILE_END_1"),
            ("MOVE", 1),
            ("ADD", "t1", "steps", 1),
            ("ASSIGN", "steps", "t1"),
            ("JUMP", "WHILE_START_1"),
            ("LABEL", "WHILE_END_1"),
        ]
        code = self.codegen.generate(instructions)
        expected = [
            "while True:",
            "    t0 = steps < 10",
            "    if not t0: break",
            "    robot.move(1)",
            "    t1 = steps + 1",
            "    steps = t1",
        ]
        self.assertEqual(code, expected)

    def test_repeat_loop(self):
        instructions = [
            ("DECLARE", "_iter_1", 0),
            ("LABEL", "REPEAT_START_1"),
            ("LT", "t0", "_iter_1", 4),
            ("JUMP_IF_FALSE", "t0", "REPEAT_END_1"),
            ("MOVE", 2),
            ("ADD", "_iter_1", "_iter_1", 1),
            ("JUMP", "REPEAT_START_1"),
            ("LABEL", "REPEAT_END_1"),
        ]
        code = self.codegen.generate(instructions)
        expected = [
            "_iter_1 = 0",
            "while True:",
            "    t0 = _iter_1 < 4",
            "    if not t0: break",
            "    robot.move(2)",
            "    _iter_1 = _iter_1 + 1",
        ]
        self.assertEqual(code, expected)

    # E. Functions
    def test_functions(self):
        instructions = [
            ("LABEL", "FUNC_draw_square"),
            ("FUNC_DEF", "draw_square", ["size"]),
            ("MOVE", "size"),
            ("TURN", "RIGHT"),
            ("RETURN", None),
            ("LABEL", "END_FUNC_draw_square"),
            ("CALL", "draw_square", [5]),
        ]
        code = self.codegen.generate(instructions)
        expected = [
            "def draw_square(size):",
            "    robot.move(size)",
            "    robot.turn_right()",
            "    return",
            "draw_square(5)",
        ]
        self.assertEqual(code, expected)

    def test_function_call_expression(self):
        instructions = [
            ("CALL", "result", "get_val", [2, 3]),
        ]
        code = self.codegen.generate(instructions)
        self.assertEqual(code, ["result = get_val(2, 3)"])

    # F. Empty blocks
    def test_empty_blocks_emit_pass(self):
        instructions = [
            ("GT", "t0", "x", 0),
            ("JUMP_IF_FALSE", "t0", "ELSE_1"),
            ("JUMP", "END_IF_1"),
            ("LABEL", "ELSE_1"),
            ("LABEL", "END_IF_1"),
        ]
        code = self.codegen.generate(instructions)
        self.assertEqual(code, [
            "t0 = x > 0",
            "if t0:",
            "    pass",
            "else:",
            "    pass",
        ])

    # G. Execution verification
    def test_execution_with_mock_robot(self):
        # Generate and execute full program via exec()
        instructions = [
            ("DECLARE", "steps", 3),
            ("LABEL", "WHILE_START_1"),
            ("GT", "t0", "steps", 0),
            ("JUMP_IF_FALSE", "t0", "WHILE_END_1"),
            ("MOVE", "steps"),
            ("SUB", "t1", "steps", 1),
            ("ASSIGN", "steps", "t1"),
            ("JUMP", "WHILE_START_1"),
            ("LABEL", "WHILE_END_1"),
        ]
        code = self.codegen.generate(instructions)
        py_source = "\n".join(code)

        mock_robot = MockRobot()
        local_scope = {"robot": mock_robot}
        exec(py_source, local_scope)

        self.assertEqual(mock_robot.log, [
            "move(3)",
            "move(2)",
            "move(1)",
        ])

    # H. Invalid and unsupported instructions
    def test_invalid_instruction_format(self):
        with self.assertRaisesRegex(ValueError, "Invalid instruction format"):
            self.codegen.generate([()])

    def test_unsupported_instruction(self):
        with self.assertRaisesRegex(ValueError, "Unsupported IR instruction"):
            self.codegen.generate([("UNKNOWN_OPCODE", 123)])

    # I. End-to-end integration with full RoboLang 2.0 pipeline
    def test_end_to_end_robolang_2_program(self):
        from compiler.lexer import Lexer
        from compiler.parser import Parser
        from compiler.semantic import SemanticAnalyzer
        from compiler.ir import IRGenerator

        source = (
            "START\n"
            "LET steps = 5\n"
            "LET speed_value = 2\n"
            "LET result = (steps + 3) * 2 - 1 / 1\n"
            "SPEED speed_value\n"
            "PEN_DOWN\n"
            "IF steps >= 3 AND NOT OBSTACLE_AHEAD {\n"
            "    MOVE steps\n"
            "} ELSE {\n"
            "    BACK 2\n"
            "}\n"
            "WHILE steps < 10 OR steps == 5 {\n"
            "    steps = steps + 1\n"
            "}\n"
            "FUNC draw_square(size) {\n"
            "    REPEAT 4 {\n"
            "        MOVE size\n"
            "        TURN RIGHT\n"
            "    }\n"
            "}\n"
            "draw_square(5)\n"
            "IF steps != 0 AND steps <= 10 {\n"
            "    TURN LEFT\n"
            "}\n"
            "PEN_UP\n"
            "POSITION\n"
            'PRINT "Robot finished"\n'
            "PRINT result\n"
            "STOP\n"
        )

        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        SemanticAnalyzer().analyze(ast)

        ir_gen = IRGenerator()
        instructions = ir_gen.generate(ast)
        self.assertTrue(len(instructions) > 0)

        code = self.codegen.generate(instructions)
        self.assertTrue(len(code) > 0)

        # Execute generated code in Python runtime
        mock_robot = MockRobot()
        local_scope = {"robot": mock_robot}
        exec("\n".join(code), local_scope)

        # Check expected variable values in local_scope
        self.assertEqual(local_scope["steps"], 10)
        self.assertEqual(local_scope["speed_value"], 2)
        self.assertEqual(local_scope["result"], 15.0)

        # Check mock robot logged calls
        self.assertIn("speed(2)", mock_robot.log)
        self.assertIn("pen_down()", mock_robot.log)
        self.assertIn("move(5)", mock_robot.log)
        self.assertIn("turn_right()", mock_robot.log)
        self.assertIn("turn_left()", mock_robot.log)
        self.assertIn("pen_up()", mock_robot.log)
        self.assertIn("position()", mock_robot.log)

    # J. Verification on actual Robot runtime class
    def test_actual_robot_runtime_state_changes(self):
        from robot.robot import Robot

        instructions = [
            ("MOVE", 5),
            ("TURN", "RIGHT"),
            ("MOVE", 3),
            ("BACK", 1),
            ("POSITION", None),
        ]
        code = self.codegen.generate(instructions)
        py_source = "\n".join(code)

        # Validate with Python's built-in compiler before execution
        compiled = compile(py_source, "<generated_code>", "exec")

        actual_robot = Robot()
        exec(compiled, {"robot": actual_robot})

        # Started at (0, 0) NORTH
        # MOVE 5 -> (0, 5) NORTH
        # TURN RIGHT -> (0, 5) EAST
        # MOVE 3 -> (3, 5) EAST
        # BACK 1 -> (2, 5) EAST
        self.assertEqual(actual_robot.x, 2)
        self.assertEqual(actual_robot.y, 5)
        self.assertEqual(actual_robot.direction, "EAST")

    def test_actual_robot_with_unsupported_features_does_not_crash(self):
        from robot.robot import Robot

        instructions = [
            ("SPEED", 5),
            ("PEN_UP", None),
            ("PEN_DOWN", None),
            ("OBSTACLE_AHEAD", "obs"),
            ("POSITION", None),
        ]
        code = self.codegen.generate(instructions)
        py_source = "\n".join(code)

        compiled = compile(py_source, "<generated_code>", "exec")

        actual_robot = Robot()
        scope = {"robot": actual_robot}
        exec(compiled, scope)

        # OBSTACLE_AHEAD safely evaluates to False when robot has no sensor
        self.assertFalse(scope["obs"])

    # K. Control flow edge cases: empty branches, false while condition, zero repeat
    def test_empty_if_branches(self):
        instructions = [
            ("GT", "t0", "x", 0),
            ("JUMP_IF_FALSE", "t0", "ELSE_1"),
            ("JUMP", "END_IF_1"),
            ("LABEL", "ELSE_1"),
            ("LABEL", "END_IF_1"),
        ]
        code = self.codegen.generate(instructions)
        py_source = "\n".join(code)

        # Must compile cleanly as valid Python with pass in empty branches
        compiled = compile(py_source, "<generated_code>", "exec")
        scope = {"x": 10}
        exec(compiled, scope)

    def test_while_loop_with_initially_false_condition(self):
        from robot.robot import Robot

        instructions = [
            ("DECLARE", "steps", 0),
            ("LABEL", "WHILE_START_1"),
            ("GT", "t0", "steps", 10),
            ("JUMP_IF_FALSE", "t0", "WHILE_END_1"),
            ("MOVE", 5),
            ("JUMP", "WHILE_START_1"),
            ("LABEL", "WHILE_END_1"),
        ]
        code = self.codegen.generate(instructions)
        compiled = compile("\n".join(code), "<generated_code>", "exec")

        actual_robot = Robot()
        scope = {"robot": actual_robot}
        exec(compiled, scope)

        # Loop body should never have executed
        self.assertEqual(actual_robot.x, 0)
        self.assertEqual(actual_robot.y, 0)

    def test_repeat_loop_with_zero_count(self):
        from robot.robot import Robot

        instructions = [
            ("DECLARE", "count", 0),
            ("DECLARE", "_iter_1", 0),
            ("LABEL", "REPEAT_START_1"),
            ("LT", "t0", "_iter_1", "count"),
            ("JUMP_IF_FALSE", "t0", "REPEAT_END_1"),
            ("MOVE", 2),
            ("ADD", "_iter_1", "_iter_1", 1),
            ("JUMP", "REPEAT_START_1"),
            ("LABEL", "REPEAT_END_1"),
        ]
        code = self.codegen.generate(instructions)
        compiled = compile("\n".join(code), "<generated_code>", "exec")

        actual_robot = Robot()
        scope = {"robot": actual_robot}
        exec(compiled, scope)

        # 0 repetitions: body should not execute
        self.assertEqual(actual_robot.y, 0)


if __name__ == "__main__":
    unittest.main()
