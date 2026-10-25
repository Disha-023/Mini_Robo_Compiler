import unittest

from compiler.semantic import TypeChecker


class TestTypeChecker(unittest.TestCase):

    def test_integer_addition(self):
        result = TypeChecker.arithmetic_result("INT", "+", "INT")
        self.assertEqual(result, "INT")

    def test_mixed_integer_float_addition(self):
        result = TypeChecker.arithmetic_result("INT", "+", "FLOAT")
        self.assertEqual(result, "FLOAT")

    def test_float_addition(self):
        result = TypeChecker.arithmetic_result("FLOAT", "+", "FLOAT")
        self.assertEqual(result, "FLOAT")

    def test_division_returns_float(self):
        result = TypeChecker.arithmetic_result("INT", "/", "INT")
        self.assertEqual(result, "FLOAT")

    def test_string_arithmetic_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "numeric operands"):
            TypeChecker.arithmetic_result("STRING", "+", "INT")

    def test_boolean_arithmetic_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "numeric operands"):
            TypeChecker.arithmetic_result("BOOL", "*", "INT")

    def test_check_numeric_rejects_string(self):
        with self.assertRaisesRegex(ValueError, "numeric type"):
            TypeChecker.check_numeric("STRING", "MOVE")

    def test_invalid_arithmetic_operator(self):
        with self.assertRaisesRegex(
            ValueError,
            "Unsupported arithmetic operator"
    ):
            TypeChecker.arithmetic_result("INT", "^", "INT")

    def test_integer_comparison_returns_bool(self):
        self.assertEqual(
            TypeChecker.comparison_result("INT", ">=", "INT"),
            "BOOL"
        )

    def test_float_comparison_returns_bool(self):
        self.assertEqual(
            TypeChecker.comparison_result("FLOAT", "<", "INT"),
            "BOOL"
        )

    def test_ordered_string_comparison_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "requires numeric operands"
        ):
            TypeChecker.comparison_result("STRING", "<", "STRING")

    def test_equality_requires_matching_types(self):
        with self.assertRaisesRegex(
            ValueError,
            "requires matching operand types"
        ):
            TypeChecker.comparison_result("INT", "==", "STRING")

    def test_boolean_condition_check(self):
        TypeChecker.check_boolean("BOOL", "IF condition")

    def test_non_boolean_condition_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "requires BOOL"
        ):
            TypeChecker.check_boolean("INT", "IF condition")



if __name__ == "__main__":
    unittest.main()