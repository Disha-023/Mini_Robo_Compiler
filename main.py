from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.ir import IRGenerator
from compiler.codegen import CodeGenerator
from robot.executor import RobotExecutor
from robot.simulator import RobotSimulator


# ROBOLANG 2.0 - LEXER TEST MODE

TEST_NEW_LEXER = True


program = """
START

// Testing new RoboLang 2.0 features

LET steps = 5
LET speed_value = 2
LET result = (steps + 3) * 2 - 1 / 1

SPEED speed_value
PEN_DOWN

IF steps >= 3 AND NOT OBSTACLE_AHEAD {
    MOVE steps
} ELSE {
    BACK 2
}

WHILE steps < 10 OR steps == 5 {
    steps = steps + 1
}

FUNC draw_square(size) {
    REPEAT 4 {
        MOVE size
        TURN RIGHT
    }
}

draw_square(5)

IF steps != 0 AND steps <= 10 {
    TURN LEFT
}

PEN_UP
POSITION
PRINT "Robot finished"
PRINT result

STOP
"""



# TEST NEW LEXICAL ANALYSIS FEATURES


if TEST_NEW_LEXER:

    print("\n========== ROBOLANG 2.0 LEXICAL ANALYSIS ==========")

    lexer = Lexer(program)
    tokens = lexer.tokenize()

    for token in tokens:
        print(
            f"{token.token_type:<16} "
            f"{str(token.value):<20} "
            f"Line: {token.line:<3} "
            f"Column: {token.column}"
        )

    print("\nNEW FEATURES LEXER TEST COMPLETED!")

    # Stop here because the old parser does not
    # support the new RoboLang 2.0 syntax yet.
    raise SystemExit(0)



# PHASE 2: LEXER


lexer = Lexer(program)
tokens = lexer.tokenize()



# PHASE 3 + 4: PARSER + AST


parser = Parser(tokens)
ast = parser.parse()



# PHASE 5: SEMANTIC ANALYSIS


analyzer = SemanticAnalyzer()
analyzer.analyze(ast)



# PHASE 6: IR GENERATION


ir_generator = IRGenerator()
instructions = ir_generator.generate(ast)

print("\nIntermediate Representation:")

for instruction in instructions:
    print(instruction)


# PHASE 7: CODE GENERATION

code_generator = CodeGenerator()
generated_code = code_generator.generate(instructions)

print("\nGenerated Python Code:")

for line in generated_code:
    print(line)


# ROBOT EXECUTION

executor = RobotExecutor()

print("\nRobot Execution:")

executor.execute(instructions)

print("\nStarting Robot Simulator...")

simulator = RobotSimulator(instructions)

simulator.run()


# ROBOT EXECUTION (ORIGINAL SECOND RUN)

executor = RobotExecutor()

print("\nRobot Execution:")

executor.execute(instructions)



# 2D SIMULATOR (ORIGINAL SECOND RUN)

print("\nStarting Robot Simulator...")

simulator = RobotSimulator(instructions)

simulator.run()
