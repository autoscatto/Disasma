from commands import *
from util.namedstruct import *
from pymsasid import *

class MachOFatHeader(NamedStruct):
	endianness = '>'
	definition = (
		('magic', 'I'),
		('numberOfArchs', 'I')
	)

class MachOFatArchsTable(NamedStruct):
	endianness = '>'
	definition = (
		('cputype', 'i'),
		('cpusubtype', 'i'),
		('offset', 'I'),
		('datasize', 'I'),
		('alignment', 'I'),
	)

class MachOHeader(NamedStruct):
	endianness = '<'
	definition = (
		('magic', 'I'),
		('cputype', 'i'),
		('cpusubtype', 'i'),
		('filetype', 'I'),
		('numberOfCommands', 'I'),
		('sizeOfCommands', 'I'),
		('flags', 'I'),
	)

class MachOFile(object):
	def __init__(self, data):
		self.data     = data
		self.header   = MachOHeader(data)
		self.commands = []
		self.sections = []

		currentOffset = 7 * 4
		for i in xrange(self.header.numberOfCommands):
			command, currentOffset = ParseMachOCommand(data, currentOffset)
			self.commands.append(command)

			if isinstance(command, MachOSegmentCommand):
				self.sections = self.sections + command.sections

	def __str__(self):
		return 'Number of commands: %s\n%s\nSections:\n%s' % (self.header.numberOfCommands, '\n'.join([str(i) for i in self.commands]), '\n'.join([str(i) for i in self.sections]))


	def disassa(self):
		out  = []
		prog = pymsasid.Pymsasid(hook   = pymsasid.BufferHook,
			                     source = self.data,
		                         mode   = 32)

		for section in self.sections:
			if section.isPureInstructions():
				sectionTitle = 'Disassembly of section %s.%s' % (section.segname, section.sectname)
				out.append(sectionTitle)
				out.append('-' * len(sectionTitle))
				out.append('')

				currentOffset = section.offset
				prog.input.base_address = section.addr

				while currentOffset < section.addr + section.size:
					instruction = prog.disassemble(currentOffset)
					out.append('[%08x] %s' % (currentOffset, str(instruction)))
					currentOffset += instruction.size

				out.append('\n\n')

		return '\n'.join(out)

def loadMachOFileData(data):
	header = MachOHeader(data)

	if header.magic != 0xfeedface:
		return None

	filo = MachOFile(data)
	return filo.disassa()


def loadMachOFatFile(filename):
	inputfile = open(filename, 'r').read()
	header = MachOFatHeader(inputfile)
	
	if header.magic != 0xcafebabe:
		return None

	for i in xrange(header.numberOfArchs):
		arch = MachOFatArchsTable(inputfile, 8 + 20 * i)

		if arch.cputype == 7: # 7 == intel 32 bit
			return loadMachOFileData(inputfile[arch.offset:arch.offset + arch.datasize])

	return None
