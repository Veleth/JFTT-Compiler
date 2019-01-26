from sly import Lexer

class CompilerLexer(Lexer):
    tokens = { ADD, SUB, MUL, DIV, MOD,
    ASSIGN, NE, GE, LE, GT, LT, EQ,
    DOWNTO, TO, FROM,
    ENDWHILE, ENDDO, ENDFOR, ENDIF, WHILE, DO, FOR, IF, END, IN, DECLARE,
    THEN, ELSE, READ, WRITE,
    LEFT, RIGHT, COL, SEM, ASSIGN, NUM, PID }
    
    ignore = ' \t\r'
    ignore_comment = r'\[[^\]]*\]'
    ignore_newline = r'\n'

    ADD = r'\+'
    SUB = r'-'
    MUL = r'\*'
    DIV = r'/'
    MOD = r'%'
    
    ASSIGN = r':='
    NE = r'!='
    GE = r'>='
    LE = r'<='
    GT = r'>'
    LT = r'<'
    EQ = r'='

    DOWNTO = r'DOWNTO'
    TO = r'TO'
    FROM = r'FROM'

    ENDWHILE = r'ENDWHILE'
    ENDDO = r'ENDDO'
    ENDFOR = r'ENDFOR'
    ENDIF = r'ENDIF'
    WHILE = r'WHILE'
    DO = r'DO'
    FOR = r'FOR'
    IF = r'IF'
    END = r'END'
    IN = r'IN'
    DECLARE = r'DECLARE'

    THEN = r'THEN'
    ELSE = r'ELSE'

    READ = r'READ'
    WRITE = r'WRITE'

    LEFT = r'\('
    RIGHT = r'\)'
    COL = r':'
    SEM = r';'

    NUM = r'[0-9]+'
    PID = r'[_a-z]+'

    def ignore_comment(self, t):
        return

    def ignore_newline(self, t):
        self.lineno += 1

    def error(self, t):
        print("Syntax error in line ",self.lineno, ". Unknown token: ",t.value)
        self.index += 1