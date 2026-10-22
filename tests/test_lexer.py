import unittest
from compiler.lexer import Lexer


class TestLexer(unittest.TestCase):

    def test_basic_commands(self):
        tokens = Lexer("START MOVE 3 TURN RIGHT STOP").tokenize()
        types = [t.token_type for t in tokens]

        self.assertEqual(types, [
            "START", "MOVE", "NUMBER",
            "TURN", "RIGHT", "STOP"
        ])

    def test_operators(self):
        tokens = Lexer(
            "a == b != c >= d <= e + f - g * h / i"
        ).tokenize()

        types = [t.token_type for t in tokens]

        for operator in [
            "EQ", "NE", "GE", "LE",
            "PLUS", "MINUS", "MULTIPLY", "DIVIDE"
        ]:
            self.assertIn(operator, types)

    def test_comments(self):
        tokens = Lexer(
            "MOVE 2 // comment\nTURN LEFT"
        ).tokenize()

        self.assertEqual(
            [t.token_type for t in tokens],
            ["MOVE", "NUMBER", "TURN", "LEFT"]
        )

    def test_unknown_character(self):
        with self.assertRaisesRegex(
            SyntaxError, r"line 2, column 6"
        ):
            Lexer("START\nMOVE @\nSTOP").tokenize()

    def test_unterminated_string(self):
        with self.assertRaisesRegex(
            SyntaxError, "Unterminated string"
        ):
            Lexer('PRINT "Hello').tokenize()

    def test_line_numbers(self):
        tokens = Lexer("START\nMOVE 5\nSTOP").tokenize()

        self.assertEqual(tokens[1].line, 2)
        self.assertEqual(tokens[1].column, 1)


if __name__ == "__main__":
    unittest.main()