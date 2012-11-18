from util.namedstruct import *

class ElfHeader(NamedStruct):
	endianness = '<'
	definition = (
		('e_ident', '16s'), 	# The magic
		('e_type', 'H'),
		('e_machine', 'H'),
		('e_version', 'I'),
		('e_entry', 'I'),		# Address
		('e_phoff', 'I'), 		# Offset
		('e_shoff', 'I'),		# Offset	
		('e_flags', 'I'),
		('e_ehsize', 'H'),
		('e_phentsize', 'H'),
		('e_phnum', 'H'),
		('e_shentsize', 'H'),
		('e_shnum', 'H'),
		('e_shstrndx', 'H')
	)

class ElfProgramHeader(NamedStruct):
	endianness = '<'
	definition = (
		('p_type', 'I'),
		('p_offset', 'I'),
		('p_vaddr', 'I'),
		('p_paddr', 'I'),
		('p_filesz', 'I'),
		('p_memsz', 'I'),
		('p_flags', 'I'),
		('p_align', 'I')
	)

class ElfSectionHeader(NamedStruct):
	endianness = '<'
	definition = (
		('sh_name', 'I'),
		('sh_type', 'I'),
		('sh_flags', 'I'),
		('sh_addr', 'I'),
		('sh_offset', 'I'),
		('sh_size', 'I'),
		('sh_link', 'I'),
		('sh_info', 'I'),
		('sh_addralign', 'I'),
		('sh_entsize', 'I')
	)

class ElfSymbolTableEntry(NamedStruct):
	endianness = '<'
	definition = (
		('st_name', 'I'),
		('st_value', 'I'),
		('st_size', 'I'),
		('st_info', 'B'),
		('st_other', 'B'),
		('st_shndx', 'H')
	)

class ElfRelocation(NamedStruct):
	endianness = '<'
	definition = (
		('r_offset', 'I'),
		('r_info', 'I')
	)

class ElfRelocationWithAddend(NamedStruct):
	endianness = '<'
	definition = (
		('r_offset', 'I'),
		('r_info', 'I'),
		('r_addend', 'I')
	)

class ElfFile(object):
	def __init__(self, data):
		self.data     = data
		self.header   = ElfHeader(data)
		self.commands = []

		phoff  		= self.header.e_phoff
		phentsize 	= self.header.e_phentsize
		phnum 		= self.header.e_phnum

		print self.header
		for i in xrange(phnum):
			phentry = ElfProgramHeader(self.data[phoff+i*phentsize:])
			print phentry

		shoff 		= self.header.e_shoff
		shentsize 	= self.header.e_shentsize
		shnum 		= self.header.e_shnum

		for i in xrange(shnum):
			shentry = ElfSymbolTableEntry(self.data[shoff+i*shentsize:])
			print shentry

def loadElfFile(filename):
	inputfile = open(filename, 'r').read()
	header = ElfHeader(inputfile)

	print "ASDFASF"
	ElfFile(inputfile)
	print header.e_ident