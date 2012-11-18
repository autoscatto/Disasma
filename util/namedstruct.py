import struct

class NamedStruct(object):
	struct     = None
	endianness = ''
	definition = ()

	def __init__(self, data, offset = 0):
		if self.struct is None:
			format = self.endianness + ''.join([formattype for name, formattype in self.definition])
			self.struct = struct.Struct(format)

		self.contents = self.struct.unpack_from(data, offset)

		for i, (name, typestring) in enumerate(self.definition):
			if 's' in typestring:
				self.contents = list(self.contents)
				self.contents[i] = self.contents[i].split('\0', 1)[0]


	def __getattr__(self, name):
		for i, (membername, formattype) in enumerate(self.definition):
			if name == membername:
				return self.contents[i]

	def __str__(self):
		contents = ['%s: %s' % (name, self.contents[i]) for i, (name, x) in enumerate(self.definition)]
		return '%s - %s' % (self.__class__.__name__, ', '.join(contents))

	def sizeOfStruct(self):
		return self.struct.size
