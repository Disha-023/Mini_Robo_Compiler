
import unittest

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.ast import (
    Program, Move, Turn, Repeat,
    VariableDeclaration, If, Back,
    FunctionDefinition, FunctionCall, Print
)


def parse_source(source):
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


class TestParser(unittest.TestCase):

    def test_basic_commands(self):
        program = parse_source(
            "START MOVE 3 TURN RIGHT STOP"
        )

        self.assertIsInstance(program, Program)
        self.assertEqual(len(program.commands), 2)
        self.assertIsInstance(program.commands[0], Move)
        self.assertEqual(program.commands[0].steps, 3)
        self.assertIsInstance(program.commands[1], Turn)
        self.assertEqual(program.commands[1].direction, "RIGHT")

    def test_repeat_block(self):
        program = parse_source(
            "START REPEAT 2 { MOVE 3 TURN LEFT } STOP"
        )

        repeat = program.commands[0]
        self.assertIsInstance(repeat, Repeat)
        self.assertEqual(repeat.count, 2)
        self.assertEqual(len(repeat.commands), 2)

    def test_variable_and_if_else(self):
        program = parse_source(
            "START "
            "LET steps = 5 "
            "IF steps >= 3 { MOVE steps } ELSE { BACK 2 } "
            "STOP"
        )

        self.assertIsInstance(program.commands[0], VariableDeclaration)
        self.assertEqual(program.commands[0].name, "steps")
        self.assertIsInstance(program.commands[1], If)
        self.assertEqual(len(program.commands[1].then_commands), 1)
        self.assertIsInstance(program.commands[1].else_commands[0], Back)

    def test_function_definition_and_call(self):
        program = parse_source(
            "START "
            "FUNC draw(size) { MOVE size } "
            "draw(5) "
            "STOP"
        )

        self.assertIsInstance(program.commands[0], FunctionDefinition)
        self.assertEqual(program.commands[0].name, "draw")
        self.assertEqual(program.commands[0].parameters, ["size"])
        self.assertIsInstance(program.commands[1], FunctionCall)
        self.assertEqual(program.commands[1].name, "draw")

    def test_print_string(self):
        program = parse_source(
            'START PRINT "Hello robot" STOP'
        )

        self.assertIsInstance(program.commands[0], Print)

    def test_missing_stop_is_rejected(self):
        with self.assertRaises(SyntaxError):
            parse_source("START MOVE 3")

    def test_invalid_command_is_rejected(self):
        with self.assertRaises(SyntaxError):
            parse_source("START UNKNOWN STOP")


if __name__ == "__main__":
    unittest.main()
