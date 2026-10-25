import unittest

from compiler.ast import (
    Program, Move, Turn, Repeat, Back, Speed, PenUp, PenDown,
    Position, Number, String, Boolean, Variable, ObstacleAhead,
    UnaryExpression, BinaryExpression, VariableDeclaration,
    Assignment, Print, If, While, FunctionDefinition, FunctionCall,
    ASTNode
)
from compiler.ir import IRGenerator


class TestIRGenerator(unittest.TestCase):

    def setUp(self):
        self.ir_gen = IRGenerator()

    # A. Robot instructions
    def test_robot_instructions_basic(self):
        program = Program([
            Move(5),
            Back(3),
            Turn("LEFT"),
            Turn("RIGHT"),
            Speed(2),
            PenUp(),
            PenDown(),
            Position(),
        ])
        instructions = self.ir_gen.generate(program)

        expected = [
            ("MOVE", 5),
            ("BACK", 3),
            ("TURN", "LEFT"),
            ("TURN", "RIGHT"),
            ("SPEED", 2),
            ("PEN_UP", None),
            ("PEN_DOWN", None),
            ("POSITION", None),
        ]
        self.assertEqual(instructions, expected)

    def test_robot_instructions_with_expressions(self):
        program = Program([
            Move(Variable("steps")),
            Back(BinaryExpression(Variable("steps"), "PLUS", Number(1))),
            Speed(Variable("s")),
        ])
        instructions = self.ir_gen.generate(program)

        self.assertIn(("MOVE", "steps"), instructions)
        self.assertIn(("SPEED", "s"), instructions)

        # BACK should have an ADD instruction before BACK
        add_inst = [inst for inst in instructions if inst[0] == "ADD"]
        self.assertEqual(len(add_inst), 1)
        temp_var = add_inst[0][1]
        self.assertEqual(add_inst[0][2], "steps")
        self.assertEqual(add_inst[0][3], 1)
        self.assertIn(("BACK", temp_var), instructions)

    # B. Variables and expressions
    def test_variable_declarations_and_assignments(self):
        program = Program([
            VariableDeclaration("x", Number(10)),
            VariableDeclaration("flag", Boolean(True)),
            VariableDeclaration("msg", String("hello")),
            Assignment("x", Number(20)),
            Print(Variable("x")),
            Print(String("Robot finished")),
        ])
        instructions = self.ir_gen.generate(program)

        self.assertIn(("DECLARE", "x", 10), instructions)
        self.assertIn(("DECLARE", "flag", True), instructions)
        self.assertIn(("DECLARE", "msg", "'hello'"), instructions)
        self.assertIn(("ASSIGN", "x", 20), instructions)
        self.assertIn(("PRINT", "x"), instructions)
        self.assertIn(("PRINT", "'Robot finished'"), instructions)

    def test_variable_value_not_confused_with_name(self):
        # Ensure a variable named 'msg' and a string literal 'msg' are distinct
        program = Program([
            VariableDeclaration("msg", String("msg")),
            Assignment("msg", Variable("msg")),
        ])
        instructions = self.ir_gen.generate(program)

        # String literal is quoted; variable name is unquoted
        self.assertEqual(instructions[0], ("DECLARE", "msg", "'msg'"))
        self.assertEqual(instructions[1], ("ASSIGN", "msg", "msg"))

    def test_arithmetic_expressions(self):
        # (x + 3) * 2 - 1 / 1
        inner_add = BinaryExpression(Variable("x"), "PLUS", Number(3))
        mul_expr = BinaryExpression(inner_add, "MULTIPLY", Number(2))
        div_expr = BinaryExpression(Number(1), "DIVIDE", Number(1))
        sub_expr = BinaryExpression(mul_expr, "MINUS", div_expr)
        program = Program([
            VariableDeclaration("result", sub_expr)
        ])
        instructions = self.ir_gen.generate(program)

        # Verify operations
        opcodes = [inst[0] for inst in instructions]
        self.assertEqual(opcodes, ["ADD", "MUL", "DIV", "SUB", "DECLARE"])
        self.assertEqual(instructions[-1][0], "DECLARE")
        self.assertEqual(instructions[-1][1], "result")

    def test_comparisons_and_logicals(self):
        # steps >= 3 AND NOT OBSTACLE_AHEAD
        ge_expr = BinaryExpression(Variable("steps"), "GE", Number(3))
        not_obs = UnaryExpression("NOT", ObstacleAhead())
        and_expr = BinaryExpression(ge_expr, "AND", not_obs)
        program = Program([
            VariableDeclaration("can_move", and_expr)
        ])
        instructions = self.ir_gen.generate(program)

        opcodes = [inst[0] for inst in instructions]
        self.assertIn("GE", opcodes)
        self.assertIn("OBSTACLE_AHEAD", opcodes)
        self.assertIn("NOT", opcodes)
        self.assertIn("AND", opcodes)
        self.assertEqual(instructions[-1][0], "DECLARE")

    def test_unary_plus_and_minus(self):
        program = Program([
            VariableDeclaration("pos", UnaryExpression("PLUS", Number(5))),
            VariableDeclaration("neg", UnaryExpression("MINUS", Number(5))),
        ])
        instructions = self.ir_gen.generate(program)

        opcodes = [inst[0] for inst in instructions]
        self.assertIn("POS", opcodes)
        self.assertIn("NEG", opcodes)

    # C. Conditional statements
    def test_if_else(self):
        # IF steps >= 3 { MOVE 2 } ELSE { BACK 2 }
        cond = BinaryExpression(Variable("steps"), "GE", Number(3))
        program = Program([
            If(cond, [Move(2)], [Back(2)])
        ])
        instructions = self.ir_gen.generate(program)

        # Expected flow:
        # GE t0, steps, 3
        # JUMP_IF_FALSE t0, ELSE_1
        # MOVE 2
        # JUMP END_IF_1
        # LABEL ELSE_1
        # BACK 2
        # LABEL END_IF_1
        opcodes = [inst[0] for inst in instructions]
        self.assertEqual(opcodes, [
            "GE", "JUMP_IF_FALSE", "MOVE", "JUMP", "LABEL", "BACK", "LABEL"
        ])
        self.assertEqual(instructions[1][0], "JUMP_IF_FALSE")
        else_label = instructions[1][2]
        self.assertEqual(instructions[4], ("LABEL", else_label))
        end_label = instructions[3][1]
        self.assertEqual(instructions[6], ("LABEL", end_label))

    def test_if_without_else(self):
        cond = BinaryExpression(Variable("steps"), "GT", Number(0))
        program = Program([
            If(cond, [Turn("LEFT")])
        ])
        instructions = self.ir_gen.generate(program)

        opcodes = [inst[0] for inst in instructions]
        self.assertEqual(opcodes, ["GT", "JUMP_IF_FALSE", "TURN", "LABEL"])
        end_label = instructions[1][2]
        self.assertEqual(instructions[3], ("LABEL", end_label))

    def test_nested_if(self):
        inner_if = If(BinaryExpression(Variable("y"), "GT", Number(1)), [Move(1)])
        outer_if = If(BinaryExpression(Variable("x"), "GT", Number(0)), [inner_if])
        program = Program([outer_if])
        instructions = self.ir_gen.generate(program)

        labels = [inst[1] for inst in instructions if inst[0] == "LABEL"]
        # Outer and inner should have unique labels
        self.assertEqual(len(labels), len(set(labels)))

    # D. Loops
    def test_while_loop(self):
        # WHILE steps < 10 { steps = steps + 1 }
        cond = BinaryExpression(Variable("steps"), "LT", Number(10))
        body = [Assignment("steps", BinaryExpression(Variable("steps"), "PLUS", Number(1)))]
        program = Program([While(cond, body)])
        instructions = self.ir_gen.generate(program)

        # Check condition is evaluated INSIDE loop (after WHILE_START label)
        self.assertEqual(instructions[0][0], "LABEL")
        start_label = instructions[0][1]
        self.assertTrue(start_label.startswith("WHILE_START"))

        # Next is condition eval (LT)
        self.assertEqual(instructions[1][0], "LT")
        # Next is JUMP_IF_FALSE to WHILE_END
        self.assertEqual(instructions[2][0], "JUMP_IF_FALSE")
        end_label = instructions[2][2]
        self.assertTrue(end_label.startswith("WHILE_END"))

        # JUMP back to start_label
        jump_inst = [inst for inst in instructions if inst[0] == "JUMP"]
        self.assertEqual(jump_inst[0], ("JUMP", start_label))

        # Final instruction is end label
        self.assertEqual(instructions[-1], ("LABEL", end_label))

    def test_repeat_loop_counter(self):
        # REPEAT 4 { MOVE 1 }
        program = Program([
            Repeat(4, [Move(1)])
        ])
        instructions = self.ir_gen.generate(program)

        opcodes = [inst[0] for inst in instructions]
        # Should declare counter, check LT, jump on false, body, increment counter, jump to start
        self.assertIn("DECLARE", opcodes)
        self.assertIn("LABEL", opcodes)
        self.assertIn("LT", opcodes)
        self.assertIn("JUMP_IF_FALSE", opcodes)
        self.assertIn("MOVE", opcodes)
        self.assertIn("ADD", opcodes)
        self.assertIn("JUMP", opcodes)

    def test_repeat_loop_variable_count(self):
        # REPEAT n { MOVE size }
        program = Program([
            Repeat(Variable("n"), [Move(Variable("size"))])
        ])
        instructions = self.ir_gen.generate(program)

        # Find LT instruction: should compare counter against 'n'
        lt_inst = [inst for inst in instructions if inst[0] == "LT"]
        self.assertEqual(len(lt_inst), 1)
        self.assertEqual(lt_inst[0][3], "n")

    def test_nested_loops(self):
        # WHILE x > 0 { REPEAT 2 { MOVE 1 } }
        program = Program([
            While(
                BinaryExpression(Variable("x"), "GT", Number(0)),
                [Repeat(2, [Move(1)])]
            )
        ])
        instructions = self.ir_gen.generate(program)

        labels = [inst[1] for inst in instructions if inst[0] == "LABEL"]
        self.assertEqual(len(labels), len(set(labels)))
        self.assertTrue(any("WHILE_START" in l for l in labels))
        self.assertTrue(any("REPEAT_START" in l for l in labels))

    # E. Functions
    def test_function_definition_and_call(self):
        program = Program([
            FunctionDefinition("draw_square", ["size"], [
                Move(Variable("size")),
                Turn("RIGHT")
            ]),
            FunctionCall("draw_square", [Number(5)]),
        ])
        instructions = self.ir_gen.generate(program)

        self.assertIn(("FUNC_DEF", "draw_square", ["size"]), instructions)
        self.assertIn(("RETURN", None), instructions)
        self.assertIn(("CALL", "draw_square", [5]), instructions)

    def test_function_call_in_expression(self):
        program = Program([
            VariableDeclaration(
                "res",
                BinaryExpression(
                    FunctionCall("get_val", [Number(2)]),
                    "PLUS",
                    Number(3)
                )
            )
        ])
        instructions = self.ir_gen.generate(program)

        # Call in expression should be ("CALL", temp, "get_val", [2])
        call_inst = [inst for inst in instructions if inst[0] == "CALL"]
        self.assertEqual(len(call_inst), 1)
        self.assertEqual(len(call_inst[0]), 4)
        self.assertEqual(call_inst[0][2], "get_val")
        self.assertEqual(call_inst[0][3], [2])

    # F. Invalid and unsupported AST nodes
    def test_invalid_program_node(self):
        with self.assertRaisesRegex(ValueError, "Program node"):
            self.ir_gen.generate("not a program")

    def test_unsupported_ast_command(self):
        class DummyCommand(ASTNode):
            pass

        with self.assertRaisesRegex(ValueError, "Unsupported AST command: DummyCommand"):
            self.ir_gen.generate(Program([DummyCommand()]))

    def test_unsupported_ast_expression(self):
        class DummyExpr(ASTNode):
            pass

        with self.assertRaisesRegex(ValueError, "Unsupported AST expression: DummyExpr"):
            self.ir_gen.generate(Program([Move(DummyExpr())]))

    def test_unsupported_binary_operator(self):
        program = Program([
            VariableDeclaration("x", BinaryExpression(Number(1), "EXP", Number(2)))
        ])
        with self.assertRaisesRegex(ValueError, "Unsupported binary operator: EXP"):
            self.ir_gen.generate(program)

    def test_unsupported_unary_operator(self):
        program = Program([
            VariableDeclaration("x", UnaryExpression("TILDE", Number(1)))
        ])
        with self.assertRaisesRegex(ValueError, "Unsupported unary operator: TILDE"):
            self.ir_gen.generate(program)


if __name__ == "__main__":
    unittest.main()
