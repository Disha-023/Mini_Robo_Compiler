import io
import sys
import unittest

from robot.executor import RobotExecutor
from robot.robot import Robot


class TestRobotExecutor(unittest.TestCase):

    def setUp(self):
        self.executor = RobotExecutor()

    def test_legacy_movement_and_turn(self):
        instructions = [
            ("MOVE", 2),
            ("TURN", "LEFT"),
            ("MOVE", 3),
            ("TURN", "RIGHT"),
            ("MOVE", 1),
        ]
        robot = self.executor.execute(instructions)

        # (0, 0) NORTH -> MOVE 2 -> (0, 2) NORTH
        # TURN LEFT -> (0, 2) WEST
        # MOVE 3 -> (-3, 2) WEST
        # TURN RIGHT -> (-3, 2) NORTH
        # MOVE 1 -> (-3, 3) NORTH
        self.assertEqual(robot.x, -3)
        self.assertEqual(robot.y, 3)
        self.assertEqual(robot.direction, "NORTH")
        self.assertEqual(len(robot.history), 5)

    def test_variables_and_arithmetic(self):
        instructions = [
            ("DECLARE", "steps", 5),
            ("ADD", "t0", "steps", 3),
            ("MOVE", "t0"),
            ("TURN", "RIGHT"),
            ("SUB", "t1", "steps", 2),
            ("MOVE", "t1"),
        ]
        self.executor.execute(instructions)

        # MOVE 8 NORTH -> (0, 8)
        # TURN RIGHT -> EAST
        # MOVE 3 EAST -> (3, 8)
        self.assertEqual(self.executor.robot.x, 3)
        self.assertEqual(self.executor.robot.y, 8)
        self.assertEqual(self.executor.robot.direction, "EAST")

    def test_conditional_execution_true_branch(self):
        instructions = [
            ("DECLARE", "x", 10),
            ("GT", "t0", "x", 5),
            ("JUMP_IF_FALSE", "t0", "ELSE_1"),
            ("MOVE", 4),
            ("JUMP", "END_IF_1"),
            ("LABEL", "ELSE_1"),
            ("MOVE", 1),
            ("LABEL", "END_IF_1"),
        ]
        self.executor.execute(instructions)
        self.assertEqual(self.executor.robot.y, 4)

    def test_conditional_execution_false_branch(self):
        instructions = [
            ("DECLARE", "x", 2),
            ("GT", "t0", "x", 5),
            ("JUMP_IF_FALSE", "t0", "ELSE_1"),
            ("MOVE", 4),
            ("JUMP", "END_IF_1"),
            ("LABEL", "ELSE_1"),
            ("MOVE", 1),
            ("LABEL", "END_IF_1"),
        ]
        self.executor.execute(instructions)
        self.assertEqual(self.executor.robot.y, 1)

    def test_while_loop(self):
        instructions = [
            ("DECLARE", "count", 0),
            ("LABEL", "WHILE_START_1"),
            ("LT", "t0", "count", 4),
            ("JUMP_IF_FALSE", "t0", "WHILE_END_1"),
            ("MOVE", 2),
            ("ADD", "count", "count", 1),
            ("JUMP", "WHILE_START_1"),
            ("LABEL", "WHILE_END_1"),
        ]
        self.executor.execute(instructions)
        # 4 iterations * 2 steps = 8
        self.assertEqual(self.executor.robot.y, 8)

    def test_repeat_loop(self):
        instructions = [
            ("DECLARE", "limit", 4),
            ("DECLARE", "_iter_1", 0),
            ("LABEL", "REPEAT_START_1"),
            ("LT", "t0", "_iter_1", "limit"),
            ("JUMP_IF_FALSE", "t0", "REPEAT_END_1"),
            ("MOVE", 2),
            ("TURN", "RIGHT"),
            ("ADD", "_iter_1", "_iter_1", 1),
            ("JUMP", "REPEAT_START_1"),
            ("LABEL", "REPEAT_END_1"),
        ]
        self.executor.execute(instructions)
        # Traced a complete square of side 2
        self.assertEqual(self.executor.robot.x, 0)
        self.assertEqual(self.executor.robot.y, 0)
        self.assertEqual(self.executor.robot.direction, "NORTH")

    def test_function_definition_and_call(self):
        instructions = [
            ("LABEL", "FUNC_step_forward"),
            ("FUNC_DEF", "step_forward", ["dist"]),
            ("MOVE", "dist"),
            ("RETURN", None),
            ("LABEL", "END_FUNC_step_forward"),
            ("CALL", "step_forward", [7]),
        ]
        self.executor.execute(instructions)
        self.assertEqual(self.executor.robot.y, 7)

    def test_obstacle_ahead_runtime_check(self):
        # Configure robot with an obstacle at (0, 1)
        robot = Robot(obstacles=[(0, 1)])
        executor = RobotExecutor(robot=robot)

        # IR:
        # Check obstacle ahead. If blocked, TURN RIGHT and MOVE 3. Else MOVE 3.
        instructions = [
            ("OBSTACLE_AHEAD", "obs"),
            ("JUMP_IF_FALSE", "obs", "ELSE_1"),
            ("TURN", "RIGHT"),
            ("MOVE", 3),
            ("JUMP", "END_IF_1"),
            ("LABEL", "ELSE_1"),
            ("MOVE", 3),
            ("LABEL", "END_IF_1"),
        ]
        executor.execute(instructions)

        # Because (0, 1) has an obstacle, robot turns EAST and moves 3
        self.assertEqual(executor.robot.x, 3)
        self.assertEqual(executor.robot.y, 0)
        self.assertEqual(executor.robot.direction, "EAST")

    def test_custom_robot_injection_and_action_history(self):
        custom_robot = Robot()
        executor = RobotExecutor(robot=custom_robot)
        self.assertIs(executor.robot, custom_robot)

        instructions = [
            ("PEN_DOWN", None),
            ("SPEED", 2),
            ("MOVE", 5),
            ("PEN_UP", None),
        ]
        executor.execute(instructions)

        # Actions are recorded on the exact same robot instance
        self.assertEqual(len(custom_robot.history), 4)
        self.assertEqual(custom_robot.history[0]["type"], "PEN_DOWN")
        self.assertEqual(custom_robot.history[1]["type"], "SPEED")
        self.assertEqual(custom_robot.history[2]["type"], "MOVE")
        self.assertEqual(custom_robot.history[2]["to"], (0, 5))
        self.assertTrue(custom_robot.history[2]["pen_down"])
        self.assertEqual(custom_robot.history[3]["type"], "PEN_UP")

    def test_generated_python_code_list_execution(self):
        py_lines = [
            "robot.move(4)",
            "robot.turn_left()",
            "robot.move(2)",
        ]
        self.executor.execute(py_lines)
        self.assertEqual(self.executor.robot.x, -2)
        self.assertEqual(self.executor.robot.y, 4)
        self.assertEqual(self.executor.robot.direction, "WEST")

    def test_generated_python_code_string_execution(self):
        py_code = "robot.move(5)\nrobot.turn_right()\nrobot.move(3)"
        self.executor.execute(py_code)
        self.assertEqual(self.executor.robot.x, 3)
        self.assertEqual(self.executor.robot.y, 5)
        self.assertEqual(self.executor.robot.direction, "EAST")

    def test_empty_program(self):
        self.executor.execute([])
        self.assertEqual((self.executor.robot.x, self.executor.robot.y), (0, 0))

        self.executor.execute("")
        self.assertEqual((self.executor.robot.x, self.executor.robot.y), (0, 0))

    def test_invalid_program_type_raises_error(self):
        with self.assertRaises(TypeError):
            self.executor.execute(12345)

        with self.assertRaises(TypeError):
            self.executor.execute([1, 2, 3])

    def test_restricted_builtins_blocks_dangerous_calls(self):
        # Attempt to call __import__ inside the execution environment
        malicious_code = "__import__('os').system('echo danger')"
        with self.assertRaises(NameError):
            self.executor.execute(malicious_code)

    def test_show_status_output_behavior(self):
        captured_output = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured_output
            self.executor.execute([("MOVE", 2), ("MOVE", 3)])
        finally:
            sys.stdout = old_stdout

        output_str = captured_output.getvalue()
        # Should only have printed the final status once, not after every instruction
        status_count = output_str.count("Position:")
        self.assertEqual(status_count, 1)
        self.assertIn("Position: (0, 5), Direction: NORTH", output_str)

    def test_end_to_end_compiler_ir_robot_commands(self):
        from compiler.ast import (
            Program, Move, Back, Turn, Speed, PenDown, PenUp, Position
        )
        from compiler.ir import IRGenerator

        # Build AST representing representative robot commands
        ast_prog = Program([
            Speed(3),
            PenDown(),
            Move(4),
            Turn("RIGHT"),
            Back(2),
            Position(),
            PenUp(),
        ])
        ir_instructions = IRGenerator().generate(ast_prog)

        # Execute through RobotExecutor
        executor = RobotExecutor()
        robot = executor.execute(ir_instructions)

        # Facing NORTH -> speed=3, pen=True, move 4 -> (0, 4)
        # Turn RIGHT -> facing EAST
        # Back 2 -> facing EAST, moving backward 2 steps -> (-2, 4)
        # PenUp -> pen=False
        self.assertEqual(robot.x, -2)
        self.assertEqual(robot.y, 4)
        self.assertEqual(robot.direction, "EAST")
        self.assertFalse(robot.is_pen_down)
        self.assertEqual(robot.speed_val, 3)

        # Verify history records contain accurate action types
        history_types = [h["type"] for h in robot.history]
        self.assertEqual(
            history_types,
            ["SPEED", "PEN_DOWN", "MOVE", "TURN", "BACK", "POSITION", "PEN_UP"]
        )

    def test_mixed_instruction_list_fails_clearly(self):
        with self.assertRaises(TypeError):
            self.executor.execute([("MOVE", 2), "robot.turn_left()"])

        with self.assertRaises(TypeError):
            self.executor.execute(["robot.move(2)", 123])


if __name__ == "__main__":
    unittest.main()
