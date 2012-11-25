from util.intervalmap import intervalmap
from pymsasid import *
from fragment import *

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

        self.fragments = intervalmap()
        if name == '.text' or ('__TEXT' in name):
            self.fragments[start:start+size] = CodeFragment(data[0:size], start)
        else:
            self.fragments[start:start+size] = DataFragment(data[0:size], start)

    @property
    def end(self):
        return self.start + self.size

    def addFragment(self, fragType, start, end):
        dstart = start - self.start
        dend = dstart + (end - start)
        data = self.data[dstart:dend]

        prev = self.fragments[start]
        next = self.fragments[end]

        frag = None

        if prev != next:
            if type(prev) == fragType and type(next) == fragType:
                print "This actually shouldn't happen"
            # Enlarge your prev
            elif type(prev) == fragType and type(next) != fragType:
                prev.resize(end-prev.start, 1, data[end-prev.start-prev.size:])
                next.resize(next.end-end, 0)
                self.fragments[prev.start:prev.end] = prev
            # Enlarge your next
            elif type(prev) != fragType and type(next) == fragType:
                next.resize(next.end-start, 0, data[0:next.start-start])
                prev.resize(start-prev.start, 1)
                self.fragments[next.start:next.end] = next
            # Enlarge staceppa, must add a new fragment
            else:
                next.resize(next.end-end, 0)
                prev.resize(start-prev.start, 1)

                frag = fragType(data, start)
        else:
            # Need to place it at the beginning
            if start == prev.start and type(prev) != fragType:
                #print start, prev.start, end, prev.end
                frag12 = prev.split(end-start)
                prev.resize(prev.size-end+start, 0)
                frag = fragType(frag12[0].data, frag12[0].start)

            # Need to place it in the middle of prev
            elif start != prev.start and end != prev.start + prev.size and type(prev) != fragType:
                frag123 = prev.doubleSplit(start-prev.start, end-prev.start)

                assert prev.size == frag123[0].size+frag123[1].size+frag123[2].size

                #print "%08x %08x %08x" %(frag123[0].start, frag123[1].start, frag123[2].start)
                frag = fragType(frag123[1].data, frag123[1].start)

                self.fragments[frag123[0].start:frag123[0].end] = prev.__class__(frag123[0].data, frag123[0].start)
                self.fragments[frag123[2].start:frag123[2].end] = prev.__class__(frag123[2].data, frag123[2].start)

                #del prev

            # Need to place it at the end
            elif type(prev) != fragType:
                frag12 = prev.split(start-prev.start)

                frag1 = prev.__class__(frag12[0].data, frag12[0].start)
                frag = fragType(frag12[1].data, frag12[1].start)

                self.fragments[frag1.start:frag1.end] = frag1

        if frag != None:
            if fragType == type(self.fragments[start-1]):
                x = self.fragments[start-1]
                x.resize(x.size+frag.size, 1, data)
                self.fragments[x.start:x.end] = x
            else:
                self.fragments[start:end] = frag


    '''
    def __str__(self):
        def printablechar(x):
            return x if x > 31 and x < 127 else ord('.')

        title = 'Section ' + self.name + ':'
        #out = [title, '-' * len(title), '']
        out = [title]
        line = []
        asciistring = []
        for i, char in enumerate(self.data):
            line.append('%02x ' % ord(char))
            asciistring.append(chr(printablechar(ord(char))))

            if (i + 1) % 4 == 0:
                line.append('  ')

            if (i + 1) % 16 == 0:
                linestring = ''.join(line)
                offsetstring = ' %08x  |  ' % ((i-15) + self.start)
                ascii = ''.join(asciistring)
                out.append(offsetstring + linestring + '  |  ' + ascii)
                line = []
                asciistring = []

        i += 1
        while i % 16 != 0:
            line.append('   ')
            asciistring.append(' ')

            if (i + 1) % 4 == 0:
                line.append('  ')

            if (i + 1) % 16 == 0:
                linestring = ''.join(line)
                offsetstring = ' %08x  |  ' % ((i-15) + self.start)
                ascii = ''.join(asciistring)
                out.append(offsetstring + linestring + '  |  ' + ascii)
                line = []
                asciistring = []
            i += 1
            
        return '\n'.join(out) + '\n\n'
    '''
    def __str__(self):
        out = []
        for (interval, f) in self.fragments.items():
            if interval[0] != interval[1]:
                out.append(str(f))
        return ''.join(out)

    def getHTML(self):
        out = []
        out.append('    <div class="section">\n')

        for (interval, f) in self.fragments.items():

            if interval[0] != interval[1]:
                out.append(f.getHtml())

        out.append('    </div>\n')
        out.append('  </body>\n')
        out.append('</html>')

        return ''.join(out)

'''
    def getHTML(self):
        content = '<div class="content">'
        title = '<div class="row"><div class="section">== Section %s : ==</div></div><br/>\n' % self.name
        out = [content, title]

        for (i, char) in enumerate(self.data):
            addr = i+self.start
            v = ord(char)
            out.append('<div class="row">')
            out.append('<div> [</div>' + \
                '<div class="address" id="%08x">%08x</div>' % (addr, addr) + \
                '<div>] </div>')
            out.append('<div class="operator">%-8s\t</div>' % 'db')
            out.append('<div class="constant">%02x</div>' % v)
            if v > 31 and v < 127:
                out.append('<div class="comment"> ; \'%s\'</div>' % char)
            out.append('<br/>')

        out.append('</div>')
        return ''.join(out)
'''

'''
class CodeSection(Section):
    def __str__(self):
        title = 'Section ' + self.name + ':'
        #out = [title, '-' * len(title), '']
        out = [title]
        prog = pymsasid.Pymsasid(hook   = pymsasid.BufferHook,
                                 source = self.data,
                                 mode   = 32)
        
        prog.input.hook.base_address = self.start
        currentOffset = self.start

        instructions = []
        xrefs = {}

        while currentOffset < self.start + self.size:
            instruction = prog.disassemble(currentOffset)
            currentOffset += instruction.size
            instructions.append(instruction)

            for br in instruction.branch():
                if br != instruction.pc:
                    try:
                        xr = xrefs.get(br, [])
                        xr.append(instruction.pc - instruction.size)
                        xrefs[br] = xr
                    except:
                        continue
        
        for instruction in instructions:
            addr = instruction.pc - instruction.size
            name = self.process.symbols.get(addr, None)
            if name:
                out.append(' [%08x]\n [%08x] %s:' % (addr, addr, name))

            xr = xrefs.get(addr, None)
            if xr:
                if not name:
                    out.append(' [%08x]' % addr)

                xrefstring = ', '.join(('%08x' % i for i in xr))
                out.append(' [%08x] X-Refs from: %s' % (addr, xrefstring))

            def operand_to_str(operand):
                address = None

                if operand.type == 'OP_JIMM':
                    address = operand.lval + operand.pc # - instruction.size?

                if operand.type == 'OP_MEM' and operand.base is None:
                    address = operand.lval + operand.pc # - instruction.size?

                if address:
                    symbol = self.process.symbols.get(address, None)
                    if symbol:
                        return symbol

                return repr(operand)


            out.append(' [%08x] %-8s\t%s' % (addr, str(instruction.operator), ', '.join(map(operand_to_str, instruction.operand))))
            #out.append(' [%08x] %-8s\t%s' % (addr, str(instruction.operator), ' - '.join([str (i) for i in instruction.operand])))

        return '\n'.join(out) + '\n\n'

    def getHTML(self):
        content = '<div class="content">'
        title = '<div class="row"><div class="section">== Section %s : ==</div></div><br/>\n' % self.name
        out = [content, title]
        prog = pymsasid.Pymsasid(hook   = pymsasid.BufferHook,
                                 source = self.data,
                                 mode   = 32)
        
        prog.input.hook.base_address = self.start
        currentOffset = self.start

        instructions = []
        xrefs = {}

        while currentOffset < self.start + self.size:
            instruction = prog.disassemble(currentOffset)
            currentOffset += instruction.size
            instructions.append(instruction)

            for br in instruction.branch():
                if br != instruction.pc:
                    try:
                        xr = xrefs.get(br, [])
                        xr.append(instruction.pc - instruction.size)
                        xrefs[br] = xr
                    except:
                        continue

        #print xrefs and names
        for instruction in instructions:
            sz = instruction.size
            addr = instruction.pc - instruction.size
            name = self.process.symbols.get(addr, None)

            htmlAddr = '<div> [</div><div class="address">%08x</div><div>] </div>' % (addr)

            if name:
                out.append('<div class="row">%s</div><br/>' % htmlAddr)
                out.append('<div class="row">%s<div id="ref_%s" type="refname">%s</div></div><br/>' % \
                    (htmlAddr, name, name))

            xr = xrefs.get(instruction.pc, None)
            if xr:
                out.append('<div class="row">')
                xrefstring = ', '.join(('<a href="#%08x"><div class="xref">%08x</div></a>' % (i, i) for i in xr))
                out.append('%s<div class="xref">X-Refs from: %s</div><br/>\n' % \
                    (htmlAddr, xrefstring))
                out.append('</div>')
            
            out.append('<div class="row">')
            out.append('<div> [</div>' + \
                '<div class="address" id="%08x">%08x</div>' % \
                (addr, addr) + \
                '<div>] </div>')
            out.append('<div class="operator">%-8s\t</div>' % str(instruction.operator))

            for i in range(0, len(instruction.operand)):
                op = instruction.operand[i]
                
                if op.type == 'OP_REG':
                    out.append('<div class="operand_register">%s</div>' % op.base)
                elif op.type == 'OP_MEM':
                    name = self.process.symbols.get(op.lval + op.pc, None)
                    if name:
                        out.append('<a href="#ref_%s"><div class="operand_reference">%s</div></a>' \
                            % (name, name))
                    else:
                        out.append('<div>[</div>' + \
                            '<a href="#%08x"><div class="operand_address">%s0x%x</div></a>' \
                            % (op.lval + op.pc - sz, '-' * (op.lval < 0), abs(op.lval))
                            + '<div>]</div>')
                elif op.type == 'OP_JIMM':
                    name = self.process.symbols.get(op.lval + op.pc, None)
                    if name:
                        out.append('<a href="#ref_%s"><div class="operand_reference">%s</div></a>' \
                            % (name, name))
                    else:
                        out.append('<a href="#%08x"><div class="operand_address">%s0x%x</div></a>' \
                            % (op.lval + op.pc, '-' * (op.lval < 0), abs(op.lval)))
                elif op.type == 'OP_IMM':
                    out.append('<div class="operand_immediate">%s0x%x</div>' \
                        % ('-' * (op.lval < 0), op.lval))
                else:
                    out.append('<div class="operand">QUALCOSA di tipo %s</div>' % op.type)

                if i < len(instruction.operand) - 1:
                    out.append('<div>, </div>')
            # end row
            out.append('</div>')
            out.append('<br/>\n')

        out.append('</div>')
        return ''.join(out)
'''

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
