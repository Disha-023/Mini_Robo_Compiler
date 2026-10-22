class CodeGenerator:

    def generate(self, instructions):

        code = []

        for instruction in instructions:

            command = instruction[0]
            value = instruction[1]

            if command == "MOVE":

                code.append(
                    f"robot.move({value})"
                )

            elif command == "TURN":

                if value == "LEFT":
                    code.append(
                        "robot.turn_left()"
                    )

                elif value == "RIGHT":
                    code.append(
                        "robot.turn_right()"
                    )

        return code