from namedstruct import NamedStruct

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
		('size', 'I'),
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

class MachOCommand(NamedStruct):
	endianness = '<'
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I')
	)

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
