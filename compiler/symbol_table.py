class SymbolTable:
    VALID_TYPES = {"INT", "BOOL", "STRING", "FLOAT"}

    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def declare(self, name, symbol_type):
        if not isinstance(name, str) or not name:
            raise ValueError("Variable name must not be empty")

        if name in self.symbols:
            raise ValueError(
                f"Variable '{name}' is already declared "
                "in this scope"
            )

        if symbol_type not in self.VALID_TYPES:
            raise ValueError(
                f"Invalid type '{symbol_type}' "
                f"for variable '{name}'"
            )

        self.symbols[name] = symbol_type

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]

        if self.parent is not None:
            return self.parent.lookup(name)

        raise ValueError(
            f"Variable '{name}' is not declared"
        )

    def exists_in_current_scope(self, name):
        return name in self.symbols

    def exists(self, name):
        if name in self.symbols:
            return True

        if self.parent is not None:
            return self.parent.exists(name)

        return False

    def create_child_scope(self):
        return SymbolTable(parent=self)