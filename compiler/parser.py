
from compiler.ast import (
    Program, Move, Turn, Repeat,
    Back, Speed, PenUp, PenDown, Position,
    Number, String, Boolean, Variable, ObstacleAhead,
    UnaryExpression, BinaryExpression,
    VariableDeclaration, Assignment, Print,
    If, While, FunctionDefinition, FunctionCall
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def peek_token(self, offset=1):
        index = self.position + offset
        if index < len(self.tokens):
            return self.tokens[index]
        return None

    def advance(self):
        token = self.current_token()
        if token is not None:
            self.position += 1
        return token

    def expect(self, token_type):
        token = self.current_token()

        if token is None:
            raise SyntaxError(
                f"Expected {token_type}, but reached end of program"
            )

        if token.token_type != token_type:
            raise SyntaxError(
                f"Expected {token_type}, but found {token.token_type} "
                f"at line {token.line}, column {token.column}"
            )

        self.advance()
        return token

    def parse(self):
        self.expect("START")
        commands = self.parse_commands()
        self.expect("STOP")

        if self.current_token() is not None:
            token = self.current_token()
            raise SyntaxError(
                f"Unexpected token {token.token_type} "
                f"at line {token.line}, column {token.column}"
            )

        return Program(commands)

    def parse_commands(self):
        commands = []

        while self.current_token() is not None:
            token_type = self.current_token().token_type

            if token_type in ("STOP", "RIGHT_BRACE"):
                break

            commands.append(self.parse_command())

        return commands

    def parse_block(self):
        self.expect("LEFT_BRACE")
        commands = self.parse_commands()
        self.expect("RIGHT_BRACE")
        return commands

    def parse_command(self):
        token = self.current_token()

        if token is None:
            raise SyntaxError("Expected a command, reached end of program")

        kind = token.token_type

        if kind == "MOVE":
            return self.parse_move()

        if kind == "BACK":
            self.advance()
            return Back(self.expression_value(self.parse_expression()))

        if kind == "TURN":
            return self.parse_turn()

        if kind == "REPEAT":
            return self.parse_repeat()

        if kind == "SPEED":
            self.advance()
            return Speed(self.expression_value(self.parse_expression()))

        if kind == "PEN_UP":
            self.advance()
            return PenUp()

        if kind == "PEN_DOWN":
            self.advance()
            return PenDown()

        if kind == "POSITION":
            self.advance()
            return Position()

        if kind == "LET":
            return self.parse_variable_declaration()

        if kind == "IDENTIFIER":
            next_token = self.peek_token()

            if next_token is not None and next_token.token_type == "ASSIGN":
                return self.parse_assignment()

            if next_token is not None and next_token.token_type == "LEFT_PAREN":
                call = self.parse_function_call()
                return call

        if kind == "IF":
            return self.parse_if()

        if kind == "WHILE":
            return self.parse_while()

        if kind == "PRINT":
            return self.parse_print()

        if kind == "FUNC":
            return self.parse_function_definition()

        raise SyntaxError(
            f"Unexpected token {token.token_type} "
            f"at line {token.line}, column {token.column}"
        )

    def expression_value(self, expression):
        # Keep numeric literal values compatible with the original
        # Move, Repeat and simple-command implementations.
        if isinstance(expression, Number):
            return expression.value
        return expression

    def parse_move(self):
        self.expect("MOVE")
        expression = self.parse_expression()
        return Move(self.expression_value(expression))

    def parse_turn(self):
        self.expect("TURN")
        token = self.current_token()

        if token is not None and token.token_type in ("LEFT", "RIGHT"):
            self.advance()
            return Turn(token.token_type)

        raise SyntaxError("Expected LEFT or RIGHT after TURN")

    def parse_repeat(self):
        self.expect("REPEAT")
        expression = self.parse_expression()
        count = self.expression_value(expression)
        commands = self.parse_block()
        return Repeat(count, commands)

    def parse_variable_declaration(self):
        self.expect("LET")
        name = self.expect("IDENTIFIER").value
        self.expect("ASSIGN")
        value = self.parse_expression()
        return VariableDeclaration(name, value)

    def parse_assignment(self):
        name = self.expect("IDENTIFIER").value
        self.expect("ASSIGN")
        value = self.parse_expression()
        return Assignment(name, value)

    def parse_print(self):
        self.expect("PRINT")
        return Print(self.parse_expression())

    def parse_if(self):
        self.expect("IF")
        condition = self.parse_expression()
        then_commands = self.parse_block()
        else_commands = []

        if (
            self.current_token() is not None
            and self.current_token().token_type == "ELSE"
        ):
            self.advance()
            else_commands = self.parse_block()

        return If(condition, then_commands, else_commands)

    def parse_while(self):
        self.expect("WHILE")
        condition = self.parse_expression()
        commands = self.parse_block()
        return While(condition, commands)

    def parse_function_definition(self):
        self.expect("FUNC")
        name = self.expect("IDENTIFIER").value
        self.expect("LEFT_PAREN")
        parameters = []

        if (
            self.current_token() is not None
            and self.current_token().token_type != "RIGHT_PAREN"
        ):
            parameters.append(self.expect("IDENTIFIER").value)

            while (
                self.current_token() is not None
                and self.current_token().token_type == "COMMA"
            ):
                self.advance()
                parameters.append(self.expect("IDENTIFIER").value)

        self.expect("RIGHT_PAREN")
        commands = self.parse_block()
        return FunctionDefinition(name, parameters, commands)

    def parse_function_call(self):
        name = self.expect("IDENTIFIER").value
        self.expect("LEFT_PAREN")
        arguments = []

        if (
            self.current_token() is not None
            and self.current_token().token_type != "RIGHT_PAREN"
        ):
            arguments.append(self.parse_expression())

            while (
                self.current_token() is not None
                and self.current_token().token_type == "COMMA"
            ):
                self.advance()
                arguments.append(self.parse_expression())

        self.expect("RIGHT_PAREN")
        return FunctionCall(name, arguments)

    # Expression precedence, from lowest to highest:
    # OR, AND, NOT, comparisons, +/-, */, unary +/- and primary values.

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        expression = self.parse_and()

        while (
            self.current_token() is not None
            and self.current_token().token_type == "OR"
        ):
            operator = self.advance().token_type
            right = self.parse_and()
            expression = BinaryExpression(expression, operator, right)

        return expression

    def parse_and(self):
        expression = self.parse_not()

        while (
            self.current_token() is not None
            and self.current_token().token_type == "AND"
        ):
            operator = self.advance().token_type
            right = self.parse_not()
            expression = BinaryExpression(expression, operator, right)

        return expression

    def parse_not(self):
        if (
            self.current_token() is not None
            and self.current_token().token_type == "NOT"
        ):
            self.advance()
            return UnaryExpression("NOT", self.parse_not())

        return self.parse_comparison()

    def parse_comparison(self):
        expression = self.parse_additive()
        comparison_ops = {"EQ", "NE", "GT", "LT", "GE", "LE"}

        while (
            self.current_token() is not None
            and self.current_token().token_type in comparison_ops
        ):
            operator = self.advance().token_type
            right = self.parse_additive()
            expression = BinaryExpression(expression, operator, right)

        return expression

    def parse_additive(self):
        expression = self.parse_term()

        while (
            self.current_token() is not None
            and self.current_token().token_type in ("PLUS", "MINUS")
        ):
            operator = self.advance().token_type
            right = self.parse_term()
            expression = BinaryExpression(expression, operator, right)

        return expression

    def parse_term(self):
        expression = self.parse_unary()

        while (
            self.current_token() is not None
            and self.current_token().token_type in ("MULTIPLY", "DIVIDE")
        ):
            operator = self.advance().token_type
            right = self.parse_unary()
            expression = BinaryExpression(expression, operator, right)

        return expression

    def parse_unary(self):
        if (
            self.current_token() is not None
            and self.current_token().token_type in ("PLUS", "MINUS")
        ):
            operator = self.advance().token_type
            return UnaryExpression(operator, self.parse_unary())

        return self.parse_primary()

    def parse_primary(self):
        token = self.current_token()

        if token is None:
            raise SyntaxError("Expected an expression, reached end of program")

        if token.token_type == "NUMBER":
            self.advance()
            return Number(token.value)

        if token.token_type == "STRING":
            self.advance()
            return String(token.value)

        if token.token_type == "TRUE":
            self.advance()
            return Boolean(True)

        if token.token_type == "FALSE":
            self.advance()
            return Boolean(False)

        if token.token_type == "OBSTACLE_AHEAD":
            self.advance()
            return ObstacleAhead()

        if token.token_type == "IDENTIFIER":
            next_token = self.peek_token()

            if next_token is not None and next_token.token_type == "LEFT_PAREN":
                return self.parse_function_call()

            self.advance()
            return Variable(token.value)

        if token.token_type == "LEFT_PAREN":
            self.advance()
            expression = self.parse_expression()
            self.expect("RIGHT_PAREN")
            return expression

        raise SyntaxError(
            f"Expected an expression, found {token.token_type} "
            f"at line {token.line}, column {token.column}"
        )
