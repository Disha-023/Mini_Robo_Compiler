
from compiler.symbol_table import SymbolTable
from compiler.ast import (
    Program, Move, Turn, Repeat, Back, Speed, PenUp, PenDown,
    Position, Number, String, Boolean, Variable, ObstacleAhead,
    UnaryExpression, BinaryExpression, VariableDeclaration,
    Assignment, Print, If, While, FunctionDefinition, FunctionCall
)


class TypeChecker:
    NUMERIC_TYPES = {"INT", "FLOAT"}
    ARITHMETIC_OPERATORS = {"+", "-", "*", "/"}
    COMPARISON_OPERATORS = {"<", "<=", ">", ">=", "==", "!="}

    @staticmethod
    def check_numeric(type_name, operation):
        if type_name not in TypeChecker.NUMERIC_TYPES:
            raise ValueError(
                f"{operation} requires a numeric type, "
                f"but received {type_name}"
            )

    @staticmethod
    def arithmetic_result(left_type, operator, right_type):
        if operator not in TypeChecker.ARITHMETIC_OPERATORS:
            raise ValueError(
                f"Unsupported arithmetic operator '{operator}'"
            )

        if (
            left_type not in TypeChecker.NUMERIC_TYPES
            or right_type not in TypeChecker.NUMERIC_TYPES
        ):
            raise ValueError(
                f"Operator '{operator}' requires numeric operands"
            )

        if operator == "/" or (
            left_type == "FLOAT" or right_type == "FLOAT"
        ):
            return "FLOAT"

        return "INT"

    @staticmethod
    def comparison_result(left_type, operator, right_type):
        if operator not in TypeChecker.COMPARISON_OPERATORS:
            raise ValueError(
                f"Unsupported comparison operator '{operator}'"
            )

        if operator in {"<", "<=", ">", ">="}:
            if (
                left_type not in TypeChecker.NUMERIC_TYPES
                or right_type not in TypeChecker.NUMERIC_TYPES
            ):
                raise ValueError(
                    f"Operator '{operator}' requires numeric operands"
                )
        elif left_type != right_type:
            raise ValueError(
                f"Operator '{operator}' requires matching operand types"
            )

        return "BOOL"

    @staticmethod
    def check_boolean(type_name, operation):
        if type_name != "BOOL":
            raise ValueError(
                f"{operation} requires BOOL, but received {type_name}"
            )


class ExpressionTypeResolver:
    """Resolve variable types and infer expression result types."""

    def __init__(self, symbol_table=None):
        self.symbol_table = symbol_table or SymbolTable()

    def resolve_identifier(self, name):
        return self.symbol_table.lookup(name)

    def resolve_arithmetic(self, left_type, operator, right_type):
        return TypeChecker.arithmetic_result(
            left_type, operator, right_type
        )


class SemanticAnalyzer:
    ARITHMETIC_TOKENS = {
        "PLUS": "+",
        "MINUS": "-",
        "MULTIPLY": "*",
        "DIVIDE": "/",
    }

    COMPARISON_TOKENS = {
        "LT": "<",
        "LE": "<=",
        "GT": ">",
        "GE": ">=",
        "EQ": "==",
        "NE": "!=",
    }

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.functions = {}

    def analyze(self, program):
        if not isinstance(program, Program):
            raise ValueError(
                "Semantic analysis requires a Program node"
            )

        self.symbol_table = SymbolTable()
        self.functions = {}

        # Register function signatures first so calls can refer
        # to functions declared later in the program.
        for command in program.commands:
            if isinstance(command, FunctionDefinition):
                if command.name in self.functions:
                    raise ValueError(
                        f"Function '{command.name}' is already defined"
                    )

                if len(set(command.parameters)) != len(command.parameters):
                    raise ValueError(
                        f"Function '{command.name}' has duplicate parameters"
                    )

                self.functions[command.name] = command

        self.check_commands(program.commands)
        print("Semantic analysis successful!")

    def infer_expression(self, expression, scope, parameters=None):
        """Return INT, FLOAT, STRING, BOOL, or UNKNOWN."""

        parameters = parameters or set()

        if isinstance(expression, Number):
            if isinstance(expression.value, bool):
                raise ValueError("Boolean is not a numeric literal")
            if isinstance(expression.value, int):
                return "INT"
            if isinstance(expression.value, float):
                return "FLOAT"
            raise ValueError("Invalid numeric literal")

        if isinstance(expression, String):
            return "STRING"

        if isinstance(expression, Boolean):
            return "BOOL"

        if isinstance(expression, ObstacleAhead):
            return "BOOL"

        if isinstance(expression, Variable):
            if expression.name in parameters:
                return "UNKNOWN"
            return scope.lookup(expression.name)

        if isinstance(expression, FunctionCall):
            self.check_function_call(expression, scope, parameters)
            raise ValueError(
                f"Function '{expression.name}' has no defined return type"
            )

        if isinstance(expression, UnaryExpression):
            operand_type = self.infer_expression(
                expression.operand, scope, parameters
            )

            if expression.operator in ("PLUS", "MINUS"):
                if operand_type == "UNKNOWN":
                    return "UNKNOWN"
                TypeChecker.check_numeric(
                    operand_type, "Unary arithmetic"
                )
                return operand_type

            if expression.operator == "NOT":
                if operand_type != "UNKNOWN":
                    TypeChecker.check_boolean(operand_type, "NOT")
                return "BOOL"

            raise ValueError(
                f"Unsupported unary operator '{expression.operator}'"
            )

        if isinstance(expression, BinaryExpression):
            left_type = self.infer_expression(
                expression.left, scope, parameters
            )
            right_type = self.infer_expression(
                expression.right, scope, parameters
            )
            operator = expression.operator

            if operator in self.ARITHMETIC_TOKENS:
                symbol = self.ARITHMETIC_TOKENS[operator]

                if "UNKNOWN" in (left_type, right_type):
                    return "UNKNOWN"

                return TypeChecker.arithmetic_result(
                    left_type, symbol, right_type
                )

            if operator in self.COMPARISON_TOKENS:
                symbol = self.COMPARISON_TOKENS[operator]

                if "UNKNOWN" in (left_type, right_type):
                    return "BOOL"

                return TypeChecker.comparison_result(
                    left_type, symbol, right_type
                )

            if operator in ("AND", "OR"):
                for operand_type in (left_type, right_type):
                    if operand_type != "UNKNOWN":
                        TypeChecker.check_boolean(
                            operand_type, operator
                        )
                return "BOOL"

            raise ValueError(
                f"Unsupported binary operator '{operator}'"
            )

        raise ValueError(
            f"Unsupported expression: {type(expression).__name__}"
        )

    @staticmethod
    def is_positive_number(value):
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and value > 0
        )

    def check_numeric_command(self, value, operation, scope, parameters):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if value <= 0:
                raise ValueError(
                    f"{operation} value must be greater than 0"
                )
            return

        value_type = self.infer_expression(value, scope, parameters)

        if value_type not in ("INT", "FLOAT", "UNKNOWN"):
            raise ValueError(
                f"{operation} requires a numeric type, "
                f"but received {value_type}"
            )

    def check_function_call(self, command, scope, parameters=None):
        parameters = parameters or set()

        if command.name not in self.functions:
            raise ValueError(
                f"Function '{command.name}' is not defined"
            )

        definition = self.functions[command.name]

        if len(command.arguments) != len(definition.parameters):
            raise ValueError(
                f"Function '{command.name}' expects "
                f"{len(definition.parameters)} arguments, "
                f"but received {len(command.arguments)}"
            )

        for argument in command.arguments:
            self.infer_expression(argument, scope, parameters)

    def check_commands(self, commands, scope=None, parameters=None):
        scope = scope or self.symbol_table
        parameters = parameters or set()

        for command in commands:
            if isinstance(command, FunctionDefinition):
                if scope is not self.symbol_table:
                    raise ValueError(
                        "Nested function definitions are not supported"
                    )

                function_scope = scope.create_child_scope()
                self.check_commands(
                    command.commands,
                    function_scope,
                    set(command.parameters)
                )

            elif isinstance(command, Move):
                self.check_numeric_command(
                    command.steps, "MOVE", scope, parameters
                )

            elif isinstance(command, Back):
                self.check_numeric_command(
                    command.steps, "BACK", scope, parameters
                )

            elif isinstance(command, Speed):
                self.check_numeric_command(
                    command.value, "SPEED", scope, parameters
                )

            elif isinstance(command, Turn):
                self.check_turn(command)

            elif isinstance(command, Repeat):
                self.check_numeric_command(
                    command.count, "REPEAT", scope, parameters
                )

                if not command.commands:
                    raise ValueError(
                        "REPEAT must contain at least one command"
                    )

                self.check_commands(
                    command.commands,
                    scope.create_child_scope(),
                    parameters
                )

            elif isinstance(command, VariableDeclaration):
                value_type = self.infer_expression(
                    command.value, scope, parameters
                )

                if value_type == "UNKNOWN":
                    raise ValueError(
                        "Cannot infer variable type from an untyped value"
                    )

                scope.declare(command.name, value_type)

            elif isinstance(command, Assignment):
                target_type = (
                    "UNKNOWN"
                    if command.name in parameters
                    else scope.lookup(command.name)
                )

                value_type = self.infer_expression(
                    command.value, scope, parameters
                )

                if (
                    target_type != "UNKNOWN"
                    and value_type != "UNKNOWN"
                    and target_type != value_type
                    and not (
                        target_type == "FLOAT" and value_type == "INT"
                    )
                ):
                    raise ValueError(
                        f"Cannot assign {value_type} to "
                        f"{target_type} variable '{command.name}'"
                    )

            elif isinstance(command, Print):
                self.infer_expression(command.value, scope, parameters)

            elif isinstance(command, If):
                condition_type = self.infer_expression(
                    command.condition, scope, parameters
                )

                if condition_type != "UNKNOWN":
                    TypeChecker.check_boolean(
                        condition_type, "IF condition"
                    )

                self.check_commands(
                    command.then_commands,
                    scope.create_child_scope(),
                    parameters
                )

                if command.else_commands:
                    self.check_commands(
                        command.else_commands,
                        scope.create_child_scope(),
                        parameters
                    )

            elif isinstance(command, While):
                condition_type = self.infer_expression(
                    command.condition, scope, parameters
                )

                if condition_type != "UNKNOWN":
                    TypeChecker.check_boolean(
                        condition_type, "WHILE condition"
                    )

                self.check_commands(
                    command.commands,
                    scope.create_child_scope(),
                    parameters
                )

            elif isinstance(command, FunctionCall):
                self.check_function_call(command, scope, parameters)

            elif isinstance(command, (PenUp, PenDown, Position)):
                pass

            else:
                raise ValueError(
                    f"Unsupported command: {type(command).__name__}"
                )

    @staticmethod
    def check_turn(command):
        if command.direction not in ("LEFT", "RIGHT"):
            raise ValueError("TURN direction must be LEFT or RIGHT")
