class Token:
    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.token_type}, {self.value})"


class Lexer:
    KEYWORDS = {
        "START": "START",
        "STOP": "STOP",
        "MOVE": "MOVE",
        "TURN": "TURN",
        "LEFT": "LEFT",
        "RIGHT": "RIGHT",
        "REPEAT": "REPEAT"
    }

    def __init__(self, text):
        self.text = text
        self.position = 0
        self.tokens = []

    def read_word(self):
        start = self.position

        while (
            self.position < len(self.text)
            and self.text[self.position].isalpha()
        ):
            self.position += 1

        return self.text[start:self.position]

    def read_number(self):
        start = self.position

        while (
            self.position < len(self.text)
            and self.text[self.position].isdigit()
        ):
            self.position += 1

        return self.text[start:self.position]

    def tokenize(self):
        while self.position < len(self.text):

            current = self.text[self.position]

            # Ignore spaces and new lines
            if current.isspace():
                self.position += 1
                continue

            # Read words
            if current.isalpha():
                word = self.read_word()
                word = word.upper()

                if word in self.KEYWORDS:
                    self.tokens.append(
                        Token(self.KEYWORDS[word], word)
                    )
                else:
                    raise ValueError(
                        f"Unknown word: {word}"
                    )

                continue

            # Read numbers
            if current.isdigit():
                number = self.read_number()

                self.tokens.append(
                    Token("NUMBER", int(number))
                )

                continue

            # Left brace
            if current == "{":
                self.tokens.append(
                    Token("LEFT_BRACE", "{")
                )
                self.position += 1
                continue

            # Right brace
            if current == "}":
                self.tokens.append(
                    Token("RIGHT_BRACE", "}")
                )
                self.position += 1
                continue

            # Unknown character
            raise ValueError(
                f"Unknown character: {current}"
            )

        return self.tokens