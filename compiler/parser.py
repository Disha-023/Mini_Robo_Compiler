from compiler.ast import Program, Move, Turn, Repeat


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]

        return None

    def advance(self):
        self.position += 1

    def expect(self, token_type):
        token = self.current_token()

        if token is None:
            raise SyntaxError(
                f"Expected {token_type}, "
                "but reached end of program"
            )

        if token.token_type != token_type:
            raise SyntaxError(
                f"Expected {token_type}, "
                f"but found {token.token_type}"
            )

        self.advance()

        return token

    def parse(self):
        self.expect("START")

        commands = self.parse_commands()

        self.expect("STOP")

        if self.current_token() is not None:
            raise SyntaxError(
                f"Unexpected token: {self.current_token()}"
            )

        return Program(commands)

    def parse_commands(self):
        commands = []

        while (
            self.current_token() is not None
            and self.current_token().token_type
            not in ["STOP", "RIGHT_BRACE"]
        ):
            command = self.parse_command()
            commands.append(command)

        return commands

    def parse_command(self):
        token = self.current_token()

        if token.token_type == "MOVE":
            return self.parse_move()

        elif token.token_type == "TURN":
            return self.parse_turn()

        elif token.token_type == "REPEAT":
            return self.parse_repeat()

        else:
            raise SyntaxError(
                f"Unexpected token: {token}"
            )

    def parse_move(self):
        self.expect("MOVE")

        number_token = self.expect("NUMBER")

        return Move(number_token.value)

    def parse_turn(self):
        self.expect("TURN")

        token = self.current_token()

        if token is None:
            raise SyntaxError(
                "Expected LEFT or RIGHT after TURN"
            )

        if token.token_type == "LEFT":
            self.advance()
            return Turn("LEFT")

        elif token.token_type == "RIGHT":
            self.advance()
            return Turn("RIGHT")

        else:
            raise SyntaxError(
                "Expected LEFT or RIGHT after TURN"
            )

    def parse_repeat(self):
        self.expect("REPEAT")

        number_token = self.expect("NUMBER")

        self.expect("LEFT_BRACE")

        commands = self.parse_commands()

        self.expect("RIGHT_BRACE")

        return Repeat(
            number_token.value,
            commands
        )