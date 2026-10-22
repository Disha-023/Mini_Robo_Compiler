
from compiler.lexer import Lexer

program = """START
// Testing RoboLang 2.0
LET steps = 5
LET robot_speed = 2

IF steps >= 3 {
    MOVE steps + 2
    PRINT "Robot moving"
}

FUNC draw_square(n) {
    REPEAT 4 {
        MOVE n
        TURN RIGHT
    }
}

PEN_DOWN
BACK 2
POSITION
STOP
"""

try:
    tokens = Lexer(program).tokenize()

    print("LEXICAL ANALYSIS SUCCESSFUL")
    print("-" * 65)

    for token in tokens:
        print(
            f"{token.token_type:<15} "
            f"{str(token.value):<20} "
            f"Line: {token.line:<3} "
            f"Column: {token.column}"
        )

except SyntaxError as error:
    print(error)
