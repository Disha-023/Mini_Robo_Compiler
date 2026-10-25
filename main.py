from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.ir import IRGenerator
from compiler.codegen import CodeGenerator
from robot.executor import RobotExecutor
from robot.simulator import RobotSimulator


# ROBOLANG 2.0 - LEXER TEST MODE

TEST_NEW_LEXER = False



program = """
START

// ROBOLANG 2.0 - COMPLETE LEXICAL ANALYSIS DEMO
// Testing all keywords, operators and punctuation

// Variable declarations and identifiers
LET steps = 5
LET speed_value = 1
LET total = 10
LET robot_counter2 = 3

// All arithmetic operators: + - * /
LET addition = 10 + 5
LET subtraction = 10 - 5
LET multiplication = 10 * 5
LET division = 10 / 2
LET combined = (10 + 5) * 2 - 8 / 4

// Assignment
steps = steps + 1

// Comparison operators: > < >= <= == !=
IF steps > 2 {
    PRINT "Greater than"
}

IF steps < 20 {
    PRINT "Less than"
}

IF steps >= 5 {
    PRINT "Greater or equal"
}

IF steps <= 10 {
    PRINT "Less or equal"
}

IF steps == 6 {
    PRINT "Equal"
}

IF steps != 0 {
    PRINT "Not equal"
}

// Logical operators and Boolean keywords
IF TRUE AND NOT FALSE {
    PRINT "AND and NOT working"
}

IF FALSE OR TRUE {
    PRINT "OR working"
}

// Robot commands
SPEED speed_value
PEN_DOWN
MOVE 5
BACK 2
TURN LEFT
TURN RIGHT
PEN_UP
POSITION

// Obstacle keyword and ELSE
IF OBSTACLE_AHEAD {
    BACK 1
} ELSE {
    MOVE 1
}

// WHILE loop
WHILE steps < 8 {
    steps = steps + 1
}

// REPEAT loop
REPEAT 4 {
    MOVE 2
    TURN RIGHT
}

// Function definition and function call
FUNC draw_rectangle(width, height) {
    MOVE width
    TURN RIGHT
    MOVE height
    TURN RIGHT
    MOVE width
    TURN RIGHT
    MOVE height
    TURN RIGHT
}

draw_rectangle(4, 2)

// String literals and escape sequences
PRINT "Robot finished"
PRINT "Hello\\nRobot"
PRINT "Column1\\tColumn2"
PRINT "Say \\"Hello\\""
PRINT "Path C:\\\\Robot"

// Lowercase and mixed-case keywords
move 1
Turn LEFT
pen_up

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

# 2D SIMULATOR

print("\nStarting Robot Simulator...")

simulator = RobotSimulator(executor.robot)

simulator.run()
