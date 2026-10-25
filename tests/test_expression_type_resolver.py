import unittest

from compiler.semantic import ExpressionTypeResolver
from compiler.symbol_table import SymbolTable


class TestExpressionTypeResolver(unittest.TestCase):

    def setUp(self):
        self.symbol_table = SymbolTable()
        self.resolver = ExpressionTypeResolver(self.symbol_table)

    def test_resolve_integer_variable(self):
        self.symbol_table.declare("steps", "INT")

        self.assertEqual(
            self.resolver.resolve_identifier("steps"),
            "INT"
        )

    def test_resolve_float_variable(self):
        self.symbol_table.declare("distance", "FLOAT")

        self.assertEqual(
            self.resolver.resolve_identifier("distance"),
            "FLOAT"
        )

    def test_undeclared_variable_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "is not declared"
        ):
            self.resolver.resolve_identifier("missing")

    def test_integer_addition(self):
        self.assertEqual(
            self.resolver.resolve_arithmetic("INT", "+", "INT"),
            "INT"
        )

    def test_integer_division(self):
        self.assertEqual(
            self.resolver.resolve_arithmetic("INT", "/", "INT"),
            "FLOAT"
        )


if __name__ == "__main__":
    unittest.main()