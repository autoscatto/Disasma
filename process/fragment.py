from pymsasid import *

class DataFragment:
    def __init__(self, data, start):
        self.data = data
        self.start = start
        self.size = len(data)

    def __str__(self):
        out = []
        offset = 0

        for d in self.data:
            out.append('[%08x]' % (self.start + offset))
            out.append('%-4s' % 'db')
            out.append('0x%02x' % ord(d))
            if ord(d) > 31 and ord(d) < 127:
                out.append(' ; \'%s\'' % d)
            out.append('\n')

            offset += 1

        return ''.join(out)

    def getHtml(self):
        out = []
        offset = 0

        out.append('<div class="fragment">\n')
        for d in self.data:
            addr = self.start+offset
            out.append('<div class="row">\n')

            out.append('<div class="toggle" onclick="sv.viewAs(\'code\', %d, %d)">D  </div>' % (addr, addr+1))
            out.append('<div>[</div>')
            out.append('<div class="address" id="%08x">%08x</div>' % (addr, addr))
            out.append('<div>]</div>\n')

            out.append('  <div class="operator">%4s</div>\n' % 'db')
            out.append('  <div class="constant">%02x</div>\n' % ord(d))

            if ord(d) > 31 and ord(d) < 127:
                out.append('  <div class="comment"> ; \'%s\'\n' % d)

            out.append('</div>\n')
            out.append('<br/>\n')
            offset += 1

        out.append('</div>\n')

        return ''.join(out)

class CodeFragment:
    def __init__(self, data, start):
        self.data = data
        self.start = start
        self.size = len(data)

    def __str__(self):
        #out = [title, '-' * len(title), '']
        out = []
        prog = pymsasid.Pymsasid(hook   = pymsasid.BufferHook,
                                 source = self.data,
                                 mode   = 32)
        
        prog.input.hook.base_address = self.start
        currentOffset = self.start

        instructions = []

        while currentOffset < self.start + self.size:
            #print currentOffset, self.start, self.size
            instruction = prog.disassemble(currentOffset)
            currentOffset += instruction.size
            if instruction.size == 0:
                instruction.pc = currentOffset
                currentOffset += self.size
            instructions.append(instruction)
        
        for instruction in instructions:
            addr = instruction.pc - instruction.size
            '''
            name = self.process.symbols.get(addr, None)
            if name:
                out.append(' [%08x]\n [%08x] %s:' % (addr, addr, name))
            '''
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

                '''if address:
                    symbol = self.process.symbols.get(address, None)
                    if symbol:
                        return symbol
                '''
                try:
                    q = repr(operand)
                except:
                    q = "Invalid."
                return q


            out.append(' [%08x] %-8s\t%s<br/>' % (addr, str(instruction.operator), ', '.join(map(operand_to_str, instruction.operand))))
            #out.append(' [%08x] %-8s\t%s' % (addr, str(instruction.operator), ' - '.join([str (i) for i in instruction.operand])))

        return '\n'.join(out) + '\n\n'

    def getHtml(self):
        return self.__str__()