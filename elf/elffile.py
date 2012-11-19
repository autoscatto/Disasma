from util.namedstruct import *
from pymsasid import *
from process.process import *

class ElfHeader(NamedStruct):
    endianness = '<'
    definition = (
        ('e_ident', '16s'),     # The magic
        ('e_type', 'H'),
        ('e_machine', 'H'),
        ('e_version', 'I'),
        ('e_entry', 'I'),       # Address
        ('e_phoff', 'I'),       # Offset
        ('e_shoff', 'I'),       # Offset    
        ('e_flags', 'I'),
        ('e_ehsize', 'H'),
        ('e_phentsize', 'H'),
        ('e_phnum', 'H'),
        ('e_shentsize', 'H'),
        ('e_shnum', 'H'),
        ('e_shstrndx', 'H')
    )
    '''
    e_machine values

    enum {
      EM_NONE = 0,      // No machine
      EM_M32 = 1,       // AT&T WE 32100
      EM_SPARC = 2,     // SPARC
      EM_386 = 3,       // Intel 386
      EM_68K = 4,       // Motorola 68000
      EM_88K = 5,       // Motorola 88000
      EM_486 = 6,       // Intel 486 (deprecated)
      EM_860 = 7,       // Intel 80860
      EM_MIPS = 8,      // MIPS R3000
      EM_PPC = 20,      // PowerPC
      EM_PPC64 = 21,    // PowerPC64
      EM_ARM = 40,      // ARM
      EM_ALPHA = 41,    // DEC Alpha
      EM_SPARCV9 = 43,  // SPARC V9
      EM_X86_64 = 62,   // AMD64
      EM_MBLAZE = 47787 // Xilinx MicroBlaze
    }
    '''


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

class ElfSection(NamedStruct):
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

    def __init__(self, data, offset):
        NamedStruct.__init__(self, data, offset)
        self.data = data[self.sh_offset:self.sh_offset+self.sh_size]
        self.string_section = None

    def getName(self):
        if self.string_section != None:
            return self.string_section.getName(self.sh_name)

    def __str__(self):  
        ret = NamedStruct.__str__(self)
        ret += "\nMy name is also "
        ret += self.string_section.getName(self.sh_name)
        return ret

class ElfSHStringSection(ElfSection):
    def getName(self, sh_name):
        return self.data[sh_name:self.data.find('\0', sh_name)]

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
        #print len(data)
        self.data     = data
        self.header   = ElfHeader(data)
        self.commands = []

        '''
        TODO: program_header entries
        phoff       = self.header.e_phoff
        phentsize   = self.header.e_phentsize
        phnum       = self.header.e_phnum

        for i in xrange(phnum):
            phentry = ElfProgramHeader(self.data[phoff+i*phentsize:])
        '''

        shoff       = self.header.e_shoff
        shentsize   = self.header.e_shentsize
        shnum       = self.header.e_shnum

        shstrndx    = self.header.e_shstrndx
        strtable    = ElfSHStringSection(
            self.data,
            shoff+(shstrndx)*shentsize
        )

        self.elfSections = {}
        self.sections = []
        self.vmem = {}
        for i in xrange(shnum):
            shentry = ElfSection(self.data, shoff+i*shentsize)
            shentry.string_section = strtable
            self.elfSections[shentry.getName()] = shentry
            # Saving only mapped segments
            if shentry.sh_addr != 0:
                self.vmem[shentry.sh_addr] = shentry

            secdata = self.data[shentry.sh_offset:shentry.sh_offset+shentry.sh_size]
            sectionClass = CodeSection if shentry.getName() == '.text' else Section
            self.sections.append(sectionClass(shentry.getName(),
                                              shentry.sh_addr,
                                              shentry.sh_size,
                                              secdata))

        #for key in sorted(self.vmem.iterkeys()):
        #    print '0x%08x' % (key), ': ', self.vmem[key].getName(), \
        #          ' size: ', self.vmem[key].sh_size

    def accessVMAddress(self, address, bytes=4):
        for vmaddress in self.vmem.iterkeys():
            if address >= vmaddress \
               and address <= vmaddress+self.vmem[vmaddress].sh_size:
               print "Section: ", self.vmem[vmaddress].getName()
               return self.vmem[vmaddress] \
                          .data[address-vmaddress:address-vmaddress+bytes]

    def disassa(self):
        out = []
        prog = pymsasid.Pymsasid(hook   = pymsasid.BufferHook,
                                 source = self.data,
                                 mode   = 32)

        # x86
        if self.header.e_machine == 3:
            textSect = self.elfSections['.text']
            sectionTitle = 'Disassembly of section %s' % (textSect.getName())
            out.append(sectionTitle)
            out.append('-' * len(sectionTitle))
            out.append('')

            currentOffset = textSect.sh_offset
            prog.input.base_address = textSect.sh_addr

            while currentOffset < textSect.sh_offset + textSect.sh_size:
                instruction = prog.disassemble(currentOffset)
                out.append('[%08x] %s' \
                    % (currentOffset+textSect.sh_addr, str(instruction)))
                currentOffset += instruction.size
            out.append('\n\n')

        return '\n'.join(out)

    @staticmethod
    def canLoad(data):
        magic = struct.unpack_from('>4s', data)[0]
        return magic == '\x7fELF'

def loadElfFile(filename):
    inputfile = open(filename, 'r').read()
    header = ElfHeader(inputfile)

    ElfFile(inputfile)