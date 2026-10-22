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