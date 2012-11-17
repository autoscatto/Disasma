import functools
import io
import mmap
import operator
import os
import struct
#from macho import *
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

'''
info powa: http://www.acsu.buffalo.edu/~charngda/elf.html

'''


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['r'] = reverse
    return type('Enum', (), enums)

_pacco= struct.Struct(b'=4s')

class _elf(object):
        arch=enum(err=0, x86=1, x64=2, free=3)
        endi=enum(err=0, LSB=1, MSB=2, free=3)
        #versione, ident nell'header
        vers=enum(INVALID=0, CURRENT=1, free=2)
        osabi=enum(NONE=0,          #No extensions or unspecified
                   SYSV=1,          #No extensions or unspecified
                   HPUX=1,          #Hewlett-Packard HP-UX
                   NETBSD=2,        #NetBSD
                   LINUX=3,         #Linux
                   SOLARIS=6,       #Sun Solaris
                   AIX=7,           #AIX
                   IRIX=8,           #IRIX
                   FREEBSD=9,       #FreeBSD
                   TRU64=10,        #Compaq TRU64 UNIX
                   MODESTO=11,      #Novell Modesto
                   OPENBSD=12,      #Open BSD
                   OPENVMS=13,      #Open VMS
                   NSK=14,          #Hewlett-Packard Non-Stop Kernel
                   AROS=15,         #Amiga Research OS
                   FENIXOS=16,      #The FenixOS highly scalable multi-core OS
                   ARM_EABI=64,     #ARM EABI
                   ARM=97,          #ARM
                   STANDALONE=255   #Standalone (embedded) application
                   )



class exeStruct(object):
    def __init__(self,fileobj):
        #mi prendo i primi 4 byte nell'ordine in cui compaiono
        magic_n=struct.Struct(b'=4s')
        self.filedata=fileobj.read()
        self.mapf=mmap.mmap(fileobj.fileno(), 0, mmap.MAP_SHARED, mmap.PROT_READ)
        self.magic_n=magic_n.unpack_from(self.mapf,0)[0]
        self.offset=0
        self.elf=False
        self.macho=False
        print self.magic_n
        try:
            {   '\x7fELF': self.elfBuild, #e' un ELF (va fatto per THUTTHI gli altri)
                '\xca\xfe\xba\xbe': self.machoBuild

            }[self.magic_n]()
        except KeyError:
            pass



#-------------------------------------[ELF]---------------------------------------------------------------
    def elfBuild(self):
            self.elf=True
            self.elfpack=struct.Struct(b'=4sBBBBBxxxxxxx') #la uso per spacchettare il resto utile dell'header
            self.unpacked=self.elfpack.unpack_from(self.mapf,self.offset)
            self.arch=_elf.arch.r[self.unpacked[1]]
            self.endi=_elf.endi.r[self.unpacked[2]]
            self.vers=_elf.vers.r[self.unpacked[3]]
            self.osabi=_elf.osabi.r[self.unpacked[4]]
            self.versabi=self.unpacked[5] #versione dell'abi
#----------------------------------------------------------------------------------------------------


#-------------------------------------[MACHO]---------------------------------------------------------------
    def machoBuild(self):
            self.macho=True
            self.header = MachOFatHeader(self.filedata)
            if self.header.magic != 0xcafebabe:
                raise Exception('Matcho', 'inizia con caffe ma manca babe. DRAMA!')

            for i in xrange(self.header.numberOfArchs):
                self.arch = MachOFatArchsTable(self.filedata, 8 + 20 * i)

                if self.arch.cputype == 7: # 7 == intel 32 bit
                    self.cputype=loadMachOFileData(self.filedata[self.arch.offset:self.arch.offset + self.arch.size])
#----------------------------------------------------------------------------------------------------

    def isElf(self):
        return self.elf

    def isMacho(self):
        return self.macho

    def getArch(self):
        return self.arch

    def getEndianess(self):
        return self.endi

    def printElf(self):
        if self.isElf:
            print "Architettura: %s\nEndianess:    %s\nVersione:     %s\nABI Os:       %s\nVersione ABI: %s\n"%(self.arch,self.endi,self.vers,self.osabi,self.versabi)

    def printMacho(self):
            print "Matcho %s"%self.cputype
    __hash__ = None

    def __eq__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        return not self.__eq__(other)


