def loadFile(location):
    from macho import MachOFile
    from macho import MachOFatFile
    from elf import ElfFile

    ret  = None
    data = open(location, 'rb').read()

    filetypes = [
        MachOFile,
        MachOFatFile,
        ElfFile
    ]

    for filetype in filetypes:
        if filetype.canLoad(data):
            ret = filetype(data)
            break

    if ret == None:
        print " == NO LOADERS FOUND =="

    return ret

def SPUTA_FUORI_IL_ROSPO(filename):
    from process.process import *
    process = Process()
    theFile = loadFile(filename)
    for section in theFile.sections:
        process.addSection(section)

    print process