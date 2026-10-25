class Robot:
    """Robot runtime model for RoboLang.

    Tracks robot coordinates (x, y), heading direction, pen state,
    movement speed, obstacles, and a chronological history of actions.
    """

    def __init__(self, obstacles=None):
        self.x = 0
        self.y = 0
        self.direction = "NORTH"
        self.pen_down_state = False
        self.speed_val = 1
        self.obstacles = set(obstacles) if obstacles is not None else set()
        self.history = []

    @property
    def is_pen_down(self):
        return self.pen_down_state

    @is_pen_down.setter
    def is_pen_down(self, value):
        self.pen_down_state = bool(value)

    @property
    def speed_value(self):
        return self.speed_val

    @speed_value.setter
    def speed_value(self, value):
        self.speed_val = value

    def add_obstacle(self, x, y):
        """Add an obstacle at the given (x, y) grid coordinates."""
        self.obstacles.add((x, y))

    def move(self, steps):
        """Move forward by `steps` along the current heading."""
        start_x, start_y = self.x, self.y

        if self.direction == "NORTH":
            self.y += steps
        elif self.direction == "EAST":
            self.x += steps
        elif self.direction == "SOUTH":
            self.y -= steps
        elif self.direction == "WEST":
            self.x -= steps

        self.history.append({
            "type": "MOVE",
            "from": (start_x, start_y),
            "to": (self.x, self.y),
            "steps": steps,
            "direction": self.direction,
            "pen_down": self.pen_down_state,
            "speed": self.speed_val,
        })

    def back(self, steps):
        """Move backward by `steps` opposite to the current heading."""
        start_x, start_y = self.x, self.y

        if self.direction == "NORTH":
            self.y -= steps
        elif self.direction == "EAST":
            self.x -= steps
        elif self.direction == "SOUTH":
            self.y += steps
        elif self.direction == "WEST":
            self.x += steps

        self.history.append({
            "type": "BACK",
            "from": (start_x, start_y),
            "to": (self.x, self.y),
            "steps": steps,
            "direction": self.direction,
            "pen_down": self.pen_down_state,
            "speed": self.speed_val,
        })

    def turn_left(self):
        """Rotate heading 90 degrees counter-clockwise."""
        old_dir = self.direction
        if self.direction == "NORTH":
            self.direction = "WEST"
        elif self.direction == "WEST":
            self.direction = "SOUTH"
        elif self.direction == "SOUTH":
            self.direction = "EAST"
        elif self.direction == "EAST":
            self.direction = "NORTH"

        self.history.append({
            "type": "TURN",
            "direction": "LEFT",
            "from_dir": old_dir,
            "to_dir": self.direction,
            "pos": (self.x, self.y),
        })

    def turn_right(self):
        """Rotate heading 90 degrees clockwise."""
        old_dir = self.direction
        if self.direction == "NORTH":
            self.direction = "EAST"
        elif self.direction == "EAST":
            self.direction = "SOUTH"
        elif self.direction == "SOUTH":
            self.direction = "WEST"
        elif self.direction == "WEST":
            self.direction = "NORTH"

        self.history.append({
            "type": "TURN",
            "direction": "RIGHT",
            "from_dir": old_dir,
            "to_dir": self.direction,
            "pos": (self.x, self.y),
        })

    def turn(self, direction):
        """Turn in the specified direction ('LEFT' or 'RIGHT')."""
        if direction == "LEFT":
            self.turn_left()
        elif direction == "RIGHT":
            self.turn_right()
        else:
            raise ValueError(f"Invalid turn direction: {direction}")

    def speed(self, val):
        """Set the robot movement speed."""
        self.speed_val = val
        self.history.append({
            "type": "SPEED",
            "value": val,
        })

    def pen_up(self):
        """Lift the pen up (disables drawing trails)."""
        self.pen_down_state = False
        self.history.append({
            "type": "PEN_UP",
            "pen_down": False,
            "pos": (self.x, self.y),
        })

    def pen_down(self):
        """Lower the pen down (enables drawing trails)."""
        self.pen_down_state = True
        self.history.append({
            "type": "PEN_DOWN",
            "pen_down": True,
            "pos": (self.x, self.y),
        })

    def position(self):
        """Display and return the current position (x, y)."""
        self.show_status()
        self.history.append({
            "type": "POSITION",
            "pos": (self.x, self.y),
            "direction": self.direction,
        })
        return (self.x, self.y)

    def obstacle_ahead(self):
        """Check if an obstacle is immediately one step ahead in current direction.

        Returns:
            bool: True if an obstacle exists at the adjacent cell ahead, else False.
        """
        if self.direction == "NORTH":
            target = (self.x, self.y + 1)
        elif self.direction == "EAST":
            target = (self.x + 1, self.y)
        elif self.direction == "SOUTH":
            target = (self.x, self.y - 1)
        elif self.direction == "WEST":
            target = (self.x - 1, self.y)
        else:
            return False

        return target in self.obstacles

    def reset(self):
        """Reset the robot back to origin (0, 0), NORTH, pen up, speed 1, and clear history.

        Note: obstacles configuration is preserved across resets.
        """
        self.x = 0
        self.y = 0
        self.direction = "NORTH"
        self.pen_down_state = False
        self.speed_val = 1
        self.history.clear()

    def show_status(self):
        """Print current position and direction to console."""
        print(
            f"Position: ({self.x}, {self.y}), "
            f"Direction: {self.direction}"
        )