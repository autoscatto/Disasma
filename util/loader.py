def loadFile(location):
    from macho import MachOFile
    from macho import MachOFatFile
    from elf import ElfFile
    from exe import ExeFile

    ret  = None
    data = open(location, 'rb').read()

    filetypes = [
        MachOFile,
        MachOFatFile,
        ElfFile,
        ExeFile
    ]

    for filetype in filetypes:
        if filetype.canLoad(data):
            ret = filetype(data)
            break

    if ret == None:
        print " == NO LOADERS FOUND =="

    return ret
