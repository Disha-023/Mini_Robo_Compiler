from compiler.codegen import CodeGenerator
from robot.robot import Robot


SAFE_BUILTINS = {
    "print": print,
    "hasattr": hasattr,
    "bool": bool,
    "int": int,
    "float": float,
    "str": str,
    "range": range,
    "len": len,
    "None": None,
    "True": True,
    "False": False,
}


class RobotExecutor:
    """Executes RoboLang IR instructions or generated Python code against a Robot instance."""

    def __init__(self, robot=None):
        self.robot = robot if robot is not None else Robot()

    def execute(self, program):
        """Execute IR instructions or Python code strings against self.robot.

        Args:
            program: List of IR instruction tuples, list of Python code lines,
                     or a single Python code string.

        Returns:
            Robot: The executor's robot instance after execution.
        """
        if isinstance(program, list):
            if not program:
                source = ""
            elif all(isinstance(x, (tuple, list)) for x in program):
                generator = CodeGenerator()
                code_lines = generator.generate(program)
                source = "\n".join(code_lines)
            elif all(isinstance(x, str) for x in program):
                source = "\n".join(program)
            else:
                raise TypeError(
                    "Program list must contain all IR instructions (tuples/lists) "
                    "or all Python code strings."
                )
        elif isinstance(program, str):
            source = program
        else:
            raise TypeError(
                f"Expected IR instruction list or code string, got {type(program)}"
            )

        if source.strip():
            compiled = compile(source, "<robot_program>", "exec")
            scope = {
                "robot": self.robot,
                "__builtins__": SAFE_BUILTINS,
            }
            exec(compiled, scope)

        self.robot.show_status()
        return self.robot