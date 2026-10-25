import unittest

from compiler.symbol_table import SymbolTable


class TestSymbolTable(unittest.TestCase):

    def test_declare_and_lookup(self):
        table = SymbolTable()
        table.declare("count", "INT")
        self.assertEqual(table.lookup("count"), "INT")

    def test_duplicate_declaration(self):
        table = SymbolTable()
        table.declare("count", "INT")

        with self.assertRaisesRegex(ValueError, "already declared"):
            table.declare("count", "INT")

    def test_parent_scope_lookup(self):
        parent = SymbolTable()
        parent.declare("score", "INT")
        child = SymbolTable(parent)
        self.assertEqual(child.lookup("score"), "INT")

    def test_undeclared_variable(self):
        table = SymbolTable()

        with self.assertRaisesRegex(ValueError, "not declared"):
            table.lookup("unknown")

    def test_invalid_type(self):
        table = SymbolTable()

        with self.assertRaisesRegex(ValueError, "Invalid type"):
            table.declare("value", "CHAR")

    def test_exists_in_parent_scope(self):
        parent = SymbolTable()
        parent.declare("score", "INT")
        child = parent.create_child_scope()
        self.assertTrue(child.exists("score"))

    def test_exists_only_in_current_scope(self):
        parent = SymbolTable()
        parent.declare("score", "INT")
        child = parent.create_child_scope()

        self.assertFalse(child.exists_in_current_scope("score"))
        self.assertTrue(parent.exists_in_current_scope("score"))

    def test_child_scope_can_shadow_parent_variable(self):
        parent = SymbolTable()
        parent.declare("score", "INT")
        child = parent.create_child_scope()
        child.declare("score", "FLOAT")

        self.assertEqual(child.lookup("score"), "FLOAT")
        self.assertEqual(parent.lookup("score"), "INT")


if __name__ == "__main__":
    unittest.main()