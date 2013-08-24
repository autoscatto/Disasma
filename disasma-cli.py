from util.loader import *
import sys

try:
	filename = sys.argv[1]
except:
	filename = 'binaries/elf'

print SPUTA_FUORI_IL_ROSPO(filename)