from sly import Lexer, Parser
import sys
import time
from module.lexer import CompilerLexer
from module.parser import CompilerParser
from module.machine import Machine as m

def readParseData(lines, depth):
    depth += 1
    for i in lines:
        if type(i) == type([]) or type(i) == type(()):
            readParseData(i, depth)
        else:
            print(' '*depth, "|--", end = '')
            print("- ", i)
    print(" "*depth, "<-")
    depth -= 1

if __name__ == '__main__':
    lexer = CompilerLexer()
    parser = CompilerParser()
    if (len(sys.argv)==3):
        text = ""
        with open(sys.argv[1], "r") as file:
            text+=file.read()
        parsed = parser.parse(lexer.tokenize(text))
        machine = m(parsed)
        code = machine.out.asm
        with open(sys.argv[2], "w") as fout:
            for a in code:
                fout.write(a+"\n")
    else:
        print("Usage: ./compiler.py fileIn fileOut")