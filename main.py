from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.ir import IRGenerator
from compiler.codegen import CodeGenerator
from robot.executor import RobotExecutor
from robot.simulator import RobotSimulator


program = """
START

MOVE 2
TURN LEFT   
MOVE 2

REPEAT 2{
TURN RIGHT
MOVE 2
}

TURN RIGHT
MOVE 2
TURN RIGHT

STOP
"""


# Phase 2: Lexer


lexer = Lexer(program)
tokens = lexer.tokenize()


# Phase 3 + 4: Parser + AST


parser = Parser(tokens)
ast = parser.parse()



# Phase 5: Semantic Analysis


analyzer = SemanticAnalyzer()
analyzer.analyze(ast)



# Phase 6: IR Generation


ir_generator = IRGenerator()
instructions = ir_generator.generate(ast)


print("\nIntermediate Representation:")

for instruction in instructions:
    print(instruction)



# Phase 7: Code Generation


code_generator = CodeGenerator()
generated_code = code_generator.generate(instructions)


print("\nGenerated Python Code:")

for line in generated_code:
    print(line)


# Robot Execution


executor = RobotExecutor()

print("\nRobot Execution:")

executor.execute(instructions)

print("\nStarting Robot Simulator...")

simulator = RobotSimulator(instructions)

simulator.run()

# Robot Execution
executor = RobotExecutor()

print("\nRobot Execution:")

executor.execute(instructions)


# 2D Simulator
print("\nStarting Robot Simulator...")

simulator = RobotSimulator(instructions)

simulator.run()