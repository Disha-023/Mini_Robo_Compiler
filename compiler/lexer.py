class Token:
    def __init__(self, token_type, value, line=1, column=1):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return (
            f"Token({self.token_type}, {self.value!r}, "
            f"line={self.line}, column={self.column})"
        )


class Lexer:

    # All supported RoboLang keywords
    KEYWORDS = {
        "START": "START",
        "STOP": "STOP",
        "MOVE": "MOVE",
        "BACK": "BACK",
        "TURN": "TURN",
        "LEFT": "LEFT",
        "RIGHT": "RIGHT",
        "REPEAT": "REPEAT",
        "SPEED": "SPEED",
        "POSITION": "POSITION",
        "PEN_UP": "PEN_UP",
        "PEN_DOWN": "PEN_DOWN",
        "LET": "LET",
        "IF": "IF",
        "ELSE": "ELSE",
        "WHILE": "WHILE",
        "PRINT": "PRINT",
        "FUNC": "FUNC",
        "AND": "AND",
        "OR": "OR",
        "NOT": "NOT",
        "TRUE": "TRUE",
        "FALSE": "FALSE",
        "OBSTACLE_AHEAD": "OBSTACLE_AHEAD"
    }

    # Single-character operators and punctuation
    OPERATORS = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "MULTIPLY",
        "/": "DIVIDE",
        "=": "ASSIGN",
        ">": "GT",
        "<": "LT",
        "(": "LEFT_PAREN",
        ")": "RIGHT_PAREN",
        "{": "LEFT_BRACE",
        "}": "RIGHT_BRACE",
        ",": "COMMA"
    }

    # Two-character operators
    DOUBLE_OPERATORS = {
        "==": "EQ",
        "!=": "NE",
        ">=": "GE",
        "<=": "LE"
    }

    def __init__(self, text):
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    # Return current character
    def current_char(self):
        if self.position >= len(self.text):
            return None
        return self.text[self.position]

    # Look at next character without moving
    def peek(self):
        next_position = self.position + 1

        if next_position >= len(self.text):
            return None

        return self.text[next_position]

    # Move to next character and update position
    def advance(self):
        char = self.current_char()

        if char is None:
            return

        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

    # Store a recognized token
    def add_token(self, token_type, value, line, column):
        self.tokens.append(
            Token(token_type, value, line, column)
        )

    # Read keywords and identifiers
    def read_word(self):
        start = self.position

        while (
            self.current_char() is not None
            and (
                self.current_char().isalnum()
                or self.current_char() == "_"
            )
        ):
            self.advance()

        return self.text[start:self.position]

    # Read integer numbers
    def read_number(self):
        start = self.position

        while (
            self.current_char() is not None
            and self.current_char().isdigit()
        ):
            self.advance()

        return int(self.text[start:self.position])

    # Read string literals
    def read_string(self):
        start_line = self.line
        start_column = self.column

        self.advance()  # Skip opening "

        characters = []

        while self.current_char() is not None:
            char = self.current_char()

            # Closing quotation mark
            if char == '"':
                self.advance()
                return "".join(characters)

            # Strings cannot contain raw newlines
            if char == "\n":
                raise SyntaxError(
                    f"Lexical error at line {start_line}, "
                    f"column {start_column}: "
                    "Unterminated string"
                )

            # Handle escape sequences
            if char == "\\":
                self.advance()

                escaped = self.current_char()

                escapes = {
                    "n": "\n",
                    "t": "\t",
                    '"': '"',
                    "\\": "\\"
                }

                if escaped not in escapes:
                    raise SyntaxError(
                        f"Lexical error at line {self.line}, "
                        f"column {self.column}: "
                        "Invalid escape sequence"
                    )

                characters.append(escapes[escaped])
                self.advance()
                continue

            characters.append(char)
            self.advance()

        raise SyntaxError(
            f"Lexical error at line {start_line}, "
            f"column {start_column}: "
            "Unterminated string"
        )

    # Main lexical analysis function
    def tokenize(self):

        # Reset state so tokenize() can be called again
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

        while self.current_char() is not None:

            current = self.current_char()

            start_line = self.line
            start_column = self.column

            # 1. Ignore spaces, tabs, and newlines
            if current.isspace():
                self.advance()
                continue

            # 2. Ignore // comments
            if current == "/" and self.peek() == "/":
                while (
                    self.current_char() is not None
                    and self.current_char() != "\n"
                ):
                    self.advance()

                continue

            # 3. Recognize keywords and identifiers
            if current.isalpha() or current == "_":

                word = self.read_word()
                upper_word = word.upper()

                if upper_word in self.KEYWORDS:
                    self.add_token(
                        self.KEYWORDS[upper_word],
                        upper_word,
                        start_line,
                        start_column
                    )
                else:
                    self.add_token(
                        "IDENTIFIER",
                        word,
                        start_line,
                        start_column
                    )

                continue

            # 4. Recognize numbers
            if current.isdigit():

                number = self.read_number()

                self.add_token(
                    "NUMBER",
                    number,
                    start_line,
                    start_column
                )

                continue

            # 5. Recognize strings
            if current == '"':

                string = self.read_string()

                self.add_token(
                    "STRING",
                    string,
                    start_line,
                    start_column
                )

                continue

            # 6. Check two-character operators first
            pair = current + (self.peek() or "")

            if pair in self.DOUBLE_OPERATORS:

                self.add_token(
                    self.DOUBLE_OPERATORS[pair],
                    pair,
                    start_line,
                    start_column
                )

                self.advance()
                self.advance()
                continue

            # 7. Recognize single-character operators
            if current in self.OPERATORS:

                self.add_token(
                    self.OPERATORS[current],
                    current,
                    start_line,
                    start_column
                )

                self.advance()
                continue

            # 8. Unknown character
            raise SyntaxError(
                f"Lexical error at line {start_line}, "
                f"column {start_column}: "
                f"Unknown character {current!r}"
            )

        return self.tokens
