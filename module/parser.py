from sly import Parser
from .lexer import CompilerLexer

class CompilerParser(Parser):
    tokens = CompilerLexer.tokens

    def __init__(self):
        self.vars = []

    @_('DECLARE declarations IN commands END')
    def program(self, p):
        return("PROGRAM", p.declarations, p.commands)

    @_('declarations PID SEM')
    def declarations(self, p):
        x = p.declarations
        if (x != None):
            self.vars.append(('int', p[1], p.lineno))
            return x
        else:
            return

    @_('declarations PID LEFT NUM COL NUM RIGHT SEM')
    def declarations(self, p):
        x = p.declarations
        if (x != None):
            self.vars.append(('tab', p[1], p[3], p[5], p.lineno))
            return x
        else:
            return 

    @_('')
    def declarations(self, p):
        return self.vars

    @_('commands command')
    def commands(self, p):
        x = p.commands
        x.append(p.command)
        return x

    @_('command')
    def commands(self, p):
        return [p.command]

    @_('id ASSIGN expr SEM')
    def command(self, p):
        return (p[1], p.id, p.expr, p.lineno)

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        return ("IF_E", p.condition, p.commands0, p.commands1, p.lineno)

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        return (p[0], p.condition, p.commands, p.lineno)

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        return (p[0], p.condition, p.commands, p.lineno)

    @_('DO commands WHILE condition ENDDO')
    def command(self, p):
        return (p[0], p.commands, p.condition, p.lineno)


    @_('FOR PID FROM value TO value DO commands ENDFOR',
    'FOR PID FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):
        #possibly take lines
        return (str(p[0]+"_"+p[4][0]), p[1], p.value0, p.value1, p.commands)

    @_('READ value SEM')
    def command(self, p):
        return (p[0], p.value, p.lineno)

    @_('WRITE value SEM')
    def command(self, p):
        return (p[0], p.value, p.lineno)

    @_('value')
    def expr(self, p):
        return p.value

    @_('value ADD value',
    'value SUB value',
    'value MUL value',
    'value DIV value',
    'value MOD value',)
    def expr(self, p):
        return (p[1], p.value0, p.value1, p.lineno)

    @_('value EQ value',
    'value NE value',
    'value GT value',
    'value LT value',
    'value GE value',
    'value LE value')
    def condition(self, p):
        return (p[1], p.value0, p.value1, p.lineno)

    @_('NUM')
    def value(self, p):
        #possibly decorate with info
        return ('NUM', p[0])
    
    @_('id')
    def value(self, p):
        #possibly decorate with info
        return p.id

    @_('PID')
    def id(self, p):
        #possibly decorate with info
        return ("int", p[0], p.lineno)

    @_('PID LEFT PID RIGHT')
    def id(self, p):
        return ('tab', p[0], ("int", p[2], p.lineno), p.lineno)


    @_('PID LEFT NUM RIGHT')
    def id(self, p):
        return ('tab', p[0], ("NUM", p[2]), p.lineno)