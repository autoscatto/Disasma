from util.intervalmap import intervalmap
from pymsasid import *

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

	@property
	def end(self):
		return self.start + self.size

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

			out.append(' [%08x] %-8s\t%s' % (addr, str(instruction.operator), str(instruction.operand)[1:-1]))
			#out.append(' [%08x] %-8s\t%s' % (instruction.pc, str(instruction.operator), ' - '.join([str (i) for i in instruction.operand])))

		return '\n'.join(out) + '\n\n'

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
		return '\n'.join(str(section) for interval, section in self.sections.items()) + str(self.symbols)
