from commands import *
from util.namedstruct import *

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

		currentOffset = 7 * 4
		for i in xrange(self.header.numberOfCommands):
			command, currentOffset = ParseMachOCommand(data, currentOffset)
			self.commands.append(command)	

	def __str__(self):
		return 'Number of commands: %s\n%s' % (self.header.numberOfCommands, '\n'.join([str(i) for i in self.commands]))

def loadMachOFileData(data):
	header = MachOHeader(data)

	if header.magic != 0xfeedface:
		return None

	filo = MachOFile(data)
	return str(filo)


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
