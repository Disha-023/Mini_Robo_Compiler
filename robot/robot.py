class Robot:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.direction = "NORTH"

    def move(self, steps):
        if self.direction == "NORTH":
            self.y += steps

        elif self.direction == "EAST":
            self.x += steps

        elif self.direction == "SOUTH":
            self.y -= steps

        elif self.direction == "WEST":
            self.x -= steps

    def turn_left(self):
        if self.direction == "NORTH":
            self.direction = "WEST"

        elif self.direction == "WEST":
            self.direction = "SOUTH"

        elif self.direction == "SOUTH":
            self.direction = "EAST"

        elif self.direction == "EAST":
            self.direction = "NORTH"

    def turn_right(self):
        if self.direction == "NORTH":
            self.direction = "EAST"

        elif self.direction == "EAST":
            self.direction = "SOUTH"

        elif self.direction == "SOUTH":
            self.direction = "WEST"

        elif self.direction == "WEST":
            self.direction = "NORTH"

    def show_status(self):
        print(
            f"Position: ({self.x}, {self.y}), "
            f"Direction: {self.direction}"
        )