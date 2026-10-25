import io
import sys
import unittest

from robot.robot import Robot


class TestRobot(unittest.TestCase):

    def setUp(self):
        self.robot = Robot()

    def test_initial_state(self):
        self.assertEqual(self.robot.x, 0)
        self.assertEqual(self.robot.y, 0)
        self.assertEqual(self.robot.direction, "NORTH")
        self.assertFalse(self.robot.pen_down_state)
        self.assertFalse(self.robot.is_pen_down)
        self.assertEqual(self.robot.speed_val, 1)
        self.assertEqual(self.robot.speed_value, 1)
        self.assertEqual(self.robot.obstacles, set())
        self.assertEqual(self.robot.history, [])

    def test_move_all_directions(self):
        # 1. NORTH: y increases
        self.robot.move(3)
        self.assertEqual((self.robot.x, self.robot.y), (0, 3))

        # 2. EAST: x increases
        self.robot.turn_right()
        self.robot.move(4)
        self.assertEqual((self.robot.x, self.robot.y), (4, 3))

        # 3. SOUTH: y decreases
        self.robot.turn_right()
        self.robot.move(2)
        self.assertEqual((self.robot.x, self.robot.y), (4, 1))

        # 4. WEST: x decreases
        self.robot.turn_right()
        self.robot.move(5)
        self.assertEqual((self.robot.x, self.robot.y), (-1, 1))

        # Verify movement history structure
        move_records = [r for r in self.robot.history if r["type"] == "MOVE"]
        self.assertEqual(len(move_records), 4)

        first_move = move_records[0]
        self.assertEqual(first_move["from"], (0, 0))
        self.assertEqual(first_move["to"], (0, 3))
        self.assertEqual(first_move["steps"], 3)
        self.assertEqual(first_move["direction"], "NORTH")
        self.assertFalse(first_move["pen_down"])
        self.assertEqual(first_move["speed"], 1)

    def test_back_all_directions(self):
        # 1. NORTH: moving backward decreases y
        self.robot.back(2)
        self.assertEqual((self.robot.x, self.robot.y), (0, -2))

        # 2. EAST: moving backward decreases x
        self.robot.turn_right()
        self.robot.back(3)
        self.assertEqual((self.robot.x, self.robot.y), (-3, -2))

        # 3. SOUTH: moving backward increases y
        self.robot.turn_right()
        self.robot.back(4)
        self.assertEqual((self.robot.x, self.robot.y), (-3, 2))

        # 4. WEST: moving backward increases x
        self.robot.turn_right()
        self.robot.back(1)
        self.assertEqual((self.robot.x, self.robot.y), (-2, 2))

        back_records = [r for r in self.robot.history if r["type"] == "BACK"]
        self.assertEqual(len(back_records), 4)
        first_back = back_records[0]
        self.assertEqual(first_back["from"], (0, 0))
        self.assertEqual(first_back["to"], (0, -2))
        self.assertEqual(first_back["steps"], 2)
        self.assertEqual(first_back["direction"], "NORTH")

    def test_turning_cycles(self):
        # Full counter-clockwise cycle (turn_left)
        self.robot.turn_left()
        self.assertEqual(self.robot.direction, "WEST")
        self.robot.turn_left()
        self.assertEqual(self.robot.direction, "SOUTH")
        self.robot.turn_left()
        self.assertEqual(self.robot.direction, "EAST")
        self.robot.turn_left()
        self.assertEqual(self.robot.direction, "NORTH")

        # Full clockwise cycle (turn_right)
        self.robot.turn_right()
        self.assertEqual(self.robot.direction, "EAST")
        self.robot.turn_right()
        self.assertEqual(self.robot.direction, "SOUTH")
        self.robot.turn_right()
        self.assertEqual(self.robot.direction, "WEST")
        self.robot.turn_right()
        self.assertEqual(self.robot.direction, "NORTH")

        # Generic turn dispatcher
        self.robot.turn("LEFT")
        self.assertEqual(self.robot.direction, "WEST")
        self.robot.turn("RIGHT")
        self.assertEqual(self.robot.direction, "NORTH")

        with self.assertRaises(ValueError):
            self.robot.turn("BACKWARD")

        # Verify turn history record
        turn_records = [r for r in self.robot.history if r["type"] == "TURN"]
        self.assertEqual(len(turn_records), 10)
        first_turn = turn_records[0]
        self.assertEqual(first_turn["direction"], "LEFT")
        self.assertEqual(first_turn["from_dir"], "NORTH")
        self.assertEqual(first_turn["to_dir"], "WEST")
        self.assertEqual(first_turn["pos"], (0, 0))

    def test_pen_state_and_trail_recording(self):
        self.assertFalse(self.robot.is_pen_down)

        self.robot.pen_down()
        self.assertTrue(self.robot.is_pen_down)
        self.assertTrue(self.robot.pen_down_state)

        self.robot.move(2)
        self.assertTrue(self.robot.history[-1]["pen_down"])

        self.robot.pen_up()
        self.assertFalse(self.robot.is_pen_down)
        self.assertFalse(self.robot.pen_down_state)

        self.robot.move(1)
        self.assertFalse(self.robot.history[-1]["pen_down"])

        pen_events = [r for r in self.robot.history if r["type"] in ("PEN_DOWN", "PEN_UP")]
        self.assertEqual(len(pen_events), 2)
        self.assertEqual(pen_events[0]["type"], "PEN_DOWN")
        self.assertEqual(pen_events[1]["type"], "PEN_UP")

    def test_speed_setting(self):
        self.assertEqual(self.robot.speed_val, 1)

        self.robot.speed(5)
        self.assertEqual(self.robot.speed_val, 5)
        self.assertEqual(self.robot.speed_value, 5)

        self.robot.move(2)
        self.assertEqual(self.robot.history[-1]["speed"], 5)

        speed_records = [r for r in self.robot.history if r["type"] == "SPEED"]
        self.assertEqual(len(speed_records), 1)
        self.assertEqual(speed_records[0]["value"], 5)

    def test_obstacle_ahead(self):
        # Default: no obstacles
        self.assertFalse(self.robot.obstacle_ahead())

        # Add obstacle ahead at (0, 1) when facing NORTH at (0, 0)
        self.robot.add_obstacle(0, 1)
        self.assertTrue(self.robot.obstacle_ahead())

        # Turn to EAST: obstacle is not ahead
        self.robot.turn_right()
        self.assertFalse(self.robot.obstacle_ahead())

        # Add obstacle at (1, 0)
        self.robot.add_obstacle(1, 0)
        self.assertTrue(self.robot.obstacle_ahead())

        # Initialize robot with obstacles
        robot_with_obs = Robot(obstacles=[(0, 1), (2, 2)])
        self.assertTrue(robot_with_obs.obstacle_ahead())
        robot_with_obs.move(1)  # now at (0, 1) facing NORTH
        self.assertFalse(robot_with_obs.obstacle_ahead())

    def test_position_and_show_status(self):
        self.robot.move(2)
        self.robot.turn_right()
        self.robot.move(3)

        captured_output = io.StringIO()
        old_stdout = sys.stdout
        try:
            sys.stdout = captured_output
            pos = self.robot.position()
        finally:
            sys.stdout = old_stdout

        self.assertEqual(pos, (3, 2))
        self.assertIn("Position: (3, 2), Direction: EAST", captured_output.getvalue())

        pos_records = [r for r in self.robot.history if r["type"] == "POSITION"]
        self.assertEqual(len(pos_records), 1)
        self.assertEqual(pos_records[0]["pos"], (3, 2))
        self.assertEqual(pos_records[0]["direction"], "EAST")

    def test_reset(self):
        self.robot.add_obstacle(5, 5)
        self.robot.move(4)
        self.robot.turn_right()
        self.robot.pen_down()
        self.robot.speed(3)
        self.assertGreater(len(self.robot.history), 0)

        self.robot.reset()

        self.assertEqual(self.robot.x, 0)
        self.assertEqual(self.robot.y, 0)
        self.assertEqual(self.robot.direction, "NORTH")
        self.assertFalse(self.robot.is_pen_down)
        self.assertEqual(self.robot.speed_val, 1)
        self.assertEqual(self.robot.history, [])
        # Obstacles should be preserved across reset
        self.assertIn((5, 5), self.robot.obstacles)


if __name__ == "__main__":
    unittest.main()
