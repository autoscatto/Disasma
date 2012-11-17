from macho.commands import *

def loadMachOFileData(data):
	header = MachOHeader(data)

	if header.magic != 0xfeedface:
		return None

	commands = []
	currentOffset = 7 * 4

	for i in xrange(header.numberOfCommands):
		command, currentOffset = ParseMachOCommand(data, currentOffset)
		commands.append(command)

	return "commands #: %s\n%s" % (header.numberOfCommands, '\n'.join([str(i) for i in commands]))


def loadMachOFatFile(filename):
	# load the fat mach-o file

	inputfile = open(filename, 'r').read()
	header = MachOFatHeader(inputfile)
	
	if header.magic != 0xcafebabe:
		return None

	for i in xrange(header.numberOfArchs):
		arch = MachOFatArchsTable(inputfile, 8 + 20 * i)

		if arch.cputype == 7: # 7 == intel 32 bit
			return loadMachOFileData(inputfile[arch.offset:arch.offset + arch.size])

	return None