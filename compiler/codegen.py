class CodeGenerator:

    def __init__(self, indent_spaces=4):
        self.indent_spaces = indent_spaces

    def format_operand(self, val):
        if val is None:
            return "None"
        if isinstance(val, bool):
            return "True" if val else "False"
        if isinstance(val, (int, float)):
            return str(val)
        if isinstance(val, str):
            # Already quoted string literal or identifier / temporary name
            return val
        return str(val)

    def generate(self, instructions):
        code = []
        indent_level = 0
        block_stack = []

        def get_indent():
            return " " * (indent_level * self.indent_spaces)

        for instruction in instructions:
            if not isinstance(instruction, (tuple, list)) or len(instruction) == 0:
                raise ValueError(f"Invalid instruction format: {instruction}")

            command = instruction[0]

            # Check if this instruction closes or transitions an active block
            if command == "LABEL":
                label_name = instruction[1]

                # Check if this label matches the top block's else_label or end_label
                if block_stack and label_name == block_stack[-1].get("else_label"):
                    top = block_stack[-1]
                    if not top.get("has_body", False):
                        code.append(get_indent() + "pass")
                    indent_level -= 1
                    code.append(get_indent() + "else:")
                    indent_level += 1
                    top["else_label"] = None
                    top["has_body"] = False
                    continue

                if block_stack and label_name == block_stack[-1].get("end_label"):
                    top = block_stack[-1]
                    if not top.get("has_body", False):
                        code.append(get_indent() + "pass")
                    indent_level -= 1
                    block_stack.pop()
                    continue

                # Check if this label begins a while or repeat loop
                if label_name.startswith("WHILE_START"):
                    suffix = label_name[len("WHILE_START"):]
                    end_label = f"WHILE_END{suffix}"
                    code.append(get_indent() + "while True:")
                    indent_level += 1
                    block_stack.append({
                        "kind": "LOOP",
                        "start_label": label_name,
                        "end_label": end_label,
                        "has_body": False
                    })
                    continue

                if label_name.startswith("REPEAT_START"):
                    suffix = label_name[len("REPEAT_START"):]
                    end_label = f"REPEAT_END{suffix}"
                    code.append(get_indent() + "while True:")
                    indent_level += 1
                    block_stack.append({
                        "kind": "LOOP",
                        "start_label": label_name,
                        "end_label": end_label,
                        "has_body": False
                    })
                    continue

                if label_name.startswith("FUNC_"):
                    # Function marker label, followed by FUNC_DEF
                    continue

                # Fallback for unrecognized labels
                code.append(get_indent() + f"# label: {label_name}")
                continue

            elif command == "FUNC_DEF":
                name = instruction[1]
                params = instruction[2]
                code.append(get_indent() + f"def {name}({', '.join(params)}):")
                indent_level += 1
                block_stack.append({
                    "kind": "FUNC",
                    "end_label": f"END_FUNC_{name}",
                    "has_body": False
                })
                continue

            elif command == "JUMP_IF_FALSE":
                cond = instruction[1]
                target = instruction[2]

                # Check if jumping to current loop's end label (loop exit condition)
                is_loop_exit = (
                    block_stack and block_stack[-1].get("kind") == "LOOP" and
                    (target == block_stack[-1].get("end_label") or target.startswith("WHILE_END") or target.startswith("REPEAT_END"))
                )
                if is_loop_exit:
                    code.append(get_indent() + f"if not {self.format_operand(cond)}: break")
                    block_stack[-1]["has_body"] = True
                    continue

                # Otherwise, this starts an IF block
                code.append(get_indent() + f"if {self.format_operand(cond)}:")
                indent_level += 1

                if target.startswith("ELSE"):
                    suffix = target[len("ELSE"):]
                    end_label = f"END_IF{suffix}"
                    else_label = target
                else:
                    else_label = None
                    end_label = target

                block_stack.append({
                    "kind": "IF",
                    "else_label": else_label,
                    "end_label": end_label,
                    "has_body": False
                })
                continue

            elif command == "JUMP":
                target = instruction[1]

                # If jumping to loop start, while True handles it automatically
                if block_stack and target == block_stack[-1].get("start_label"):
                    continue

                # If jumping to end of if (skipping else), ignore
                if block_stack and target == block_stack[-1].get("end_label"):
                    continue

                code.append(get_indent() + f"# jump {target}")
                continue

            # Any standard command marks the current block as having statements
            if block_stack:
                block_stack[-1]["has_body"] = True

            value = instruction[1] if len(instruction) > 1 else None

            if command == "MOVE":
                code.append(get_indent() + f"robot.move({self.format_operand(value)})")

            elif command == "BACK":
                val = self.format_operand(value)
                code.append(
                    get_indent()
                    + f"robot.back({val}) if hasattr(robot, 'back') else robot.move(-({val}))"
                )

            elif command == "TURN":
                if value == "LEFT":
                    code.append(get_indent() + "robot.turn_left()")
                elif value == "RIGHT":
                    code.append(get_indent() + "robot.turn_right()")
                else:
                    code.append(get_indent() + f"robot.turn('{value}')")

            elif command == "SPEED":
                val = self.format_operand(value)
                code.append(
                    get_indent()
                    + f"robot.speed({val}) if hasattr(robot, 'speed') else None"
                )

            elif command == "PEN_UP":
                code.append(
                    get_indent()
                    + "robot.pen_up() if hasattr(robot, 'pen_up') else None"
                )

            elif command == "PEN_DOWN":
                code.append(
                    get_indent()
                    + "robot.pen_down() if hasattr(robot, 'pen_down') else None"
                )

            elif command == "POSITION":
                code.append(
                    get_indent()
                    + "robot.position() if hasattr(robot, 'position') else robot.show_status()"
                )

            elif command == "PRINT":
                code.append(get_indent() + f"print({self.format_operand(value)})")

            elif command == "DECLARE":
                target = instruction[1]
                val = instruction[2]
                if val is None:
                    code.append(get_indent() + f"{target} = None")
                else:
                    code.append(get_indent() + f"{target} = {self.format_operand(val)}")

            elif command == "ASSIGN":
                target = instruction[1]
                val = instruction[2]
                code.append(get_indent() + f"{target} = {self.format_operand(val)}")

            elif command in ("ADD", "SUB", "MUL", "DIV", "EQ", "NE", "LT", "LE", "GT", "GE", "AND", "OR"):
                target = instruction[1]
                left = self.format_operand(instruction[2])
                right = self.format_operand(instruction[3])

                op_symbols = {
                    "ADD": "+",
                    "SUB": "-",
                    "MUL": "*",
                    "DIV": "/",
                    "EQ": "==",
                    "NE": "!=",
                    "LT": "<",
                    "LE": "<=",
                    "GT": ">",
                    "GE": ">=",
                    "AND": "and",
                    "OR": "or",
                }
                op = op_symbols[command]
                code.append(get_indent() + f"{target} = {left} {op} {right}")

            elif command == "NOT":
                target = instruction[1]
                operand = self.format_operand(instruction[2])
                code.append(get_indent() + f"{target} = not {operand}")

            elif command == "NEG":
                target = instruction[1]
                operand = self.format_operand(instruction[2])
                code.append(get_indent() + f"{target} = -{operand}")

            elif command == "POS":
                target = instruction[1]
                operand = self.format_operand(instruction[2])
                code.append(get_indent() + f"{target} = +{operand}")

            elif command == "OBSTACLE_AHEAD":
                target = instruction[1]
                code.append(
                    get_indent()
                    + f"{target} = robot.obstacle_ahead() if hasattr(robot, 'obstacle_ahead') else False"
                )

            elif command == "CALL":
                if len(instruction) == 3:
                    # Statement function call: ("CALL", func_name, args)
                    name = instruction[1]
                    args = [self.format_operand(a) for a in instruction[2]]
                    code.append(get_indent() + f"{name}({', '.join(args)})")
                elif len(instruction) == 4:
                    # Expression function call: ("CALL", target, func_name, args)
                    target = instruction[1]
                    name = instruction[2]
                    args = [self.format_operand(a) for a in instruction[3]]
                    code.append(get_indent() + f"{target} = {name}({', '.join(args)})")
                else:
                    raise ValueError(f"Invalid CALL instruction: {instruction}")

            elif command == "RETURN":
                val = instruction[1] if len(instruction) > 1 else None
                if val is not None:
                    code.append(get_indent() + f"return {self.format_operand(val)}")
                else:
                    code.append(get_indent() + "return")

            else:
                raise ValueError(f"Unsupported IR instruction: {instruction}")

        # If any blocks remain unclosed, close them with pass if needed
        while block_stack:
            top = block_stack.pop()
            if not top.get("has_body", False):
                code.append(get_indent() + "pass")
            indent_level -= 1

        return code