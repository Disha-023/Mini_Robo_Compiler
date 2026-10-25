
import unittest

from compiler.ast import Program, Move, Turn, Repeat
from compiler.semantic import SemanticAnalyzer


class TestSemanticAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = SemanticAnalyzer()

    def test_valid_move(self):
        self.analyzer.analyze(Program([Move(5)]))

    def test_invalid_move(self):
        with self.assertRaisesRegex(ValueError, "greater than 0"):
            self.analyzer.analyze(Program([Move(0)]))

    def test_invalid_turn(self):
        with self.assertRaisesRegex(ValueError, "LEFT or RIGHT"):
            self.analyzer.analyze(Program([Turn("UP")]))

    def test_invalid_repeat_count(self):
        with self.assertRaisesRegex(ValueError, "greater than 0"):
            self.analyzer.analyze(Program([Repeat(0, [Move(1)])]))

    def test_empty_repeat(self):
        with self.assertRaisesRegex(ValueError, "at least one command"):
            self.analyzer.analyze(Program([Repeat(2, [])]))

    def test_nested_repeat(self):
        program = Program([
            Repeat(2, [Move(3), Turn("LEFT")])
        ])
        self.analyzer.analyze(program)

    def test_unsupported_command(self):
        class UnknownCommand:
            pass

        with self.assertRaisesRegex(ValueError, "Unsupported command"):
            self.analyzer.analyze(Program([UnknownCommand()]))

    def test_invalid_program_node(self):
        with self.assertRaisesRegex(ValueError, "Program node"):
            self.analyzer.analyze([])


if __name__ == "__main__":
    unittest.main()
