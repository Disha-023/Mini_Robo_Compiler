import unittest
from unittest.mock import patch

from robot.robot import Robot
from robot.simulator import RobotSimulator


class TestRobotSimulator(unittest.TestCase):

    def test_empty_history(self):
        sim = RobotSimulator([], headless=True)
        self.assertEqual(len(sim.actions), 0)
        self.assertEqual(sim.x, 0)
        self.assertEqual(sim.y, 0)
        self.assertEqual(sim.direction, "NORTH")
        sim.execute_next(0)
        self.assertTrue(sim.is_finished)

    def test_headless_run_empty_history_completes_safely(self):
        sim = RobotSimulator([], headless=True)
        sim.run()
        self.assertTrue(sim.is_finished)
        self.assertEqual((sim.x, sim.y), (0, 0))
        self.assertEqual(sim.direction, "NORTH")
        self.assertFalse(sim.display_pen_down)
        self.assertEqual(sim.display_speed, 1)

    def test_headless_run_completes_full_history(self):
        robot = Robot()
        robot.speed(2)
        robot.pen_down()
        robot.move(3)
        robot.turn_right()
        robot.back(2)
        robot.pen_up()
        robot.move(1)
        robot.turn_left()

        # Capture final state of the original robot
        orig_x, orig_y = robot.x, robot.y
        orig_dir = robot.direction
        orig_history_len = len(robot.history)
        orig_history_snapshot = list(robot.history)

        # Replay entire history in headless mode using run()
        sim = RobotSimulator(robot, headless=True)
        sim.run()

        # 1. Fully replayed to the end
        self.assertTrue(sim.is_finished)
        self.assertEqual(sim.current_step, orig_history_len - 1)

        # 2. Final displayed state reflects the events
        self.assertEqual((sim.x, sim.y), (orig_x, orig_y))
        self.assertEqual(sim.direction, orig_dir)
        self.assertFalse(sim.display_pen_down)
        self.assertEqual(sim.display_speed, 2)

        # 3. Expected trails recorded (only the 2 moves made while pen_down was True)
        self.assertEqual(len(sim.trails), 2)
        self.assertEqual(sim.trails[0], ((0, 0), (0, 3)))
        self.assertEqual(sim.trails[1], ((0, 3), (-2, 3)))

        # 4. Original robot instance remains untouched
        self.assertEqual((robot.x, robot.y), (orig_x, orig_y))
        self.assertEqual(robot.direction, orig_dir)
        self.assertEqual(len(robot.history), orig_history_len)
        self.assertEqual(robot.history, orig_history_snapshot)

    def test_headless_run_replays_events_in_chronological_order(self):
        events = [
            {"type": "SPEED", "value": 3},
            {"type": "PEN_DOWN", "pen_down": True, "pos": (0, 0)},
            {
                "type": "MOVE",
                "from": (0, 0),
                "to": (0, 2),
                "steps": 2,
                "direction": "NORTH",
                "pen_down": True,
                "speed": 3,
            },
            {
                "type": "TURN",
                "direction": "RIGHT",
                "from_dir": "NORTH",
                "to_dir": "EAST",
                "pos": (0, 2),
            },
            {
                "type": "MOVE",
                "from": (0, 2),
                "to": (4, 2),
                "steps": 4,
                "direction": "EAST",
                "pen_down": True,
                "speed": 3,
            },
            {"type": "PEN_UP", "pen_down": False, "pos": (4, 2)},
            {"type": "POSITION", "pos": (4, 2), "direction": "EAST"},
        ]
        sim = RobotSimulator(events, headless=True)

        observed_states = []
        original_process_event = sim.process_event

        def recording_process_event(event):
            original_process_event(event)
            observed_states.append((sim.x, sim.y, sim.direction, sim.display_pen_down, sim.display_speed))

        sim.process_event = recording_process_event
        sim.run()

        expected_states = [
            (0, 0, "NORTH", False, 3),   # Event 0: SPEED 3
            (0, 0, "NORTH", True, 3),    # Event 1: PEN_DOWN
            (0, 2, "NORTH", True, 3),    # Event 2: MOVE (0, 0) -> (0, 2)
            (0, 2, "EAST", True, 3),     # Event 3: TURN RIGHT -> EAST
            (4, 2, "EAST", True, 3),     # Event 4: MOVE (0, 2) -> (4, 2)
            (4, 2, "EAST", False, 3),    # Event 5: PEN_UP
            (4, 2, "EAST", False, 3),    # Event 6: POSITION
        ]
        self.assertEqual(observed_states, expected_states)
        self.assertTrue(sim.is_finished)
        self.assertEqual((sim.x, sim.y), (4, 2))
        self.assertEqual(sim.direction, "EAST")
        self.assertFalse(sim.display_pen_down)
        self.assertEqual(sim.display_speed, 3)

    def test_pre_executed_robot_does_not_invoke_executor(self):
        robot = Robot()
        robot.move(4)
        robot.turn_right()

        with patch("robot.executor.RobotExecutor.execute") as mock_exec:
            sim = RobotSimulator(robot, headless=True)
            sim.run()
            mock_exec.assert_not_called()

        # (0, 0) NORTH -> MOVE 4 -> (0, 4) NORTH -> TURN RIGHT -> (0, 4) EAST
        self.assertEqual((sim.x, sim.y), (0, 4))
        self.assertEqual(sim.direction, "EAST")

    def test_legacy_ir_instructions_invokes_executor_once(self):
        ir = [("MOVE", 2), ("TURN", "LEFT")]

        with patch("robot.executor.RobotExecutor.execute") as mock_exec:
            sim = RobotSimulator(ir, headless=True)
            mock_exec.assert_called_once_with(ir)

    def test_legacy_ir_executes_exactly_once_and_replays_history(self):
        from robot.executor import RobotExecutor
        ir = [
            ("MOVE", 3),
            ("TURN", "RIGHT"),
            ("MOVE", 2),
        ]
        orig_execute = RobotExecutor.execute

        with patch.object(RobotExecutor, "execute", side_effect=orig_execute, autospec=True) as mock_exec:
            sim = RobotSimulator(ir, headless=True)
            # Must be called exactly once during extraction
            self.assertEqual(mock_exec.call_count, 1)

            # Replaying through run() must NOT invoke executor again
            sim.run()
            self.assertEqual(mock_exec.call_count, 1)

        # Confirm resulting history was fully replayed
        self.assertTrue(sim.is_finished)
        self.assertEqual((sim.x, sim.y), (2, 3))
        self.assertEqual(sim.direction, "EAST")

    def test_forward_and_backward_movement(self):
        events = [
            {
                "type": "MOVE",
                "from": (0, 0),
                "to": (0, 3),
                "steps": 3,
                "direction": "NORTH",
                "pen_down": False,
                "speed": 1,
            },
            {
                "type": "BACK",
                "from": (0, 3),
                "to": (0, 1),
                "steps": 2,
                "direction": "NORTH",
                "pen_down": False,
                "speed": 1,
            },
        ]
        sim = RobotSimulator(events, headless=True)

        # Step 0: MOVE (0, 0) -> (0, 3)
        sim.execute_next(0)
        self.assertEqual((sim.x, sim.y), (0, 3))

        # Step 1: BACK (0, 3) -> (0, 1)
        sim.execute_next(1)
        self.assertEqual((sim.x, sim.y), (0, 1))

    def test_turns_and_heading_updates(self):
        events = [
            {
                "type": "TURN",
                "direction": "RIGHT",
                "from_dir": "NORTH",
                "to_dir": "EAST",
                "pos": (0, 0),
            },
            {
                "type": "TURN",
                "direction": "RIGHT",
                "from_dir": "EAST",
                "to_dir": "SOUTH",
                "pos": (0, 0),
            },
        ]
        sim = RobotSimulator(events, headless=True)

        sim.execute_next(0)
        self.assertEqual(sim.direction, "EAST")

        sim.execute_next(1)
        self.assertEqual(sim.direction, "SOUTH")

    def test_pen_up_movement_creates_no_trail(self):
        events = [
            {
                "type": "MOVE",
                "from": (0, 0),
                "to": (0, 4),
                "steps": 4,
                "direction": "NORTH",
                "pen_down": False,
                "speed": 1,
            }
        ]
        sim = RobotSimulator(events, headless=True)
        sim.execute_next(0)
        self.assertEqual(len(sim.trails), 0)

    def test_pen_down_movement_creates_a_trail(self):
        events = [
            {
                "type": "MOVE",
                "from": (0, 0),
                "to": (0, 4),
                "steps": 4,
                "direction": "NORTH",
                "pen_down": True,
                "speed": 1,
            }
        ]
        sim = RobotSimulator(events, headless=True)
        sim.execute_next(0)
        self.assertEqual(len(sim.trails), 1)
        self.assertEqual(sim.trails[0], ((0, 0), (0, 4)))

    def test_speed_changes_affect_animation_timing(self):
        sim = RobotSimulator([], headless=True)

        # Default speed = 1 -> delay = 500 ms
        sim.display_speed = 1
        self.assertEqual(sim.get_delay(), 500)

        # Speed 2 -> 250 ms
        sim.display_speed = 2
        self.assertEqual(sim.get_delay(), 250)

        # Speed 5 -> 100 ms
        sim.display_speed = 5
        self.assertEqual(sim.get_delay(), 100)

        # Extreme fast speed 50 -> capped at min safeguard 50 ms
        sim.display_speed = 50
        self.assertEqual(sim.get_delay(), 50)

        # Extreme slow speed 0.1 -> capped at max safeguard 2000 ms
        sim.display_speed = 0.1
        self.assertEqual(sim.get_delay(), 2000)

        # Invalid speed 0 or negative -> safeguarded to 500 ms
        sim.display_speed = 0
        self.assertEqual(sim.get_delay(), 500)
        sim.display_speed = -5
        self.assertEqual(sim.get_delay(), 500)
        sim.display_speed = "invalid"
        self.assertEqual(sim.get_delay(), 500)

    def test_multiple_event_types_in_one_history(self):
        events = [
            {"type": "SPEED", "value": 2},
            {"type": "PEN_DOWN", "pen_down": True, "pos": (0, 0)},
            {
                "type": "MOVE",
                "from": (0, 0),
                "to": (0, 3),
                "steps": 3,
                "direction": "NORTH",
                "pen_down": True,
                "speed": 2,
            },
            {
                "type": "TURN",
                "direction": "RIGHT",
                "from_dir": "NORTH",
                "to_dir": "EAST",
                "pos": (0, 3),
            },
            {
                "type": "BACK",
                "from": (0, 3),
                "to": (-2, 3),
                "steps": 2,
                "direction": "EAST",
                "pen_down": True,
                "speed": 2,
            },
            {"type": "PEN_UP", "pen_down": False, "pos": (-2, 3)},
            {
                "type": "MOVE",
                "from": (-2, 3),
                "to": (1, 3),
                "steps": 3,
                "direction": "EAST",
                "pen_down": False,
                "speed": 2,
            },
            {"type": "POSITION", "pos": (1, 3), "direction": "EAST"},
        ]
        sim = RobotSimulator(events, headless=True)
        sim.run()

        self.assertEqual((sim.x, sim.y), (1, 3))
        self.assertEqual(sim.direction, "EAST")
        self.assertFalse(sim.display_pen_down)
        self.assertEqual(sim.display_speed, 2)
        # Only the 2 pen_down movements recorded trails
        self.assertEqual(len(sim.trails), 2)
        self.assertEqual(sim.trails[0], ((0, 0), (0, 3)))
        self.assertEqual(sim.trails[1], ((0, 3), (-2, 3)))

    def test_unknown_or_malformed_events_handled_gracefully(self):
        events = [
            "not_a_dictionary",
            {"missing_type": True},
            {"type": "UNKNOWN_ACTION_TYPE"},
            {
                "type": "MOVE",
                "from": "malformed_from",
                "to": ("bad_x", 4),
                "steps": 2,
                "direction": "EAST",
                "pen_down": False,
                "speed": 1,
            },
            {
                "type": "MOVE",
                "from": (0, 0),
                "to": (2, 0),
                "steps": 2,
                "direction": "EAST",
                "pen_down": True,
                "speed": 1,
            },
        ]
        sim = RobotSimulator(events, headless=True)
        sim.run()

        # None of the malformed events crash the simulator, valid events process normally
        self.assertEqual((sim.x, sim.y), (2, 0))
        self.assertEqual(len(sim.trails), 1)

    def test_legacy_ir_instruction_list_compatibility(self):
        ir = [
            ("MOVE", 3),
            ("TURN", "RIGHT"),
            ("MOVE", 2),
        ]
        sim = RobotSimulator(ir, headless=True)
        self.assertEqual(len(sim.actions), 3)
        sim.run()

        # (0, 0) -> MOVE 3 NORTH -> TURN RIGHT (EAST) -> MOVE 2 EAST -> (2, 3)
        self.assertEqual((sim.x, sim.y), (2, 3))
        self.assertEqual(sim.direction, "EAST")

    def test_coordinate_conversion(self):
        sim = RobotSimulator([], headless=True)
        # Center (0, 0) -> (300, 300)
        self.assertEqual(sim.to_screen_coords(0, 0), (300, 300))
        # (2, 4) -> (300 + 100, 300 - 200) = (400, 100)
        self.assertEqual(sim.to_screen_coords(2, 4), (400, 100))
        # (-3, -2) -> (300 - 150, 300 + 100) = (150, 400)
        self.assertEqual(sim.to_screen_coords(-3, -2), (150, 400))

    def test_invalid_target_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            RobotSimulator(12345, headless=True)

        with self.assertRaises(TypeError):
            RobotSimulator("unsupported_string_target", headless=True)

        with self.assertRaises(TypeError):
            RobotSimulator({"not": "supported"}, headless=True)

    def test_malformed_coordinates_with_mocked_canvas(self):
        import math
        from unittest.mock import MagicMock

        events = [
            {
                "type": "MOVE",
                "from": None,
                "to": "invalid_str",
                "steps": 1,
                "direction": "NORTH",
                "pen_down": True,
                "speed": 1,
            },
            {
                "type": "MOVE",
                "from": (1,),  # incomplete coordinate pair
                "to": (2, "bad_num"),
                "steps": 2,
                "direction": "EAST",
                "pen_down": True,
                "speed": 1,
            },
            {
                "type": "MOVE",
                "from": ("str_x", 3),
                "to": (3, 4),
                "steps": 2,
                "direction": "EAST",
                "pen_down": True,
                "speed": 1,
            },
            {
                "type": "MOVE",
                "from": (float("nan"), float("inf")),
                "to": (5, 6),
                "steps": 2,
                "direction": "NORTH",
                "pen_down": True,
                "speed": 1,
            },
            {
                "type": "MOVE",
                "from": (5, 6),
                "to": None,
                "steps": 1,
                "direction": "NORTH",
                "pen_down": True,
                "speed": 1,
            },
        ]
        sim = RobotSimulator(events, headless=True)
        mock_canvas = MagicMock()
        sim.canvas = mock_canvas

        # Process each malformed event with canvas active
        for i in range(len(events)):
            sim.execute_next(i)

        # Confirm canvas.create_line was called
        self.assertGreater(mock_canvas.create_line.call_count, 0)
        # Verify every argument passed as screen coordinates is finite and numeric
        for call_args in mock_canvas.create_line.call_args_list:
            args, kwargs = call_args
            for coord in args[:4]:
                self.assertIsInstance(coord, (int, float))
                self.assertTrue(math.isfinite(coord))

        self.assertEqual((sim.x, sim.y), (5, 6))

    def test_malformed_coordinates_in_headless_mode(self):
        events = [
            # from and to are None
            {"type": "MOVE", "from": None, "to": None, "steps": 1, "direction": "NORTH", "pen_down": True, "speed": 1},
            # from is a string, to is an incomplete 1-tuple
            {"type": "MOVE", "from": "str_coord", "to": (10,), "steps": 1, "direction": "NORTH", "pen_down": True, "speed": 1},
            # from has None inside tuple, to has strings
            {"type": "MOVE", "from": (None, 2), "to": ("invalid_x", "invalid_y"), "steps": 1, "direction": "NORTH", "pen_down": True, "speed": 1},
            # Valid move to establish new position
            {"type": "MOVE", "from": (0, 0), "to": (2, 5), "steps": 5, "direction": "NORTH", "pen_down": True, "speed": 1},
        ]
        sim = RobotSimulator(events, headless=True)
        # Must execute cleanly without unhandled exceptions
        sim.run()

        self.assertTrue(sim.is_finished)
        self.assertEqual((sim.x, sim.y), (2, 5))
        self.assertEqual(sim.direction, "NORTH")
        self.assertTrue(sim.display_pen_down)
        self.assertGreater(len(sim.trails), 0)

    def test_gui_playback_schedules_via_root_after(self):
        from unittest.mock import MagicMock

        events = [
            {"type": "MOVE", "from": (0, 0), "to": (0, 2), "steps": 2, "direction": "NORTH", "pen_down": False, "speed": 2},
            {"type": "MOVE", "from": (0, 2), "to": (0, 4), "steps": 2, "direction": "NORTH", "pen_down": False, "speed": 2},
        ]

        # Use mock root and mock canvas with headless=False
        mock_root = MagicMock()
        mock_canvas = MagicMock()

        sim = RobotSimulator(events, root=mock_root, headless=False)
        sim.canvas = mock_canvas

        # Call execute_next(0): should only process event 0 and schedule event 1
        sim.execute_next(0)

        # 1. State should reflect only event 0
        self.assertEqual((sim.x, sim.y), (0, 2))
        self.assertEqual(sim.current_step, 0)
        self.assertFalse(sim.is_finished)

        # 2. root.after must have been scheduled with expected delay (250ms for speed=2)
        mock_root.after.assert_called_once()
        args, _ = mock_root.after.call_args
        self.assertEqual(args[0], 250)  # 500 / 2 = 250 ms
        callback = args[1]

        # 3. Invoking the scheduled callback triggers event 1
        callback()
        self.assertEqual((sim.x, sim.y), (0, 4))
        self.assertEqual(sim.current_step, 1)

    def test_gui_run_does_not_synchronously_consume_history(self):
        from unittest.mock import MagicMock

        events = [
            {"type": "MOVE", "from": (0, 0), "to": (0, 2), "steps": 2, "direction": "NORTH", "pen_down": False, "speed": 2},
            {"type": "MOVE", "from": (0, 2), "to": (0, 4), "steps": 2, "direction": "NORTH", "pen_down": False, "speed": 2},
            {"type": "MOVE", "from": (0, 4), "to": (0, 6), "steps": 2, "direction": "NORTH", "pen_down": False, "speed": 2},
        ]

        mock_root = MagicMock()
        mock_canvas = MagicMock()

        sim = RobotSimulator(events, root=mock_root, headless=False)
        sim.canvas = mock_canvas

        # Calling run() should call execute_next(0) and enter root.mainloop()
        # It must NOT synchronously consume subsequent events!
        sim.run()

        # 1. mainloop was entered
        mock_root.mainloop.assert_called_once()

        # 2. Only step 0 was executed, NOT steps 1 or 2
        self.assertEqual(sim.current_step, 0)
        self.assertEqual((sim.x, sim.y), (0, 2))
        self.assertFalse(sim.is_finished)

        # 3. Exactly one call to root.after for step 1 was scheduled
        mock_root.after.assert_called_once()

    def test_public_attributes_and_interface_compatibility(self):
        robot = Robot()
        robot.move(2)
        sim = RobotSimulator(robot, headless=True)

        # Properties
        self.assertEqual(sim.x, 0)
        self.assertEqual(sim.y, 0)
        self.assertEqual(sim.direction, "NORTH")

        # Public attributes
        self.assertEqual(sim.cell_size, 50)
        self.assertTrue(sim.headless)
        self.assertEqual(sim.display_pen_down, False)
        self.assertEqual(sim.display_speed, 1)
        self.assertEqual(sim.trails, [])
        self.assertEqual(sim.current_step, 0)
        self.assertEqual(sim.is_finished, False)
        self.assertIs(sim.target_robot, robot)
        self.assertEqual(len(sim.actions), 1)

        # Public methods callable without error
        sx, sy = sim.to_screen_coords(1, 2)
        self.assertEqual((sx, sy), (350, 200))

        delay = sim.get_delay()
        self.assertEqual(delay, 500)

        # Grid and robot drawing safe with or without canvas
        sim.draw_grid()
        sim.draw_robot()
        sim.draw_status()

    def test_end_to_end_compiler_pipeline_to_simulator(self):
        from compiler.lexer import Lexer
        from compiler.parser import Parser
        from compiler.semantic import SemanticAnalyzer
        from compiler.ir import IRGenerator
        from robot.executor import RobotExecutor

        code = """
        START
        LET dist = 4
        SPEED 2
        PEN_DOWN
        MOVE dist
        TURN RIGHT
        MOVE 3
        TURN LEFT
        BACK 1
        PEN_UP
        POSITION
        STOP
        """
        # Step 1: Full compiler frontend
        tokens = Lexer(code).tokenize()
        ast = Parser(tokens).parse()
        SemanticAnalyzer().analyze(ast)
        instructions = IRGenerator().generate(ast)
        self.assertGreater(len(instructions), 0)

        # Step 2: Executor
        executor = RobotExecutor()
        with patch.object(RobotExecutor, "execute", wraps=executor.execute) as mock_exec:
            executor.execute(instructions)
            self.assertEqual(mock_exec.call_count, 1)

            # Robot state after execution:
            # (0, 0) NORTH -> MOVE 4 -> (0, 4) NORTH
            # TURN RIGHT -> (0, 4) EAST
            # MOVE 3 -> (3, 4) EAST
            # TURN LEFT -> (3, 4) NORTH
            # BACK 1 -> (3, 3) NORTH
            self.assertEqual((executor.robot.x, executor.robot.y), (3, 3))
            self.assertEqual(executor.robot.direction, "NORTH")
            self.assertFalse(executor.robot.is_pen_down)
            self.assertEqual(executor.robot.speed_val, 2)

            # Step 3: Simulator replay
            sim = RobotSimulator(executor.robot, headless=True)
            sim.run()

            # Executor should still have been called exactly once (never re-executed by simulator)
            self.assertEqual(mock_exec.call_count, 1)

        # Step 4: Simulator display state
        self.assertTrue(sim.is_finished)
        self.assertEqual((sim.x, sim.y), (3, 3))
        self.assertEqual(sim.direction, "NORTH")
        self.assertFalse(sim.display_pen_down)
        self.assertEqual(sim.display_speed, 2)
        # 3 movements were made while pen was down: (0,0)->(0,4), (0,4)->(3,4), (3,4)->(3,3)
        self.assertEqual(len(sim.trails), 3)
        self.assertEqual(sim.trails[0], ((0, 0), (0, 4)))
        self.assertEqual(sim.trails[1], ((0, 4), (3, 4)))
        self.assertEqual(sim.trails[2], ((3, 4), (3, 3)))


if __name__ == "__main__":
    unittest.main()
