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

		title = 'Section ' + self.name
		out = [title, '-' * len(title), '']

		line = []
		asciistring = []
		for i, char in enumerate(self.data):
			line.append('%02x ' % ord(char))
			asciistring.append(chr(printablechar(ord(char))))

			if (i + 1) % 4 == 0:
				line.append('  ')

			if (i + 1) % 16 == 0:
				linestring = ''.join(line)
				offsetstring = '%08x  |  ' % (i + self.start)
				ascii = ''.join(asciistring)
				out.append(offsetstring + linestring + '  |  ' + ascii)
				line = []
				asciistring = []

		return '\n'.join(out) + '\n\n'

class CodeSection(Section):
	def __str__(self):
		title = 'Section ' + self.name
		out = [title, '-' * len(title), '']

		prog = pymsasid.Pymsasid(hook   = pymsasid.BufferHook,
			                     source = self.data,
		                         mode   = 32)

		prog.input.base_address = self.start
		currentOffset = 0

		while currentOffset < self.size:
			instruction = prog.disassemble(currentOffset)
			out.append('[%08x] %s' % (currentOffset + self.start, str(instruction)))
			currentOffset += instruction.size

		return '\n'.join(out) + '\n\n'

class Process(object):
	def __init__(self):
		self.sections = intervalmap()

	def addSection(self, section):
		self.sections[section.start : section.end] = section

	def __getitem__(self, key):
		section = self.sections[key]
		return section.data[key - section.start]

	def __str__(self):
		return '\n'.join(str(section) for interval, section in self.sections.items())
