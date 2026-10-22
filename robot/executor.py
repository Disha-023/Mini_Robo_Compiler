from robot.robot import Robot


class RobotExecutor:

    def __init__(self):
        self.robot = Robot()

    def execute(self, instructions):

        for instruction in instructions:

            command = instruction[0]
            value = instruction[1]

            if command == "MOVE":

                self.robot.move(value)

            elif command == "TURN":

                if value == "LEFT":
                    self.robot.turn_left()

                elif value == "RIGHT":
                    self.robot.turn_right()

            self.robot.show_status()