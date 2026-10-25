import math
import tkinter as tk

from robot.robot import Robot


class RobotSimulator:
    """2D Grid Simulator for RoboLang robots.

    Animates the recorded action history of a robot, including position changes,
    directional headings, pen trails, and variable speeds.
    """

    def __init__(self, target=None, root=None, cell_size=50, headless=False):
        self.cell_size = cell_size
        self.headless = headless
        self.target_robot = None
        self.actions = []

        # Playback display state
        self.display_x = 0
        self.display_y = 0
        self.display_direction = "NORTH"
        self.display_pen_down = False
        self.display_speed = 1
        self.trails = []
        self.after_id = None
        self.current_step = 0
        self.is_finished = False

        self._extract_actions(target)

        self.root = None
        self.canvas = None

        if not self.headless:
            try:
                self.root = root if root is not None else tk.Tk()
                self.root.title("RoboLang Robot Simulator")

                self.canvas = tk.Canvas(
                    self.root,
                    width=600,
                    height=600,
                    bg="white"
                )
                self.canvas.pack()
                self.draw_grid()
            except Exception:
                # Fallback to headless if display is unavailable
                self.root = None
                self.canvas = None
                self.headless = True

    @property
    def x(self):
        return self.display_x

    @property
    def y(self):
        return self.display_y

    @property
    def direction(self):
        return self.display_direction

    def _validate_coord(self, pos, default=(0, 0)):
        """Safely validate that pos is a coordinate pair of numbers."""
        if isinstance(pos, (tuple, list)) and len(pos) >= 2:
            try:
                x = float(pos[0])
                y = float(pos[1])
                if math.isfinite(x) and math.isfinite(y):
                    return (int(x) if x.is_integer() else x, int(y) if y.is_integer() else y)
            except (ValueError, TypeError, OverflowError):
                pass
        return default

    def _extract_actions(self, target):
        """Extract action history from a Robot instance, an action list, or legacy IR instructions.

        Preferred interface:
            RobotSimulator(robot) where `robot` is a pre-executed Robot instance.
            The simulator only replays that robot's recorded history and never re-executes the program.

        Backward-compatibility interface:
            RobotSimulator(instructions) where `instructions` is an IR instruction list.
            NOTE: Passing IR instructions causes the simulator to execute them once internally
            via RobotExecutor to derive the action history for replay.
        """
        if target is None:
            self.actions = []
        elif isinstance(target, Robot):
            # Pre-executed Robot: replay its history directly without executing again
            self.target_robot = target
            self.actions = list(target.history)
        elif isinstance(target, list):
            if not target:
                self.actions = []
            elif isinstance(target[0], (tuple, list)):
                # Legacy IR instruction list: execute once via RobotExecutor to derive action history
                from robot.executor import RobotExecutor
                executor = RobotExecutor()
                executor.execute(target)
                self.target_robot = executor.robot
                self.actions = list(executor.robot.history)
            else:
                # Treat as action event list; individual events validated in process_event
                self.actions = list(target)
        else:
            raise TypeError(f"Unsupported simulator target type: {type(target)}")

    def to_screen_coords(self, x, y):
        """Convert robot grid coordinates (x, y) to canvas pixel coordinates."""
        try:
            x_val = float(x)
            y_val = float(y)
            if not (math.isfinite(x_val) and math.isfinite(y_val)):
                x_val, y_val = 0.0, 0.0
        except (ValueError, TypeError, OverflowError):
            x_val, y_val = 0.0, 0.0
        screen_x = 300 + x_val * self.cell_size
        screen_y = 300 - y_val * self.cell_size
        return (int(screen_x) if screen_x.is_integer() else screen_x,
                int(screen_y) if screen_y.is_integer() else screen_y)

    def draw_grid(self):
        """Draw the 50px grid lines across the 600x600 canvas."""
        if not self.canvas:
            return

        for x in range(0, 601, self.cell_size):
            self.canvas.create_line(x, 0, x, 600, fill="#e0e0e0")

        for y in range(0, 601, self.cell_size):
            self.canvas.create_line(0, y, 600, y, fill="#e0e0e0")

        # Center axes
        self.canvas.create_line(300, 0, 300, 600, fill="#c0c0c0", width=1)
        self.canvas.create_line(0, 300, 600, 300, fill="#c0c0c0", width=1)

    def draw_robot(self):
        """Draw the robot at its current display coordinates, including heading direction pointer."""
        if not self.canvas:
            return

        self.canvas.delete("robot")

        screen_x, screen_y = self.to_screen_coords(self.display_x, self.display_y)

        # Draw body circle
        self.canvas.create_oval(
            screen_x - 15,
            screen_y - 15,
            screen_x + 15,
            screen_y + 15,
            fill="blue",
            tags="robot"
        )

        # Draw heading direction pointer
        pts = None
        if self.display_direction == "NORTH":
            pts = [screen_x, screen_y - 22, screen_x - 6, screen_y - 14, screen_x + 6, screen_y - 14]
        elif self.display_direction == "EAST":
            pts = [screen_x + 22, screen_y, screen_x + 14, screen_y - 6, screen_x + 14, screen_y + 6]
        elif self.display_direction == "SOUTH":
            pts = [screen_x, screen_y + 22, screen_x - 6, screen_y + 14, screen_x + 6, screen_y + 14]
        elif self.display_direction == "WEST":
            pts = [screen_x - 22, screen_y, screen_x - 14, screen_y - 6, screen_x - 14, screen_y + 6]

        if pts:
            self.canvas.create_polygon(
                pts,
                fill="yellow",
                outline="black",
                tags="robot"
            )

        # Draw text label
        self.canvas.create_text(
            screen_x,
            screen_y,
            text="R",
            fill="white",
            tags="robot"
        )

    def draw_status(self):
        """Draw on-screen HUD status banner with position, direction, pen state, and speed."""
        if not self.canvas:
            return

        self.canvas.delete("status")
        status_text = (
            f"Position: ({self.display_x}, {self.display_y})  |  "
            f"Heading: {self.display_direction}  |  "
            f"Pen: {'DOWN' if self.display_pen_down else 'UP'}  |  "
            f"Speed: {self.display_speed}"
        )
        self.canvas.create_text(
            10, 15,
            anchor="w",
            text=status_text,
            fill="black",
            font=("Arial", 10, "bold"),
            tags="status"
        )

    def get_delay(self):
        """Compute step animation delay in milliseconds from speed setting with safeguards."""
        try:
            speed_val = float(self.display_speed)
            if speed_val <= 0:
                return 500
            delay = int(500 / speed_val)
            return max(50, min(2000, delay))
        except (ValueError, TypeError):
            return 500

    def process_event(self, event):
        """Process a single history event and update simulator display state."""
        if not isinstance(event, dict) or "type" not in event:
            print(f"Simulator warning: malformed event {event}, skipping.")
            return

        event_type = event["type"]

        if event_type in ("MOVE", "BACK"):
            fallback_pos = (self.display_x, self.display_y)
            from_pos = self._validate_coord(event.get("from"), fallback_pos)
            to_pos = self._validate_coord(event.get("to"), from_pos)
            if event.get("direction") is not None:
                self.display_direction = event["direction"]
            if event.get("pen_down") is not None:
                self.display_pen_down = bool(event["pen_down"])
            if event.get("speed") is not None:
                self.display_speed = event["speed"]

            if self.display_pen_down:
                trail_segment = (from_pos, to_pos)
                self.trails.append(trail_segment)
                if self.canvas:
                    sx1, sy1 = self.to_screen_coords(*from_pos)
                    sx2, sy2 = self.to_screen_coords(*to_pos)
                    self.canvas.create_line(
                        sx1, sy1, sx2, sy2,
                        fill="red", width=3, tags="trail"
                    )

            self.display_x, self.display_y = to_pos

        elif event_type == "TURN":
            pos = self._validate_coord(event.get("pos"), (self.display_x, self.display_y))
            self.display_x, self.display_y = pos
            if event.get("to_dir") is not None:
                self.display_direction = event["to_dir"]

        elif event_type in ("PEN_UP", "PEN_DOWN"):
            self.display_pen_down = bool(event.get("pen_down", event_type == "PEN_DOWN"))
            if "pos" in event and event["pos"] is not None:
                self.display_x, self.display_y = self._validate_coord(
                    event["pos"], (self.display_x, self.display_y)
                )

        elif event_type == "SPEED":
            if event.get("value") is not None:
                self.display_speed = event["value"]

        elif event_type == "POSITION":
            pos = self._validate_coord(event.get("pos"), (self.display_x, self.display_y))
            self.display_x, self.display_y = pos
            if event.get("direction") is not None:
                self.display_direction = event["direction"]
            print(
                f"Position: ({self.display_x}, {self.display_y}), "
                f"Direction: {self.display_direction}"
            )

        else:
            print(f"Simulator warning: unknown event type '{event_type}', skipping.")
            return

        if self.canvas:
            self.draw_robot()
            self.draw_status()

    def execute_next(self, index=0):
        """Execute the next history action in the animation sequence."""
        if index >= len(self.actions):
            self.is_finished = True
            print("\nSimulation finished!")
            return

        self.current_step = index
        event = self.actions[index]
        self.process_event(event)

        delay = self.get_delay()
        if self.root and not self.headless:
            self.after_id = self.root.after(
                delay,
                lambda: self.execute_next(index + 1)
            )

    def run(self):
        """Start the simulator animation and main event loop.

        In headless mode, processes all actions synchronously in chronological order.
        When a GUI root is present, animates asynchronously using root.after() and enters mainloop.
        """
        if self.headless or not self.root:
            for i, event in enumerate(self.actions):
                self.current_step = i
                self.process_event(event)
            self.is_finished = True
            print("\nSimulation finished!")
            return

        if self.canvas:
            self.draw_robot()
            self.draw_status()

        self.execute_next(0)
        self.root.mainloop()