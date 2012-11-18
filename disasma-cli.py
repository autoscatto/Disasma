from util.loader import loadFile
import sys

try:
	filename = sys.argv[1]
except:
	filename = 'binaries/fat-macho'

print loadFile(filename).disassa()
