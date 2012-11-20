from commands import *
from util.namedstruct import *
from util.util import *
from pymsasid import *
from process.process import *

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

class NListEntry(NamedStruct):
	endianness = '<'
	definition = (
		('n_strx', 'i'),
		('n_type', 'B'),
		('n_sect', 'B'),
		('n_desc', 'h'),
		('n_value', 'I'),
	)

class IndirectSymbol(object):
	# if self.value == 0x80000000: flags_string += ' #LOCAL# '
	# if self.value == 0x40000000: flags_string += ' #ABSOLUTE# '
	# if self.value == 0x40000000 | 0x80000000: flags_string += ' #LOCAL ABSOLUTE# '

	# if flags & 0xe0: flags_string += 'N_STAB '
	# if flags & 0x10: flags_string += 'N_PEXT '
	# if flags & 0x01: flags_string += 'N_EXT '
	# if flags & 0xe == 0: flags_string += 'N_UNDF'
	# if flags & 0x02: flags_string += 'N_ABS'
	# if flags & 0x0e: flags_string += 'N_SECT'
	# if flags & 0x0c: flags_string += 'N_PBUD'
	# if flags & 0x0a: flags_string += 'N_INDR'

	def __init__(self, value):
		self.value = value

	@property
	def index(self):
		return (self.value & 0x00FFFFFF)

	@property
	def flags(self):
		return (self.value & 0xFF000000) >> 24

class MachOFile(object):
	def __init__(self, data):
		self.data     = data
		self.header   = MachOHeader(data)

		self.sections = []
		self.symbols  = {}

		nlist = []
		machosections = []
		indirect_symbols = []
		symbols_names = []

		currentOffset = 7 * 4
		for i in xrange(self.header.numberOfCommands):
			command, currentOffset = ParseMachOCommand(data, currentOffset)

			if isinstance(command, MachOSegmentCommand):
				for section in command.sections:
					machosections.append(section)
					name = '%s.%s' % (section.segname, section.sectname)
					secdata = self.data[section.offset:section.offset + section.size]
					sectionClass = CodeSection if section.isPureInstructions() else Section
					self.sections.append(sectionClass(name,
						                              section.addr,
						                              section.size,
						                              secdata))

			if isinstance(command, MachOSymtabCommand):
				symbOffset = command.symoff
				for i in xrange(command.nsyms):
					e = NListEntry(self.data, symbOffset)
					nlist.append(e)
					symbols_names.append(getZeroTerminatedString(self.data, command.stroff + e.n_strx))
					symbOffset += e.sizeOfStruct()

			if isinstance(command, MachODySymtabCommand):
				for i in xrange(command.nindirectsyms):
					value = struct.unpack_from('<I', self.data, command.indirectsymoff + i * 4)[0]
					indirect_symbols.append(IndirectSymbol(value))

		for section in machosections:
			if section.hasSymbols():
				stride = section.reserved2 if section.type == MachOSectionInfo.S_SYMBOL_STUBS else 4
				count = section.size / stride
				n = section.reserved1

				for i in xrange(count):
					symbolAddress = section.addr + (i * stride)
					symbol = indirect_symbols[i + n]
					self.symbols[symbolAddress] = symbols_names[symbol.index]

	def __str__(self):
		return 'Number of commands: %s\n%s\nSections:\n%s' % (self.header.numberOfCommands, '\n'.join([str(i) for i in self.commands]), '\n'.join([str(i) for i in self.sections]))

	@staticmethod
	def canLoad(data):
		magic = struct.unpack_from('<I', data)[0]
		return magic == 0xfeedface

class MachOFatFile(MachOFile):
	def __init__(self, data):
		header = MachOFatHeader(data)

		for i in xrange(header.numberOfArchs):
			arch = MachOFatArchsTable(data, 8 + 20 * i)

			if arch.cputype == 7: # 7 == intel 32 bit
				MachOFile.__init__(self, data[arch.offset:arch.offset + arch.datasize])

	@staticmethod
	def canLoad(data):
		header = MachOFatHeader(data)
	
		if header.magic != 0xcafebabe:
			return False

		for i in xrange(header.numberOfArchs):
			arch = MachOFatArchsTable(data, 8 + 20 * i)

			if arch.cputype == 7: # 7 == intel 32 bit
				return True

		return False
