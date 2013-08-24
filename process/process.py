from util.intervalmap import intervalmap
from pymsasid import *
# from fragment import *
import templazza

class Partitioner(object):
    def __init__(self, a, b, t):
        self.intervals = [(a, b, t)]

    ##
    #  @param interval: an interval of the form [a, b)
    #  @param value: the value to be assigned to the interval
    def __setitem__(self, interval, value):
        assert isinstance(interval, slice)
        a = interval.start
        b = interval.stop
        assert a < b
        
        # Every interval who does not intersect with the new interval
        # to be inserted is left unchanged, the others are checked
        # with the only 2 significant cases, or else just ignored.
        t = []
        ab = set(range(a, b))
        for i in self.intervals:
            r = range(i[0], i[1])
            if set(r).intersection(ab) == set([]):
                t.append(i)
            else:
                if i[0] < a:
                    t.append((i[0], a, i[2]))
                if i[1] >= b:
                    t.append((a, b, value))
                    if b < i[1]:
                        t.append((b, i[1], i[2]))

        # Applying a fold-left in the list of intervals, every time
        # two adjacent intervals have the same value, they are merged 
        self.intervals = reduce(
            lambda x, y: (
                [y] if x == []
                else (
                    x[:-1] + [(x[-1][0], y[1], y[2])] if x[-1][2] == y[2]
                    else x + [y]
                )
            ), t, []
        )

    def items(self):
        return self.intervals
        
## Represents a process section in a generic fashion.
#  A Section contains its name, its actual data, its starting address in VM
#  and the data size.
class Section(object):
    def __init__(self,
                 name  = '',
                 start = 0,
                 size  = 0,
                 data  = None):
        self.name  = name
        self.start = start
        self.size  = size
        self.data  = data

        ## This Partitioner defines which portions of the section are to be
        #  decoded as data and which ones as code
        if name in ['.text','.init'] or ('__TEXT' in name):
            self.cdmap = Partitioner(0, size, 'C')
        else:
            self.cdmap = Partitioner(0, size, 'D')

    @property
    def end(self):
        return self.start + self.size

    def __instructions_from_data__(self, rawdata, base_address):
        offset = base_address
        instructions = []
        prog = pymsasid.Pymsasid(hook   = pymsasid.BufferHook,
                                 source = rawdata,
                                 mode   = 32)
        
        prog.input.hook.base_address = base_address
        
        while offset < base_address + len(rawdata):
            instruction = prog.disassemble(offset)
            offset += instruction.size
            if instruction.size == 0:
                instruction.pc = offset+1
                instruction.size = 1
                print instruction.pc
                offset += len(rawdata)
            instructions.append(instruction)
            
        return instructions

    def __str__(self):
        def __datastr__(rawdata, base_address):
            ret = ''
            offset = 0
            for d in rawdata:
                if ord(d) > 31 and ord(d) < 127:
                    ret += templazza.cli_data_char_template \
                               % (base_address + offset, 'db', ord(d), d)
                else:
                    ret += templazza.cli_data_template \
                               % (base_address + offset, 'db', ord(d))
                offset += 1
            return ret

        #TODO: fix
        def __codestr__(rawdata, base_address):
            ret = []
            instrs = self.__instructions_from_data__(rawdata, base_address)

            for instruction in instrs:
                addr = instruction.pc - instruction.size
    
                def operand_to_str(operand):
                    address = None
    
                    if operand.type == 'OP_JIMM':
                        try:
                            address = operand.lval + operand.pc # - instruction.size?
                        except:
                            address = -1
    
                    if operand.type == 'OP_MEM' and operand.base is None:
                        try:
                            address = operand.lval + operand.pc # - instruction.size?
                        except:
                            address = -1
    
                    try:
                        q = repr(operand)
                    except:
                        q = "Invalid."
                    return q

                ret.append(' [%08x] %-8s\t%s' % (addr, str(instruction.operator), ', '.join(map(operand_to_str, instruction.operand))))
            return '\n'.join(ret) + '\n\n'
        
        fun = {'D': __datastr__, 'C': __codestr__}
        out = []
        for (interval, f) in self.cdmap.items():
            if interval[0] != interval[1]:
                out.append(
                    fun[f](self.data[interval[0]:interval[1]],
                           interval[0] + self.start)
                )
                
        return ''.join(out)

    def getHTML(self):
        def __dataHTML__(rawdata, base_address):
            ret = ''
            offset = 0
            for d in rawdata:
                addr = base_address + offset
                if ord(d) > 31 and ord(d) < 127:
                    ret += templazza.html_data_char_template \
                           % (addr, addr+1, addr, addr, 'db', ord(d), d)
                else:
                    ret += templazza.html_data_template \
                           % (addr, addr+1, addr, addr, 'db', ord(d))
                offset += 1
            return ret

        def __codeHTML__(rawdata, base_address):

            ret = ''
            instrs = self.__instructions_from_data__(rawdata, base_address)
            
            optempl = {
                'OP_REG' : lambda op: templazza.html_code_op_reg % (op.base),
                'OP_MEM' : lambda op: templazza.html_code_op_mem \
                               % (op.lval + op.pc, '-' * (op.lval < 0),
                                  abs(op.lval)),
                'OP_JIMM': lambda op: templazza.html_code_op_jimm \
                               % (op.lval + op.pc, '-' * (op.lval < 0),
                                  abs(op.lval)),
                'OP_IMM' : lambda op: templazza.html_code_op_imm \
                               % ('-' * (op.lval < 0), abs(op.lval))
            }
            
            for instruction in instrs:
                sz = instruction.size
                addr = instruction.pc - instruction.size
                ops = []
                for i in range(0, len(instruction.operand)):
                    op = instruction.operand[i]
                    try:
                        ops.append(optempl[op.type](op))
                    except Exception:
                    	pass
                ret += templazza.html_code_template % \
                    (addr, addr + sz, addr, addr, \
                     str(instruction.operator), ','.join(ops))
            return ret

        fun = {'D': __dataHTML__, 'C': __codeHTML__}
        out = [fun[f](self.data[a:b], a + self.start) 
                for (a, b, f) in self.cdmap.items()]
            
        return ''.join(out)


class Process(object):
    def __init__(self):
        self.sections = intervalmap()

    def addSection(self, section):
        self.sections[section.start : section.end] = section
        section.process = self

    def __getitem__(self, key):
        section = self.sections[key]
        return section.data[key - section.start]

    def __str__(self):
        return '\n'.join(str(section) for interval, section in self.sections.items())

    def getHTML(self):
        return '\n'.join(section.getHTML() for interval, section in self.sections.items())
