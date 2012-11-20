from util.namedstruct import NamedStruct

class MachOCommand(NamedStruct):
	endianness = '<'
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I')
	)

class MachOSectionInfo(NamedStruct):
	S_REGULAR                             = 0x00
	S_ZEROFILL                            = 0x01
	S_CSTRING_LITERALS                    = 0x02
	S_4BYTE_LITERALS                      = 0x03
	S_8BYTE_LITERALS                      = 0x04
	S_LITERAL_POINTERS                    = 0x05
	S_NON_LAZY_SYMBOLS_STUBS              = 0x06
	S_LAZY_SYMBOL_POINTERS                = 0x07
	S_SYMBOL_STUBS                        = 0x08
	S_MOD_INIT_FUNC_POINTERS              = 0x09
	S_MOD_TERM_FUNC_POINTERS              = 0x0a
	S_COALESCED                           = 0x0b
	S_GB_ZEROFILL                         = 0x0c
	S_INTERPOSING                         = 0x0d
	S_16BYTE_LITERALS                     = 0x0e
	S_DTRACE_DOF                          = 0x0f
	S_LAZY_DYLIB_SYMBOL_POINTERS          = 0x10
	S_THREAD_LOCAL_REGULAR                = 0x11
	S_THREAD_LOCAL_ZEROFILL               = 0x12
	S_THREAD_LOCAL_VARIABLES              = 0x13
	S_THREAD_LOCAL_VARIABLE_POINTERS      = 0x14
	S_THREAD_LOCAL_INIT_FUNCTION_POINTERS = 0x15

	endianness = '<'
	definition = (
		('sectname', '16s'),
		('segname', '16s'),
		('addr', 'I'),
		('size', 'I'),
		('offset', 'I'),
		('align', 'I'),
		('reloff', 'I'),
		('nreloc', 'I'),
		('flags', 'I'),
		('reserved1', 'I'),
		('reserved2', 'I'),
	)

	@property
	def type(self):
		return self.flags & 0xFF

	def isPureInstructions(self):
		return self.flags & 0x80000000

	def hasSymbols(self):
		return (self.type == MachOSectionInfo.S_SYMBOL_STUBS) or \
		       (self.type == MachOSectionInfo.S_LAZY_SYMBOL_POINTERS) or \
		       (self.type == MachOSectionInfo.S_NON_LAZY_SYMBOLS_STUBS) or \
		       (self.type == MachOSectionInfo.S_LAZY_DYLIB_SYMBOL_POINTERS)

class MachOSegmentCommand(MachOCommand):
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I'),
		('segname', '16s'),
		('vmaddr', 'I'),
		('vmsize', 'I'),
		('fileoff', 'I'),
		('filesize', 'I'),
		('maxprot', 'I'),
		('initprot', 'I'),
		('nsects', 'I'),
		('flags', 'I'),
	)

	def __init__(self, data, offset=0):
		MachOCommand.__init__(self, data, offset)

		currentOffset = offset + self.sizeOfStruct()

		self.sections = []
		for i in xrange(self.nsects):
			sec = MachOSectionInfo(data, currentOffset)
			self.sections.append(MachOSectionInfo(data, currentOffset))
			currentOffset += sec.sizeOfStruct()

	def __str__(self):
		return '%s - %s' % (MachOCommand.__str__(self), '\n'.join(str(i) for i in self.sections))


class MachOSymtabCommand(MachOCommand):
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I'),
		('symoff', 'I'),
		('nsyms', 'I'),
		('stroff', 'I'),
		('strsize', 'I'),
	)

class MachODySymtabCommand(MachOCommand):
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I'),
		('ilocalsym', 'I'),
		('nlocalsym', 'I'),
		('iextdefsym', 'I'),
		('nextdefsym', 'I'),
		('iundefsym', 'I'),
		('nundefsym', 'I'),
		('tocoff', 'I'),
		('ntoc', 'I'),
		('modtaboff', 'I'),
		('nmodtab', 'I'),
		('extrefsymoff', 'I'),
		('nextrefsyms', 'I'),
		('indirectsymoff', 'I'),
		('nindirectsyms', 'I'),
		('extreloff', 'I'),
		('nextrel', 'I'),
		('locreloff', 'I'),
		('nlocrel', 'I'),
	)

class MachOLoadDylinkerCommand(MachOCommand):
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I'),
		('offset', 'I'),
	)

class MachOThreadStateCommand(MachOCommand):
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I'),
		('flavour', 'I'),
		('count', 'I'),
		('eax', 'I'),
   		('ebx', 'I'),
   		('ecx', 'I'),
   		('edx', 'I'),
   		('edi', 'I'),
   		('esi', 'I'),
   		('ebp', 'I'),
   		('esp', 'I'),
   		('ss', 'I'),
   		('eflags', 'I'),
   		('eip', 'I'),
   		('cs', 'I'),
   		('ds', 'I'),
   		('es', 'I'),
   		('fs', 'I'),
   		('gs', 'I'),
	)

class MachOLoadDylibCommand(MachOCommand):
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I'),
		('name', 'I'),
		('timestamp', 'I'),
		('current_version', 'I'),
		('compatibility_version', 'I'),
	)

class MachOUUIDCommand(MachOCommand):
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I'),
		#('uuid', '32s'),
	)

class MachOCodeSignatureCommand(MachOCommand):
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I'),
		('dataoff', 'I'),
		('datasize', 'I'),
	)

class MachOVersionMinOSXCommand(MachOCommand):
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I'),
	)	

class MachOFunctionStartsCommand(MachOCommand):
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I'),
	)	

class MachODyldInfoOnlyCommand(MachOCommand):
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I'),
	)	

def ParseMachOCommand(data, offset):
	commands = {
		0x01: MachOSegmentCommand,
		0x02: MachOSymtabCommand,
		0x05: MachOThreadStateCommand,
		0x0b: MachODySymtabCommand,
		0x0c: MachOLoadDylibCommand,
		0x0e: MachOLoadDylinkerCommand,
		0x1b: MachOUUIDCommand,
		0x1d: MachOCodeSignatureCommand,
		0x24: MachOVersionMinOSXCommand,
		0x26: MachOFunctionStartsCommand,

		0x80000022: MachODyldInfoOnlyCommand,
	}

	command = MachOCommand(data, offset)
	commandClass = commands.get(command.cmd, MachOCommand)
	command = commandClass(data, offset)

	return command, offset + command.cmdsize
