
class ASTNode:
    pass



class Program(ASTNode):
    def __init__(self, commands):
        self.commands = commands

    def __repr__(self):
        return f"Program({self.commands})"


class Move(ASTNode):
    def __init__(self, steps):
        self.steps = steps

    def __repr__(self):
        return f"Move({self.steps})"


class Turn(ASTNode):
    def __init__(self, direction):
        self.direction = direction

    def __repr__(self):
        return f"Turn({self.direction})"


class Repeat(ASTNode):
    def __init__(self, count, commands):
        self.count = count
        self.commands = commands

    def __repr__(self):
        return f"Repeat({self.count}, {self.commands})"



class Back(ASTNode):
    def __init__(self, steps):
        self.steps = steps


class Speed(ASTNode):
    def __init__(self, value):
        self.value = value


class PenUp(ASTNode):
    pass


class PenDown(ASTNode):
    pass


class Position(ASTNode):
    pass


# Expressions.
class Number(ASTNode):
    def __init__(self, value):
        self.value = value


class String(ASTNode):
    def __init__(self, value):
        self.value = value


class Boolean(ASTNode):
    def __init__(self, value):
        self.value = value


class Variable(ASTNode):
    def __init__(self, name):
        self.name = name


class ObstacleAhead(ASTNode):
    pass


class UnaryExpression(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand


class BinaryExpression(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


# Variables and output.
class VariableDeclaration(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Assignment(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Print(ASTNode):
    def __init__(self, value):
        self.value = value


# Conditional and loop statements.
class If(ASTNode):
    def __init__(self, condition, then_commands, else_commands=None):
        self.condition = condition
        self.then_commands = then_commands
        self.else_commands = else_commands or []


class While(ASTNode):
    def __init__(self, condition, commands):
        self.condition = condition
        self.commands = commands


# Functions.
class FunctionDefinition(ASTNode):
    def __init__(self, name, parameters, commands):
        self.name = name
        self.parameters = parameters
        self.commands = commands


class FunctionCall(ASTNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments
