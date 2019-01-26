import sys
import math

class Machine(object):

    def __init__(self, parsed):
        self.dispatcher = {
            ':=':  self.assign, 
            'READ':  self.read,
            'WRITE':  self.write,
            'WHILE': self.loop_while,
            'DO': self.loop_do,
            'FOR_T': self.loop_forT,
            'FOR_D': self.loop_forD,
            'IF' : self.cond_if,
            'IF_E' : self.cond_ife
        }
        self.mem = 0
        self.counter = 0
        self.variables = {}
        self.registers = []
        self.code = []
        self.lines = 0
        self.out = Code()
        for l in "ABCDEFGH":
            self.registers.append(Register(l))
        self.compile(parsed)

    def compile(self, parsed):
        if (parsed == None): #parsing failed
            self.err("SYNTAX ERROR. PARSING UNSUCCESSFUL")
        parsed = parsed[1:] #Strip PROGRAM str
        #Declarations
        if not (parsed[0] == []):
            dec = parsed[0]
            self.declare(dec)
        parsed = parsed[1:]
        #Commands
        commands = parsed[0]
        self.perform(commands)
        a = self.out.asm
        a.append("HALT")
        self.removeLabels(a) #remove labels and link jumps
        # for x in a:
        #    print(x)

    def perform(self, commands):
        for c in commands:
            sym = c[0]
            #print(c)
            self.dispatcher[sym](c)

    def removeLabels(self, arr):
        labels = {}
        a = []
        i = 0
        while len(arr)>i: #map labels
            line = arr[i]
            if line[0:5] == 'LABEL':
                labels[line] = i
                arr.remove(line)
            else:
                i += 1
        i = 0
        for el in arr: #replace in jumps
            if 'LABEL' in el:
                label = el[el.index("LABEL"):]
                arr[i] = el.replace(label, str(labels[label])).strip() #strip removes accidental spaces
            i += 1
    
    def getLabel(self):
        self.counter += 1
        return ("LABEL"+str(self.counter))

    def checkDec(self, name, line): #check if variable is declared 
        if(name not in self.variables.keys()): 
            self.err(str("CRITICAL ERROR : UNDECLARED VARIABLE '"+str(name)+"' IN LINE "+str(line)))
        return

    def err(self, s, errno=1):
        print(s, file=sys.stderr)
        print("Compilation failed")
        exit(errno)

    def checkLeft(self, var, line): #check if the left argument of := is correct 
        name = var[1]
        v = self.getVar(name)
        if(v == None):
            self.err(str("CRITICAL ERROR: UNDECLARED OR INVALID VARIABLE '"+str(name)+"' IN LINE "+str(line)))
        #v is a var
        if(isinstance(v, Tab)):
            if len(var)<=3:
                self.err(str("CRITICAL ERROR: '"+str(name)+"' IS A TABLE; CHECK LINE "+str(line)))
            if(var[0] == "NUM"):
                if(int(var[1])>v.max or int(var[1])<v.min):
                    self.err(str("CRITICAL ERROR: INVALID TABLE INDEX '"+str(var[1])+"' IN LINE "+str(var[3])))
            # self.checkTab(v, None if len(var)==2 else var[2][1], line)
        elif len(var)>3:
            self.err(str("CRITICAL ERROR: '"+str(name)+"' IS NOT A TABLE; CHECK LINE "+str(line)))
    
    def getVar(self, name): 
        if name in self.variables.keys():
            return self.variables[name]
        else:
            return None

    #(':=', ('int', 'c', 4), ('NUM', '2'), 4)
    #(':=', ('tab', 'a', ('int', 'b', 5), 5), ('tab', 'a', ('int', 'c', 5), 5), 5)
    def storeVarIn(self, tok, register = "B"):
        buffer = "E"
        buffer2 = "F"
        if ((tok[0] == "tab" and isinstance(self.getVar(tok[1]), Int)) or (tok[0] == "int" and isinstance(self.getVar(tok[1]), Tab))):
            self.err(str("CRITICAL ERROR: TYPE MISMATCH, VARIABLE '"+str(tok[1])+"' IN LINE "+str(tok[len(tok)-1])))
        if (tok[0] == 'tab'):
            tab = self.getVar(tok[1])
            t = tab.address
            if (tok[2][0] == 'int'): #tab(var)
                var = self.getVar(tok[2][1])
                if (var == None):
                    self.err(str("CRITICAL ERROR: UNDECLARED VARIABLE "+str(tok[2][1])+" IN LINE "+str(tok[3])))
                if (var.ini == False):
                    self.err(str("CRITICAL ERROR: UNINITIALIZED VARIABLE "+str(tok[2][1])+" IN LINE "+str(tok[3])))#TODO: If something fails, remove this if
                ind = var.address
                self.out.loadTabVar(t, ind, register, buffer, buffer2)
            else: #tab(num)
                if (int(tok[2][1])<tab.min or int(tok[2][1])>tab.max):
                    self.err(str("CRITICAL ERROR: INVALID TABLE INDEX '"+str(tok[2][1])+"' IN LINE "+str(tok[3])))
                self.out.loadTabNum(t, int(tok[2][1]), register, buffer, buffer2)
        elif (tok[0] == 'int'): #int
            var = self.getVar(tok[1])
            if (var == None):
                self.err(str("CRITICAL ERROR: UNDECLARED VARIABLE "+str(tok[1])+" IN LINE "+str(tok[2])))
            if (var.ini == False):
                self.err(str("CRITICAL ERROR: UNINITIALIZED VARIABLE "+str(tok[1])+" IN LINE "+str(tok[2])))
            self.out.loadInt(var.address, register)
        elif (tok[0] == 'NUM'): #numeric 
            self.out.setValue(register, int(tok[1]))
        else: #expression
            op = tok[0]
            if (op == "+"):
                self.add(tok, register, "C")
            elif (op == "-"):
                self.sub(tok, register, "C")
            elif (op == "*"):
                self.mul(tok, register, "C", "D")
            elif (op == "/"): #A/B, module, buffer
                self.div(tok, register, "C", "D", "E", "F")
            elif (op == "%"):
                self.mod(tok, "C", register, "D", "E", "F")
            else:
                print("CRITICAL ERROR: UNKNOWN OPERATOR "+op)
                exit()

    def add(self, args, reg, r2):
        self.storeVarIn(args[1], reg)
        self.storeVarIn(args[2], r2)
        self.out.c_add(reg, r2)

    def sub(self, args, reg, r2):
        self.storeVarIn(args[1], reg)
        self.storeVarIn(args[2], r2)
        self.out.c_sub(reg, r2)

    def mul(self, args, result, r1, r2): #r1 * r2, outcome stored in reg
        label = self.getLabel()
        label2 = self.getLabel()
        label3 = self.getLabel()
        label4 = self.getLabel()
        self.storeVarIn(args[1], r1)
        self.storeVarIn(args[2], r2)
        self.out.c_sub(result, result)
        self.out.addLabel(label)
        self.out.c_jzero(r2, label4)
        self.out.c_jodd(r2, label3)
        self.out.addLabel(label2)
        self.out.c_half(r2)
        self.out.c_add(r1, r1)
        self.out.c_jump(label)
        self.out.addLabel(label3)
        self.out.c_add(result, r1)
        self.out.c_jump(label2)
        self.out.addLabel(label4) 

                        #      B       C      k
    def div(self, args, res, module, divisor, counter, temp):
        label = self.getLabel()
        label2 = self.getLabel()
        label3 = self.getLabel()
        label4 = self.getLabel()
        label5 = self.getLabel()
        self.storeVarIn(args[1], module)
        self.storeVarIn(args[2], divisor)
        self.out.c_sub(res, res)
        self.out.c_jzero(divisor, label5)
        self.out.c_sub(counter, counter)
        self.out.c_inc(counter)
        self.out.addLabel(label)
        self.out.c_copy(temp, module)
        self.out.c_inc(temp)
        self.out.c_sub(temp, divisor)
        self.out.c_jzero(temp, label2)
        self.out.c_add(divisor, divisor)
        self.out.c_add(counter, counter)
        self.out.c_jump(label)
        self.out.addLabel(label2)
        self.out.c_jzero(counter, label4)
        self.out.c_copy(temp, module)
        self.out.c_inc(temp)
        self.out.c_sub(temp, divisor)
        self.out.c_jzero(temp, label3)
        self.out.c_add(res, counter)
        self.out.c_sub(module, divisor)
        self.out.addLabel(label3)
        self.out.c_half(counter)
        self.out.c_half(divisor)
        self.out.c_jump(label2)
        self.out.addLabel(label5)
        self.out.c_sub(module,module)
        self.out.addLabel(label4)
        
    def mod(self, args, res, module, divisor, counter, temp):
        label = self.getLabel()
        label2 = self.getLabel()
        label3 = self.getLabel()
        label4 = self.getLabel()
        label5 = self.getLabel()
        self.storeVarIn(args[1], module)
        self.storeVarIn(args[2], divisor)
        self.out.c_sub(res, res)
        self.out.c_jzero(divisor, label5)
        self.out.c_sub(counter, counter)
        self.out.c_inc(counter)
        self.out.addLabel(label)
        self.out.c_copy(temp, module)
        self.out.c_inc(temp)
        self.out.c_sub(temp, divisor)
        self.out.c_jzero(temp, label2)
        self.out.c_add(divisor, divisor)
        self.out.c_add(counter, counter)
        self.out.c_jump(label)
        self.out.addLabel(label2)
        self.out.c_jzero(counter, label4)
        self.out.c_copy(temp, module)
        self.out.c_inc(temp)
        self.out.c_sub(temp, divisor)
        self.out.c_jzero(temp, label3)
        self.out.c_add(res, counter)
        self.out.c_sub(module, divisor)
        self.out.addLabel(label3)
        self.out.c_half(counter)
        self.out.c_half(divisor)
        self.out.c_jump(label2)
        self.out.addLabel(label5)
        self.out.c_sub(module,module)
        self.out.addLabel(label4)

    def ge(self, r1, r2):
        self.out.c_inc(r1)
        self.out.c_sub(r1, r2) #r1 != 0 means true

    def le(self, r1, r2):
        self.out.c_inc(r2)
        self.out.c_sub(r2, r1)
        self.out.c_copy(r1, r2) #r1 != 0 means true
            
    def gt(self, r1, r2): 
        self.out.c_sub(r1, r2) #r1 != 0 means true

    def lt(self, r1, r2):
        self.out.c_sub(r2, r1)
        self.out.c_copy(r1, r2) #r1 != 0 means true

    def eq(self, r1, r2, buffer):
        label = self.getLabel()
        label2 = self.getLabel()
        self.out.c_copy(buffer, r2)
        self.out.c_sub(buffer, r1)
        self.out.c_sub(r1, r2)
        self.out.c_add(r1, buffer)
        self.out.c_jzero(r1, label)
        self.out.c_sub(r1, r1)
        self.out.c_jump(label2)
        self.out.addLabel(label)
        self.out.c_inc(r1)
        self.out.addLabel(label2)   #r1 != 0 means true

    def ne(self, r1, r2, buffer):
        self.out.c_copy(buffer, r2)
        self.out.c_sub(buffer, r1)
        self.out.c_sub(r1, r2)
        self.out.c_add(r1, buffer) #r1 != 0 means true

    def declareIt(self, name, it = True):
        if (name in self.variables.keys()):
            self.err(str("CRITICAL ERROR: ITERATOR "+str(name)+" ALREADY IN USE"))
        self.variables[name] = Int(self.mem, iterator=it)
        self.variables[name].ini = True
        self.mem += 1

    def undeclareIt(self, name):
        self.variables.__delitem__(name)

    def findFreeMemCell(self):
        print("#TODO")

    def declare(self, dec):
        while(dec):
            d = dec[0]
            if (d[0] == "tab" and (int(d[2])<0 or int(d[2])>int(d[3]))):
                print(str("CRITICAL ERROR: MISTAKE IN DECLARATION OF TABLE "+d[1]), file=sys.stderr)
                print("Compilation failed")
                exit(1)
            if (d[1] in self.variables.keys()):
                print(str("CRITICAL ERROR: MULTIPLE DECLARATIONS OF VARIABLE '"+str(d[1])+"' IN LINE "+str(d[2])), file=sys.stderr)
                print("Compilation failed")
                exit(2)
            else:
                if d[0] == "tab":
                    self.variables[d[1]] = Tab(min=int(d[2]),max=int(d[3]),address=self.mem)
                    size = 2+int(d[3])-int(d[2])
                    self.out.setOffset(self.mem, int(d[2]))
                else: 
                    size = 1
                    self.variables[d[1]] = Int(self.mem)
                self.mem += size
            dec = dec[1:]

    def assign(self, com): # x := y
        #print(com)
        x = com[1]
        self.checkLeft(x, com[3])
        xN = str(x[1])
        y = com[2]
        yN = str(y[1])
        lhs = self.getVar(xN)
        rhs = self.getVar(yN)
        #check rhs if its not something like 2+2
        self.storeVarIn(y, 'B')
        if (isinstance(lhs, Int)): #x is a var
            if (lhs.iterator == True):
                self.err(str("ITERATOR CANNOT BE MODIFIED IN THE LOOP; LINE "+str(com[3])))
            lhs.ini = True
            self.out.store('B', lhs.address)
        elif (isinstance(lhs, Tab) and x[2][0] == "NUM"): #x is a tab[num]
            self.out.setAToKnownAddress(lhs.address, int(x[2][1]), "C", "D")
            self.out.c_store("B")
        else: #x is a tab[var]
            index = self.variables[x[2][1]].address
            self.out.setAToUnknownAddress(lhs.address, index, "C", "D") #sets index+arr value to regTo 
            self.out.c_store('B')
            
    def read(self, v):
        var = v[1]
        Machine.checkDec(self, var[1], v[2])
        if ((var[0] == "tab" and isinstance(self.getVar(var[1]), Int)) or (var[0] == "int" and isinstance(self.getVar(var[1]), Tab))):
            self.err(str("CRITICAL ERROR: TYPE MISMATCH, VARIABLE '"+str(var[1])+"' IN LINE "+str(var[len(var)-1])))
        if (var[0] == 'int'):
            self.getVar(var[1]).ini = True
            self.out.getInt(self.getVar(var[1]).address)
        elif (var[0] == 'tab'):
            t = self.getVar(var[1])
            if (var[2][0] == 'int'):
                index = self.variables[var[2][1]].address
                self.out.getTabVar(t.address, int(index))
            else:
                if (int(var[2][1])<t.min or int(var[2][1])>t.max):
                    self.err(str("CRITICAL ERROR: INVALID TABLE INDEX '"+str(var[2][1])+"' IN LINE "+str(var[3])))
                self.out.getTabNum(t.address, int(var[2][1])) #modify
        else:
            print("CRITICAL ERROR: READ MUST BE USED WITH A VARIABLE")
            exit()

    def write(self, v):
        var = v[1]
        if (var[0] != 'NUM'):
            if ((var[0] == "tab" and isinstance(self.getVar(var[1]), Int)) or (var[0] == "int" and isinstance(self.getVar(var[1]), Tab))):
                self.err(str("CRITICAL ERROR: TYPE MISMATCH, VARIABLE '"+str(var[1])+"' IN LINE "+str(var[len(var)-1])))
            Machine.checkDec(self, var[1], v[2])
            if (var[0] == 'int'):
                if(self.getVar(var[1]).ini == False):
                    self.err(str("USE OF UNINITIALIZED VARIABLE "+str(var[1])+" IN LINE "+str(var[2])))
                self.out.putInt(self.getVar(var[1]).address)
            elif (var[0] == 'tab'):
                t = self.getVar(var[1])
                if (var[2][0] == 'int'):
                    index = self.variables[var[2][1]].address
                    self.out.putTabVar(t.address, int(index))
                else:
                    if (int(var[2][1])<t.min or int(var[2][1])>t.max):
                        self.err(str("CRITICAL ERROR: INVALID TABLE INDEX '"+str(var[2][1])+"' IN LINE "+str(var[3])))
                    self.out.putTabNum(t.address, int(var[2][1]))
        else:
            self.out.putVal(int(var[1]))


    def condition(self, op, r1, r2):
        buffer = "H" #TODO: modify
        if (op == "="):
            self.eq(r1, r2, buffer)
        elif (op == "!="):
            self.ne(r1, r2, buffer)
        elif (op == ">="):
            self.ge(r1, r2)
        elif (op == "<="):
            self.le(r1, r2)
        elif (op == ">"):
            self.gt(r1, r2)
        elif (op == "<"):
            self.lt(r1, r2)

    def cond_if(self, com):
        cond = com[1]
        actions = com[2]
        op = cond[0]
        r1 = "B" #TODO: change later
        r2 = "C"
        label = self.getLabel()
        self.debugInfo("vvvvv IF values")
        self.storeVarIn(cond[1], r1)
        self.storeVarIn(cond[2], r2)
        self.debugInfo("vvvvv IF condition")
        self.condition(op, r1, r2)
        self.out.c_jzero(r1, label)
        self.debugInfo("vvvvv IF commands")
        self.perform(actions)
        self.out.addLabel(label)
        self.debugInfo("^^^^^ UP")

    def cond_ife(self, com):
        cond = com[1]
        true = com[2]
        false = com[3]
        op = cond[0]
        r1 = "B" #TODO: change later
        r2 = "C"
        label = self.getLabel()
        label2 = self.getLabel()
        self.debugInfo("vvvvv IF values")
        self.storeVarIn(cond[1], r1)
        self.storeVarIn(cond[2], r2)
        self.debugInfo("vvvvv IF condition")
        self.condition(op, r1, r2)
        self.out.c_jzero(r1, label)
        self.debugInfo("vvvvv IF commands")
        self.perform(true)
        self.out.c_jump(label2)
        self.out.addLabel(label)
        self.debugInfo("vvvvvvv ELSE")
        self.perform(false)
        self.out.addLabel(label2)
        self.debugInfo("^^^^^ UP")

    def debugInfo(self, s):
        #self.out.asm.append(s)
        return

    def loop_while(self, com): #if with a jump
        cond = com[1]
        actions = com[2]
        op = cond[0]
        r1 = "B" #TODO: change later
        r2 = "C"
        label = self.getLabel()
        label2 = self.getLabel()
        self.debugInfo("vvvvv WHILE LABEL/vals")
        self.out.addLabel(label)
        self.storeVarIn(cond[1], r1)
        self.storeVarIn(cond[2], r2)
        self.debugInfo("vvvvv WHILE condition")
        self.condition(op, r1, r2)
        self.out.c_jzero(r1, label2)
        self.debugInfo("vvvvv WHILE commands")
        self.perform(actions)
        self.out.c_jump(label)
        self.out.addLabel(label2)
        self.debugInfo("^^^^^ UP")

    def loop_do(self, com): #while with minor changes
        cond = com[2]
        actions = com[1]
        op = cond[0]
        r1 = "B" #TODO: change later
        r2 = "C"
        label = self.getLabel()
        self.debugInfo("vvvvv DO LABEL/commands")
        self.out.addLabel(label)
        self.perform(actions)
        self.debugInfo("vvvvv DO condition")
        self.storeVarIn(cond[1], r1)
        self.storeVarIn(cond[2], r2)
        self.condition(op, r1, r2)
        self.out.c_jzero(r1, label)
        self.debugInfo("^^^^^ UP")

    def loop_forT(self, com):
        actions = com[4]
        iterator = com[1]
        r1 = "B"
        r2 = "C"
        label = self.getLabel()
        label2 = self.getLabel()
        name = iterator+"END"
        self.declareIt(iterator)
        self.declareIt(name)
        self.storeVarIn(com[2], r1)
        self.storeVarIn(com[3], r2)
        self.out.store(r1, self.variables[iterator].address)
        self.out.store(r2, self.variables[name].address)
        self.out.addLabel(label)
        self.le(r1, r2)
        self.out.c_jzero(r1, label2)
        self.perform(actions)
        self.out.loadMemtoReg(self.variables[iterator].address, r1)
        self.out.c_inc(r1)
        self.out.c_store(r1)
        self.out.loadMemtoReg(self.variables[name].address, r2)
        self.out.c_jump(label)
        self.out.addLabel(label2)
        self.undeclareIt(iterator)
        self.undeclareIt(name)

    def loop_forD(self, com):
        actions = com[4]
        iterator = com[1]
        r1 = "B"
        r2 = "C"
        label = self.getLabel()
        label2 = self.getLabel()
        label3 = self.getLabel()
        name = iterator+"END"
        self.declareIt(iterator)
        self.declareIt(name)
        self.storeVarIn(com[2], r1)
        self.storeVarIn(com[3], r2)
        self.out.store(r1, self.variables[iterator].address)
        self.out.store(r2, self.variables[name].address)
        self.ge(r1, r2)
        self.out.c_jzero(r1, label3)
        self.perform(actions)
        self.out.loadMemtoReg(self.variables[iterator].address, r1)
        self.out.c_jzero(r1, label3)
        self.out.c_dec(r1)
        self.out.c_store(r1)
        self.out.loadMemtoReg(self.variables[name].address, r2)
        self.out.addLabel(label)
        self.gt(r1, r2)
        self.out.c_jzero(r1, label2)
        self.perform(actions)
        self.out.loadMemtoReg(self.variables[iterator].address, r1)
        self.out.c_jzero(r1, label3)
        self.out.c_dec(r1)
        self.out.c_store(r1)
        self.out.loadMemtoReg(self.variables[name].address, r2)
        self.out.c_jump(label)
        self.out.addLabel(label2)
        self.perform(actions)
        self.out.addLabel(label3)
        self.undeclareIt(iterator)
        self.undeclareIt(name)

class Register(object):
    def __init__(self, name):
        self.name = name
        self.var = None

class Int():
    def __init__(self, address = None, iterator = False):
        self.type = "int"
        self.address = address
        self.ini = False
        self.iterator = iterator

class Tab():
    def __init__(self, min, max, address = None):
        self.type = "tab"
        self.min = min
        self.max = max
        self.address = address

class Code():
    asm = []
    def clr(self, reg): #clears a register
        self.asm.append("SUB "+reg+" "+reg)

    def setValue(self, reg, val): #sets value at register
        self.clr(reg)
        instructions = []
        s1 = "INC "+reg
        s2 = "ADD "+reg+" "+reg
        while val > 10:
            if (val % 2 == 1):
                val -= 1
                instructions.append(s1)
            else:
                val = val // 2
                instructions.append(s2)
        instructions += [s1]*int(val)
        instructions.reverse()
        self.asm += instructions

    def store(self, reg, mem): #stores register at memory address
        self.setValue("A", mem)
        self.asm.append("STORE "+reg)
    
    def setOffset(self, mem, val):
        self.setValue("A", mem)
        self.setValue("B", val)
        self.c_store("B")

    def storeInt(self, mem, reg):
        self.setValue("A", mem)
        self.store(reg)

    def storeTabNum(self, arr, index, reg, buffer, buffer2):
        self.setAToKnownAddress(arr, index, buffer, buffer2)
        self.c_store(reg)

    def storeTabVar(self, arr, index, reg, buffer, buffer2):
        self.setAToUnknownAddress(arr, index, buffer, buffer2)
        self.c_store(reg)

    def loadInt(self, mem, reg):
        self.setValue("A", mem)
        self.c_load(reg)

    def loadTabNum(self, arr, index, reg, buffer, buffer2):
        self.setAToKnownAddress(arr, index, buffer, buffer2)
        self.c_load(reg)

    def loadTabVar(self, arr, index, reg, buffer, buffer2):
        self.setAToUnknownAddress(arr, index, buffer, buffer2)
        self.c_load(reg)

    def setAToKnownAddress(self, arr, index, buffer, buffer2):#sets A to the memory cell of arr@index
        self.setValue('A', arr)
        self.c_load(buffer) #offset
        self.setValue(buffer2, index)
        self.c_add('A', buffer2)
        self.c_sub('A', buffer)
        self.c_inc('A')

    def setAToUnknownAddress(self, arr, index, buffer, buffer2):#sets A to the memory cell of arr@index
        self.setValue('A', index)
        self.c_load(buffer2)
        self.setValue('A', arr)
        self.c_load(buffer) #offset
        self.c_add('A', buffer2)
        self.c_sub('A', buffer)
        self.c_inc('A')

    def loadMemtoReg(self, address, register):
        self.setValue('A', address)
        self.c_load(register)

    def c_load(self, reg):
        self.asm.append("LOAD "+reg)

    def c_store(self, reg):
        self.asm.append("STORE "+reg)
    
    def c_add(self, r1, r2):
        self.asm.append("ADD "+r1+" "+r2)
    
    def c_sub(self, r1, r2):
        self.asm.append("SUB "+r1+" "+r2)

    def c_inc(self, r):
        self.asm.append("INC "+r)

    def c_dec(self, r):
        self.asm.append("DEC "+r)

    def c_half(self, r):
        self.asm.append("HALF "+r)

    def c_copy(self, r1, r2):
        self.asm.append("COPY "+r1+" "+r2)

    def c_jump(self, j):
        self.asm.append("JUMP "+j)

    def c_jzero(self, r, j):
        self.asm.append("JZERO "+r+" "+j)

    def c_jodd(self, r, j):
        self.asm.append("JODD "+r+" "+j)
    
    def addLabel(self, label):
        self.asm.append(label)

    def c_put(self, r):
        self.asm.append("PUT "+r)
    
    def c_get(self, r):
        self.asm.append("GET "+r)

    def getInt(self, mem): 
        self.setValue("A", mem)
        self.c_get("B")
        self.c_store("B")

    def getTabNum(self, arr, index): 
        self.setAToKnownAddress(arr, index, "B", "C")
        self.c_get("B")
        self.c_store("B")

    def getTabVar(self, arr, index): 
        self.setAToUnknownAddress(arr, index, "B", "C")
        self.c_get("B")
        self.c_store("B")
    
    def putVal(self, val): 
        self.setValue("B", val)
        self.c_put("B") 

    def putInt(self, mem): 
        self.setValue("A", mem)
        self.c_load("B")
        self.c_put("B") 

    def putTabNum(self, arr, index): 
        self.setAToKnownAddress(arr, index, "B", "C")
        self.c_load("B")
        self.c_put("B") 

    def putTabVar(self, arr, index): 
        self.setAToUnknownAddress(arr, index, "B", "C")
        self.c_load("B")
        self.c_put("B")
    