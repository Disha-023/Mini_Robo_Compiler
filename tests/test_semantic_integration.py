import unittest

from compiler.ast import (
    Program,
    Number,
    Variable,
    BinaryExpression,
    VariableDeclaration,
    Move,
    If,
    FunctionDefinition,
    FunctionCall,
)
from compiler.semantic import SemanticAnalyzer


class TestSemanticIntegration(unittest.TestCase):

    def test_variable_expression_and_condition(self):
        program = Program([
            VariableDeclaration("steps", Number(5)),
            If(
                BinaryExpression(
                    Variable("steps"),
                    "GE",
                    Number(3),
                ),
                [
                    Move(
                        BinaryExpression(
                            Variable("steps"),
                            "PLUS",
                            Number(2),
                        )
                    )
                ],
            ),
        ])

        SemanticAnalyzer().analyze(program)

    def test_undeclared_variable_is_rejected(self):
        program = Program([
            Move(Variable("unknown_steps")),
        ])

        with self.assertRaisesRegex(ValueError, "not declared"):
            SemanticAnalyzer().analyze(program)

    def test_valid_function_call(self):
        program = Program([
            FunctionDefinition(
                "move_robot",
                ["steps"],
                [Move(Variable("steps"))],
            ),
            FunctionCall("move_robot", [Number(5)]),
        ])

        SemanticAnalyzer().analyze(program)

    def test_undefined_function_call(self):
        program = Program([
            FunctionCall("missing_function", []),
        ])

        with self.assertRaisesRegex(ValueError, "is not defined"):
            SemanticAnalyzer().analyze(program)

    def test_function_call_with_too_few_arguments(self):
        program = Program([
            FunctionDefinition(
                "move_robot",
                ["steps", "distance"],
                [Move(Variable("steps"))],
            ),
            FunctionCall("move_robot", [Number(5)]),
        ])

        with self.assertRaisesRegex(ValueError, "expects 2 arguments"):
            SemanticAnalyzer().analyze(program)

    def test_function_call_with_too_many_arguments(self):
        program = Program([
            FunctionDefinition(
                "move_robot",
                ["steps"],
                [Move(Variable("steps"))],
            ),
            FunctionCall("move_robot", [Number(5), Number(2)]),
        ])

        with self.assertRaisesRegex(ValueError, "expects 1 arguments"):
            SemanticAnalyzer().analyze(program)

    def test_duplicate_function_definition(self):
        program = Program([
            FunctionDefinition("move_robot", [], [Move(1)]),
            FunctionDefinition("move_robot", [], [Move(2)]),
        ])

        with self.assertRaisesRegex(ValueError, "already defined"):
            SemanticAnalyzer().analyze(program)

    def test_duplicate_function_parameters(self):
        program = Program([
            FunctionDefinition(
                "move_robot",
                ["steps", "steps"],
                [Move(Variable("steps"))],
            ),
        ])

        with self.assertRaisesRegex(ValueError, "duplicate parameters"):
            SemanticAnalyzer().analyze(program)


if __name__ == "__main__":
    unittest.main()