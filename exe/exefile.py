# -*- coding: Latin-1 -*-
from util.namedstruct import *
import struct
# from pefile import pefile
from pymsasid import *

class ExeFormatError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

DOSZM_SIGNATURE = 0x4D5A
NE_SIGNATURE    = 0x454E
LE_SIGNATURE    = 0x454C
LX_SIGNATURE    = 0x584C
NT_SIGNATURE    = 0x00004550
OPTIONAL_HEADER_MAGIC_PE        = 0x10b
OPTIONAL_HEADER_MAGIC_PE_PLUS   = 0x20b

SIZE_OF_NT_SIGNATURE = 4
IMAGE_SECTION_HEADER_SIZE = 40
IMAGE_FILE_HEADER_SIZE = 20

class ExeHeader(NamedStruct):
    endianness = '@'
    definition = (
        ('e_magic', '2s'),          # Magic number
        ('e_cblp',   'H'),          # Bytes on last page of file
        ('e_cp',    'H'),           # Pages in file
        ('e_crlc',     'H'),        # Relocations
        ('e_cparhdr',    'H'),      # Size of header in paragraphs
        ('e_minalloc',   'H'),      # Minimum extra paragraphs needed       
        ('e_maxalloc',   'H'),      # Maximum extra paragraphs needed   
        ('e_ss',         'H'),      # Initial (relative) SS value
        ('e_sp',         'H'),      # Initial SP value
        ('e_csum',   'H'),          # Checksum
        ('e_ip',         'H'),      # Initial IP value
        ('e_cs',         'H'),      # Initial (relative) CS value
        ('e_lfarlc',   'H'),        # File address of relocation table
        ('e_ovno',   'H'),          # Overlay number
        ('e_res', '8s'),            # Reserved words
        ('e_oemid',     'H'),       # OEM identifier (for e_oeminfo)
        ('e_oeminfo',   'H'),       # OEM information; oemid specific
        ('e_res2','20s'),           # Reserved words
        ('e_lfanew',   'I')         # File address of new exe header (PE)
    )

class ExePeSign(NamedStruct):
    endianess='@'
    definition=(('Signature','I'))

class ExeFileHeader(NamedStruct):
    endianness = '@'
    definition = (
        ('Machine','H'),
        ('NumberOfSections','H'),
        ('TimeDateStamp','I'),
        ('PointerToSymbolTable','I'),
        ('NumberOfSymbols','I'),
        ('SizeOfOptionalHeader','H'),
        ('Characteristics','H')
        )


class ExeOptionalHeader(NamedStruct):
    endianness = '@'
    definition = (
        ('Magic','H'),
        ('MajorLinkerVersion','B'),
        ('MinorLinkerVersion','B'),
        ('SizeOfCode','I'),
        ('SizeOfInitializedData','I'),
        ('SizeOfUninitializedData','I'),
        ('AddressOfEntryPoint','I'),
        ('BaseOfCode','I'),
        ('BaseOfData','I'),
        ('ImageBase','I'),
        ('SectionAlignment','I'),
        ('FileAlignment','I'),
        ('MajorOperatingSystemVersion','H'),
        ('MinorOperatingSystemVersion','H'),
        ('MajorImageVersion','H'),
        ('MinorImageVersion','H'),
        ('MajorSubsystemVersion','H'),
        ('MinorSubsystemVersion','H'),
        ('Reserved1','I'),
        ('SizeOfImage','I'),
        ('SizeOfHeaders','I'),
        ('CheckSum','I'),
        ('Subsystem','H'),
        ('DllCharacteristics','H'),
        ('SizeOfStackReserve','I'),
        ('SizeOfStackCommit','I'),
        ('SizeOfHeapReserve','I'),
        ('SizeOfHeapCommit','I'),
        ('LoaderFlags','I'),
        ('NumberOfRvaAndSizes','I')
        )

class ExeOptionalHeader64(NamedStruct):
    endianness = '@'
    definition = (
        ('Magic','H'),
        ('MajorLinkerVersion','B'),
        ('MinorLinkerVersion','B'),
        ('SizeOfCode','I'),
        ('SizeOfInitializedData','I'),
        ('SizeOfUninitializedData','I'),
        ('AddressOfEntryPoint','I'),
        ('BaseOfCode','I'),
        ('ImageBase','Q'),
        ('SectionAlignment','I'),
        ('FileAlignment','I'),
        ('MajorOperatingSystemVersion','H'),
        ('MinorOperatingSystemVersion','H'),
        ('MajorImageVersion','H'),
        ('MinorImageVersion','H'),
        ('MajorSubsystemVersion','H'),
        ('MinorSubsystemVersion','H'),
        ('Reserved1','I'),
        ('SizeOfImage','I'),
        ('SizeOfHeaders','I'),
        ('CheckSum','I'),
        ('Subsystem','H'),
        ('DllCharacteristics','H'),
        ('SizeOfStackReserve','Q'),
        ('SizeOfStackCommit','Q'),
        ('SizeOfHeapReserve','Q'),
        ('SizeOfHeapCommit','Q'),
        ('LoaderFlags','I'),
        ('NumberOfRvaAndSizes','I')
        )

class ExeSectionHeader(NamedStruct):
    endianness = '@'
    definition = (
        ('Name','8s'),
        ('Misc','I'),
        ('VirtualAddress','I'),
        ('SizeOfRawData','I'),
        ('PointerToRawData','I'),
        ('PointerToRelocations','I'),
        ('PointerToLinenumbers','I'),
        ('NumberOfRelocations','H'),
        ('NumberOfLinenumbers','H'),
        ('Characteristics','I'),
        )

    def __init__(self, data, offset):
        NamedStruct.__init__(self, data, offset)
        self.data = data[self.PointerToRawData :
                         self.PointerToRawData + self.SizeOfRawData]


class ExeFile(object):

    def checkIfPE(self):
        if self.header.e_lfanew > len(self.data):
            print 'Invalid e_lfanew value, probably not a PE file'
            return False
        else:
            self.nt_headers_offset = self.header.e_lfanew
            #self.pesign=ExePeSign(self.data[self.nt_headers_offset:self.nt_headers_offset+8])
            mstruct = struct.Struct("@I")
            self.pesign=mstruct.unpack_from(self.data[self.nt_headers_offset:self.nt_headers_offset+8])[0]
            if not self.pesign:
                print 'NT Headers not found.'
                return False
            if (0xFFFF & self.pesign) == NE_SIGNATURE:
                print 'Invalid NT Headers signature. Probably a NE file'
                return False
            if (0xFFFF & self.pesign) == LE_SIGNATURE:
                print 'Invalid NT Headers signature. Probably a LE file'
                return False
            if (0xFFFF & self.pesign) == LX_SIGNATURE:
                print 'Invalid NT Headers signature. Probably a LX file'
                return False
            if self.pesign != NT_SIGNATURE:
                print 'Invalid NT Headers signature.'
                return False


    def __init__(self, data):
        self.data      = data
        #self.pe       = pefile.PE(data=data)
        self.oldheader = ExeHeader(data)
        self.commands  = []
        
        # Controllo se e' PE
        # self.ispe = self.checkIfPE()

        # File Header
        self.newheader = ExeFileHeader(self.data,
                            self.oldheader.e_lfanew + SIZE_OF_NT_SIGNATURE)
        # Need to take the size of a ExeFileHeader, which is 20
        self.optheader = ExeOptionalHeader(self.data, self.oldheader.e_lfanew \
                            + SIZE_OF_NT_SIGNATURE + IMAGE_FILE_HEADER_SIZE)
        print self.oldheader
        print self.newheader
        print self.optheader

        '''
        entryPoint  = self.optheader.AddressOfEntryPoint
        relCodeBase = self.optheader.BaseOfCode
        codeSize    = self.optheader.SizeOfCode
        self.code   = data[entryPoint+relCodeBase+IMAGE_SECTION_HEADER_SIZE:
                           entryPoint+relCodeBase+codeSize]
        '''

        self.sections = {}
        # offset = self.optheader.AddressOfEntryPoint
        offset = self.oldheader.e_lfanew + SIZE_OF_NT_SIGNATURE \
                 + IMAGE_FILE_HEADER_SIZE + self.newheader.SizeOfOptionalHeader
        print offset
        for i in range(0, self.newheader.NumberOfSections):
            section = ExeSectionHeader(self.data, offset)
            offset += section.sizeOfStruct()
            # offset += section.SizeOfRawData
            self.sections[section.Name] = section
            print section

        '''
        if not self.fileheader:
            raise ExeFormatError('File Header missing')


        self.optional_header_offset =  self.nt_headers_offset+4+self.fileheader.sizeOfStruct()
        self.sections_offset = self.optional_header_offset + self.fileheader.SizeOfOptionalHeader
        self.optional_header=ExeOptionalHeader(self.data[self.optional_header_offset:self.optional_header_offset+256])

        MINIMUM_VALID_OPTIONAL_HEADER_RAW_SIZE = 69

        if ( self.optional_header is None and
            len(self.data[self.optional_header_offset:self.optional_header_offset+0x200])>= MINIMUM_VALID_OPTIONAL_HEADER_RAW_SIZE ):
            padding_length = 128
            padded_data = self.data[self.optional_header_offset:self.optional_header_offset+0x200] + ('\0' * padding_length)
            self.optional_header = ExeOptionalHeader(padded_data)

        if self.optional_header is not None:
            if self.optional_header.Magic == OPTIONAL_HEADER_MAGIC_PE:
                self.petype = OPTIONAL_HEADER_MAGIC_PE
            elif self.optional_header.Magic == OPTIONAL_HEADER_MAGIC_PE_PLUS:
                self.petype = OPTIONAL_HEADER_MAGIC_PE_PLUS
                self.optional_header = ExeOptionalHeader64(self.data[self.optional_header_offset:self.optional_header_offset+0x200])

                MINIMUM_VALID_OPTIONAL_HEADER_RAW_SIZE = 69+4

                if ( self.optional_header is None and
                    len(self.data[self.optional_header_offset:self.optional_header_offset+0x200])
                    >= MINIMUM_VALID_OPTIONAL_HEADER_RAW_SIZE ):

                    padding_length = 128
                    padded_data = self.data[self.optional_header_offset:self.optional_header_offset+0x200] + ('\0' * padding_length)
                    self.optional_header = ExeOptionalHeader64(padded_data)

        if self.petype is None or self.optional_header is None:
            print "No Optional Header found, invalid PE32 or PE32+ file"
            self.ispe=False


        sezioni=self.pe.sections
        self.sections = {}
        self.vmem = {}
        for s in sezioni:
            self.sections[s.Name.replace('\x00','')] = s
            # Saving only mapped segments
            if s.VirtualAddress != 0:
                self.vmem[s.VirtualAddress] = s
        '''


    def disassa(self):
        out = []
        #prog = pymsasid.Pymsasid(hook=pymsasid.BufferHook,source = self.data,mode= 32)
        prog = pymsasid.Pymsasid(hook   = pymsasid.BufferHook,
                                 source = self.data,
                                 mode   = 32)

        textSect = self.sections['.text']
        sectionTitle = 'Disassembly of section %s' % (textSect.Name.replace('\x00',''))
        out.append(sectionTitle)
        out.append('-' * len(sectionTitle))
        out.append('')

        currentOffset = textSect.PointerToRawData
        prog.input.base_address = textSect.VirtualAddress

        while currentOffset < textSect.PointerToRawData + textSect.SizeOfRawData:
            instruction = prog.disassemble(currentOffset)
            out.append('[%08x] %s'% (currentOffset+textSect.VirtualAddress, str(instruction)))
            currentOffset += instruction.size
        out.append('\n\n')

        '''
        currentOffset = textSect.get_file_offset()
        prog.input.base_address = textSect.VirtualAddress

        while currentOffset < textSect.get_file_offset() + textSect.SizeOfRawData:
            instruction = prog.disassemble(currentOffset)
            out.append('[%08x] %s'% (currentOffset+textSect.VirtualAddress, str(instruction)))
            currentOffset += instruction.size
        out.append('\n\n')
        '''
        return '\n'.join(out)

    @staticmethod
    def canLoad(data):
        magic = struct.unpack_from('@2s', data)[0]
        if magic == DOSZM_SIGNATURE:
            print 'Probably a ZM Executable (not a PE file).'
        return magic == 'MZ'

def loadExeFile(filename):
    inputfile = open(filename, 'r').read()
    header =ExeHeader(inputfile)

    ExeFile(inputfile)
