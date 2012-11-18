def loadFile(location):
    from macho import MachOFile
    from macho import MachOFatFile
    from elf import ElfFile

    ret  = None
    data = open(location, 'r').read()

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
