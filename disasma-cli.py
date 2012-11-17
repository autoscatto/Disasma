from macho import *

print machofile.loadMachOFatFile('binaries/fat-macho') or "qualche errore"
