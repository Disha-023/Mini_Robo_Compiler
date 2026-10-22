from compiler.ast import Program, Move, Turn, Repeat


class SemanticAnalyzer:

    def analyze(self, program):
        self.check_commands(program.commands)

        print("Semantic analysis successful!")

    def check_commands(self, commands):

        for command in commands:

            if isinstance(command, Move):
                self.check_move(command)

            elif isinstance(command, Turn):
                self.check_turn(command)

            elif isinstance(command, Repeat):
                self.check_repeat(command)

    def check_move(self, command):

        if command.steps <= 0:
            raise ValueError(
                "MOVE steps must be greater than 0"
            )

    def check_turn(self, command):

        if command.direction not in ["LEFT", "RIGHT"]:
            raise ValueError(
                "TURN direction must be LEFT or RIGHT"
            )

    def check_repeat(self, command):

        if command.count <= 0:
            raise ValueError(
                "REPEAT count must be greater than 0"
            )

        if len(command.commands) == 0:
            raise ValueError(
                "REPEAT must contain at least one command"
            )

        self.check_commands(command.commands)