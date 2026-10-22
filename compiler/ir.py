from compiler.ast import Program, Move, Turn, Repeat


class IRGenerator:

    def generate(self, program):
        instructions = []

        self.generate_commands(
            program.commands,
            instructions
        )

        return instructions

    def generate_commands(self, commands, instructions):

        for command in commands:

            if isinstance(command, Move):

                instructions.append(
                    ("MOVE", command.steps)
                )

            elif isinstance(command, Turn):

                instructions.append(
                    ("TURN", command.direction)
                )

            elif isinstance(command, Repeat):

                for _ in range(command.count):

                    self.generate_commands(
                        command.commands,
                        instructions
                    )