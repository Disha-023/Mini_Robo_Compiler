
import unittest
from compiler.lexer import Lexer


class TestAllLexerFeatures(unittest.TestCase):

    def get_types(self, source):
        return [token.token_type for token in Lexer(source).tokenize()]

    def test_every_keyword(self):
        for keyword, expected_type in Lexer.KEYWORDS.items():
            with self.subTest(keyword=keyword):
                tokens = Lexer(keyword).tokenize()
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].token_type, expected_type)
                self.assertEqual(tokens[0].value, keyword)

    def test_every_single_operator(self):
        for symbol, expected_type in Lexer.OPERATORS.items():
            with self.subTest(operator=symbol):
                tokens = Lexer(symbol).tokenize()
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].token_type, expected_type)

    def test_every_double_operator(self):
        for symbol, expected_type in Lexer.DOUBLE_OPERATORS.items():
            with self.subTest(operator=symbol):
                tokens = Lexer(symbol).tokenize()
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].token_type, expected_type)

    def test_identifiers(self):
        source = "steps robot_speed2 _counter"
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            [token.token_type for token in tokens],
            ["IDENTIFIER", "IDENTIFIER", "IDENTIFIER"]
        )
        self.assertEqual(
            [token.value for token in tokens],
            ["steps", "robot_speed2", "_counter"]
        )

    def test_integer_numbers(self):
        tokens = Lexer("0 5 12345").tokenize()

        self.assertEqual(
            [token.value for token in tokens],
            [0, 5, 12345]
        )
        self.assertTrue(
            all(token.token_type == "NUMBER" for token in tokens)
        )

    def test_strings_and_escapes(self):
        source = r'"Hello" "A\nB" "A\tB" "Say \"Hi\"" "A\\B"'
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            [token.value for token in tokens],
            ["Hello", "A\nB", "A\tB", 'Say "Hi"', "A\\B"]
        )
        self.assertTrue(
            all(token.token_type == "STRING" for token in tokens)
        )

    def test_comments(self):
        source = "MOVE 5 // ignored\nBACK 2"
        self.assertEqual(
            self.get_types(source),
            ["MOVE", "NUMBER", "BACK", "NUMBER"]
        )

    def test_case_insensitive_keywords(self):
        self.assertEqual(
            self.get_types("move Move MOVE"),
            ["MOVE", "MOVE", "MOVE"]
        )

    def test_line_and_column(self):
        tokens = Lexer("MOVE 5\n  BACK 2").tokenize()

        self.assertEqual(
            [(t.line, t.column) for t in tokens],
            [(1, 1), (1, 6), (2, 3), (2, 8)]
        )

    def test_unknown_character(self):
        with self.assertRaisesRegex(SyntaxError, "Unknown character"):
            Lexer("MOVE @").tokenize()

    def test_unterminated_string(self):
        with self.assertRaisesRegex(SyntaxError, "Unterminated string"):
            Lexer('PRINT "Hello').tokenize()

    def test_invalid_escape(self):
        with self.assertRaisesRegex(SyntaxError, "Invalid escape sequence"):
            Lexer(r'PRINT "Hello\q"').tokenize()

    def test_tokenize_can_run_twice(self):
        lexer = Lexer("MOVE 5")

        first = lexer.tokenize()
        second = lexer.tokenize()

        self.assertEqual(
            [(t.token_type, t.value) for t in first],
            [(t.token_type, t.value) for t in second]
        )
        self.assertEqual(len(second), 2)

    def test_complete_lexer_program(self):
        source = """
        START
        LET steps = 5
        IF TRUE AND NOT FALSE {
            SPEED 2
            PEN_DOWN
            MOVE steps
        } ELSE {
            BACK 2
        }
        WHILE steps < 10 OR OBSTACLE_AHEAD {
            steps = steps + 1
        }
        FUNC draw(n) {
            REPEAT 4 {
                TURN RIGHT
                TURN LEFT
            }
        }
        draw(5)
        POSITION
        PEN_UP
        PRINT "Done"
        STOP
        """

        tokens = Lexer(source).tokenize()
        types = {token.token_type for token in tokens}

        expected = {
            "START", "STOP", "LET", "IDENTIFIER",
            "ASSIGN", "NUMBER", "IF", "TRUE",
            "AND", "NOT", "FALSE", "LEFT_BRACE",
            "RIGHT_BRACE", "SPEED", "PEN_DOWN",
            "MOVE", "ELSE", "BACK", "WHILE",
            "LT", "OR", "OBSTACLE_AHEAD",
            "PLUS", "FUNC", "LEFT_PAREN",
            "RIGHT_PAREN", "REPEAT", "TURN",
            "RIGHT", "LEFT", "POSITION",
            "PEN_UP", "PRINT", "STRING"
        }

        self.assertTrue(expected.issubset(types))


if __name__ == "__main__":
    unittest.main()
