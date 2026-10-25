from compiler.ast import (
    Program, Move, Turn, Repeat, Back, Speed, PenUp, PenDown,
    Position, Number, String, Boolean, Variable, ObstacleAhead,
    UnaryExpression, BinaryExpression, VariableDeclaration,
    Assignment, Print, If, While, FunctionDefinition, FunctionCall
)


class IRGenerator:

    def __init__(self):
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self, prefix="t"):
        name = f"{prefix}{self.temp_count}"
        self.temp_count += 1
        return name

    def new_label_id(self):
        self.label_count += 1
        return self.label_count

    def new_label(self, prefix="L"):
        return f"{prefix}_{self.new_label_id()}"

    def generate(self, program):
        if not isinstance(program, Program):
            raise ValueError("IR generation requires a Program node")

        self.temp_count = 0
        self.label_count = 0
        instructions = []

        self.generate_commands(
            program.commands,
            instructions
        )

        return instructions

    def generate_commands(self, commands, instructions):
        for command in commands:
            if isinstance(command, Move):
                steps = self.generate_expression(command.steps, instructions)
                instructions.append(("MOVE", steps))

            elif isinstance(command, Back):
                steps = self.generate_expression(command.steps, instructions)
                instructions.append(("BACK", steps))

            elif isinstance(command, Turn):
                instructions.append(("TURN", command.direction))

            elif isinstance(command, Speed):
                value = self.generate_expression(command.value, instructions)
                instructions.append(("SPEED", value))

            elif isinstance(command, PenUp):
                instructions.append(("PEN_UP", None))

            elif isinstance(command, PenDown):
                instructions.append(("PEN_DOWN", None))

            elif isinstance(command, Position):
                instructions.append(("POSITION", None))

            elif isinstance(command, VariableDeclaration):
                value = self.generate_expression(command.value, instructions)
                instructions.append(("DECLARE", command.name, value))

            elif isinstance(command, Assignment):
                value = self.generate_expression(command.value, instructions)
                instructions.append(("ASSIGN", command.name, value))

            elif isinstance(command, Print):
                value = self.generate_expression(command.value, instructions)
                instructions.append(("PRINT", value))

            elif isinstance(command, If):
                cond = self.generate_expression(command.condition, instructions)
                if_id = self.new_label_id()
                if command.else_commands:
                    else_label = f"ELSE_{if_id}"
                    end_label = f"END_IF_{if_id}"
                    instructions.append(("JUMP_IF_FALSE", cond, else_label))
                    self.generate_commands(command.then_commands, instructions)
                    instructions.append(("JUMP", end_label))
                    instructions.append(("LABEL", else_label))
                    self.generate_commands(command.else_commands, instructions)
                    instructions.append(("LABEL", end_label))
                else:
                    end_label = f"END_IF_{if_id}"
                    instructions.append(("JUMP_IF_FALSE", cond, end_label))
                    self.generate_commands(command.then_commands, instructions)
                    instructions.append(("LABEL", end_label))

            elif isinstance(command, While):
                loop_id = self.new_label_id()
                start_label = f"WHILE_START_{loop_id}"
                end_label = f"WHILE_END_{loop_id}"
                instructions.append(("LABEL", start_label))
                cond = self.generate_expression(command.condition, instructions)
                instructions.append(("JUMP_IF_FALSE", cond, end_label))
                self.generate_commands(command.commands, instructions)
                instructions.append(("JUMP", start_label))
                instructions.append(("LABEL", end_label))

            elif isinstance(command, Repeat):
                count = self.generate_expression(command.count, instructions)
                counter = self.new_temp("_iter_")
                instructions.append(("DECLARE", counter, 0))
                rep_id = self.new_label_id()
                start_label = f"REPEAT_START_{rep_id}"
                end_label = f"REPEAT_END_{rep_id}"
                instructions.append(("LABEL", start_label))
                cond = self.new_temp("t")
                instructions.append(("LT", cond, counter, count))
                instructions.append(("JUMP_IF_FALSE", cond, end_label))
                self.generate_commands(command.commands, instructions)
                instructions.append(("ADD", counter, counter, 1))
                instructions.append(("JUMP", start_label))
                instructions.append(("LABEL", end_label))

            elif isinstance(command, FunctionDefinition):
                func_label = f"FUNC_{command.name}"
                end_label = f"END_FUNC_{command.name}"
                instructions.append(("LABEL", func_label))
                instructions.append(("FUNC_DEF", command.name, list(command.parameters)))
                self.generate_commands(command.commands, instructions)
                instructions.append(("RETURN", None))
                instructions.append(("LABEL", end_label))

            elif isinstance(command, FunctionCall):
                args = [
                    self.generate_expression(arg, instructions)
                    for arg in command.arguments
                ]
                instructions.append(("CALL", command.name, args))

            else:
                raise ValueError(
                    f"Unsupported AST command: {type(command).__name__}"
                )

    def generate_expression(self, expression, instructions):
        if expression is None:
            return None

        if isinstance(expression, (int, float)) and not isinstance(expression, bool):
            return expression

        if isinstance(expression, bool):
            return expression

        if isinstance(expression, Number):
            return expression.value

        if isinstance(expression, String):
            return repr(expression.value)

        if isinstance(expression, Boolean):
            return expression.value

        if isinstance(expression, Variable):
            return expression.name

        if isinstance(expression, ObstacleAhead):
            temp = self.new_temp()
            instructions.append(("OBSTACLE_AHEAD", temp))
            return temp

        if isinstance(expression, UnaryExpression):
            operand = self.generate_expression(expression.operand, instructions)
            temp = self.new_temp()

            if expression.operator == "NOT":
                instructions.append(("NOT", temp, operand))
            elif expression.operator in ("MINUS", "-"):
                instructions.append(("NEG", temp, operand))
            elif expression.operator in ("PLUS", "+"):
                instructions.append(("POS", temp, operand))
            else:
                raise ValueError(
                    f"Unsupported unary operator: {expression.operator}"
                )

            return temp

        if isinstance(expression, BinaryExpression):
            left = self.generate_expression(expression.left, instructions)
            right = self.generate_expression(expression.right, instructions)
            temp = self.new_temp()

            op_map = {
                "PLUS": "ADD",
                "MINUS": "SUB",
                "MULTIPLY": "MUL",
                "DIVIDE": "DIV",
                "+": "ADD",
                "-": "SUB",
                "*": "MUL",
                "/": "DIV",
                "EQ": "EQ",
                "==": "EQ",
                "NE": "NE",
                "!=": "NE",
                "LT": "LT",
                "<": "LT",
                "LE": "LE",
                "<=": "LE",
                "GT": "GT",
                ">": "GT",
                "GE": "GE",
                ">=": "GE",
                "AND": "AND",
                "OR": "OR",
            }

            if expression.operator not in op_map:
                raise ValueError(
                    f"Unsupported binary operator: {expression.operator}"
                )

            opcode = op_map[expression.operator]
            instructions.append((opcode, temp, left, right))
            return temp

        if isinstance(expression, FunctionCall):
            args = [
                self.generate_expression(arg, instructions)
                for arg in expression.arguments
            ]
            temp = self.new_temp()
            instructions.append(("CALL", temp, expression.name, args))
            return temp

        raise ValueError(
            f"Unsupported AST expression: {type(expression).__name__}"
        )