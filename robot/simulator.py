import tkinter as tk


class RobotSimulator:

    def __init__(self, instructions):
        self.instructions = instructions

        self.x = 0
        self.y = 0
        self.direction = "NORTH"

        self.cell_size = 50

        self.root = tk.Tk()
        self.root.title("RoboLang Robot Simulator")

        self.canvas = tk.Canvas(
            self.root,
            width=600,
            height=600,
            bg="white"
        )

        self.canvas.pack()

        self.draw_grid()

    def draw_grid(self):
        for x in range(0, 601, self.cell_size):
            self.canvas.create_line(
                x, 0, x, 600
            )

        for y in range(0, 601, self.cell_size):
            self.canvas.create_line(
                0, y, 600, y
            )

    def draw_robot(self):
        self.canvas.delete("robot")

        screen_x = 300 + self.x * self.cell_size
        screen_y = 300 - self.y * self.cell_size

        self.canvas.create_oval(
            screen_x - 15,
            screen_y - 15,
            screen_x + 15,
            screen_y + 15,
            fill="blue",
            tags="robot"
        )

        self.canvas.create_text(
            screen_x,
            screen_y,
            text="R",
            fill="white",
            tags="robot"
        )

    def execute_next(self, index=0):
        if index >= len(self.instructions):
            print("\nSimulation finished!")
            return

        command, value = self.instructions[index]

        if command == "MOVE":

            if self.direction == "NORTH":
                self.y += value

            elif self.direction == "EAST":
                self.x += value

            elif self.direction == "SOUTH":
                self.y -= value

            elif self.direction == "WEST":
                self.x -= value

        elif command == "TURN":

            if value == "LEFT":

                if self.direction == "NORTH":
                    self.direction = "WEST"

                elif self.direction == "WEST":
                    self.direction = "SOUTH"

                elif self.direction == "SOUTH":
                    self.direction = "EAST"

                elif self.direction == "EAST":
                    self.direction = "NORTH"

            elif value == "RIGHT":

                if self.direction == "NORTH":
                    self.direction = "EAST"

                elif self.direction == "EAST":
                    self.direction = "SOUTH"

                elif self.direction == "SOUTH":
                    self.direction = "WEST"

                elif self.direction == "WEST":
                    self.direction = "NORTH"

        self.draw_robot()

        print(
            f"Position: ({self.x}, {self.y}), "
            f"Direction: {self.direction}"
        )

        self.root.after(
            500,
            lambda: self.execute_next(index + 1)
        )

    def run(self):
        self.draw_robot()

        self.execute_next()

        self.root.mainloop()