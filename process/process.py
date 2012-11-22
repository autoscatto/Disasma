from util.intervalmap import intervalmap
from pymsasid import *

class Section(object):
	def __init__(self,
		         name  = '',
		         start = 0,
		         size  = 0,
		         data  = None):
		self.name  = name
		self.start = start
		self.size  = size
		self.data  = data

	@property
	def end(self):
		return self.start + self.size

	def __str__(self):
		def printablechar(x):
			return x if x > 31 and x < 127 else ord('.')

		title = 'Section ' + self.name + ':'
		#out = [title, '-' * len(title), '']
		out = [title]
		line = []
		asciistring = []
		for i, char in enumerate(self.data):
			line.append('%02x ' % ord(char))
			asciistring.append(chr(printablechar(ord(char))))

			if (i + 1) % 4 == 0:
				line.append('  ')

			if (i + 1) % 16 == 0:
				linestring = ''.join(line)
				offsetstring = ' %08x  |  ' % ((i-15) + self.start)
				ascii = ''.join(asciistring)
				out.append(offsetstring + linestring + '  |  ' + ascii)
				line = []
				asciistring = []

		i += 1
		while i % 16 != 0:
			line.append('   ')
			asciistring.append(' ')

			if (i + 1) % 4 == 0:
				line.append('  ')

			if (i + 1) % 16 == 0:
				linestring = ''.join(line)
				offsetstring = ' %08x  |  ' % ((i-15) + self.start)
				ascii = ''.join(asciistring)
				out.append(offsetstring + linestring + '  |  ' + ascii)
				line = []
				asciistring = []
			i += 1
			
		return '\n'.join(out) + '\n\n'

	def getHTML(self):
		return ''

class CodeSection(Section):
	def __str__(self):
		title = 'Section ' + self.name + ':'
		#out = [title, '-' * len(title), '']
		out = [title]
		prog = pymsasid.Pymsasid(hook   = pymsasid.BufferHook,
		                         source = self.data,
		                         mode   = 32)
		
		prog.input.hook.base_address = self.start
		currentOffset = self.start

		instructions = []
		xrefs = {}

		while currentOffset < self.start + self.size:
			instruction = prog.disassemble(currentOffset)
			currentOffset += instruction.size
			instructions.append(instruction)

			for br in instruction.branch():
				if br != instruction.pc:
					try:
						xr = xrefs.get(br, [])
						xr.append(instruction.pc - instruction.size)
						xrefs[br] = xr
					except:
						continue
		
		for instruction in instructions:
			addr = instruction.pc - instruction.size
			name = self.process.symbols.get(addr, None)
			if name:
				out.append(' [%08x]\n [%08x] %s:' % (addr, addr, name))

			xr = xrefs.get(addr, None)
			if xr:
				if not name:
					out.append(' [%08x]' % addr)

				xrefstring = ', '.join(('%08x' % i for i in xr))
				out.append(' [%08x] X-Refs from: %s' % (addr, xrefstring))

			def operand_to_str(operand):
				address = None

				if operand.type == 'OP_JIMM':
					address = operand.lval + operand.pc # - instruction.size?

				if operand.type == 'OP_MEM' and operand.base is None:
					address = operand.lval + operand.pc # - instruction.size?

				if address:
					symbol = self.process.symbols.get(address, None)
					if symbol:
						return symbol

				return repr(operand)


			out.append(' [%08x] %-8s\t%s' % (addr, str(instruction.operator), ', '.join(map(operand_to_str, instruction.operand))))
			#out.append(' [%08x] %-8s\t%s' % (addr, str(instruction.operator), ' - '.join([str (i) for i in instruction.operand])))

		return '\n'.join(out) + '\n\n'

	def getHTML(self):
		# import re
		preinizzio = '<!DOCTYPE HTML>\n'
		inizzio = '<html><head>' + \
		          '<link rel="stylesheet" type="text/css" href="style.css"/>\n' + \
		          '</head><body>'
		title = '<pre class="section">== Section %s : ==</pre><br/>\n' % self.name
		out = [preinizzio, inizzio, title]
		prog = pymsasid.Pymsasid(hook   = pymsasid.BufferHook,
		                         source = self.data,
		                         mode   = 32)
		
		prog.input.hook.base_address = self.start
		currentOffset = self.start

		instructions = []
		xrefs = {}

		while currentOffset < self.start + self.size:
			instruction = prog.disassemble(currentOffset)
			currentOffset += instruction.size
			instructions.append(instruction)

			for br in instruction.branch():
				if br != instruction.pc:
					try:
						xr = xrefs.get(br, [])
						xr.append(instruction.pc - instruction.size)
						xrefs[br] = xr
					except:
						continue

		#print xrefs and names
		for instruction in instructions:
			sz = instruction.size
			addr = instruction.pc - instruction.size
			name = self.process.symbols.get(addr, None)

			htmlAddr = '<pre> [</pre><pre class="address">%08x</pre><pre>] </pre>' % (addr)

			if name:
				out.append('%s<br/>%s<pre id="ref_%s" type="refname">%s</pre><br/>' % \
					(htmlAddr, htmlAddr, name, name))

			xr = xrefs.get(instruction.pc, None)
			if xr:
				xrefstring = ', '.join(('<a href="#%08x"><pre class="xref">%08x</pre></a>' % (i, i) for i in xr))
				out.append('%s<pre class="xref">X-Refs from: %s</pre><br/>\n' % \
					(htmlAddr, xrefstring))
			
			out.append('<pre class="inline"> [</pre>' + \
				'<pre class="address" id="%08x">%08x</pre>' % \
				(addr, addr) + \
				'<pre>] </pre>')
			out.append('<pre class="operator">%-8s\t</pre>' % str(instruction.operator))

			for i in range(0, len(instruction.operand)):
				op = instruction.operand[i]
				
				if op.type == 'OP_REG':
					out.append('<pre class="operand_register">%s</pre>' % op.base)
				elif op.type == 'OP_MEM':
					name = self.process.symbols.get(op.lval + op.pc - sz, None)
					if name:
						out.append('<a href="#ref_%s"><pre class="operand_reference">%s</pre></a>' \
							% (name, name))
					else:
						out.append('<pre>[</pre>' + \
							'<a href="#%08x"><pre class="operand_address">%s0x%x</pre></a>' \
							% (op.lval + op.pc - sz, '-' * (op.lval < 0), abs(op.lval))
							+ '<pre>]</pre>')
				elif op.type == 'OP_JIMM':
					name = self.process.symbols.get(op.lval + op.pc - sz, None)
					if name:
						out.append('<a href="#ref_%s"><pre class="operand_reference">%s</pre></a>' \
							% (name, name))
					else:
						out.append('<a href="#%08x"><pre class="operand_address">%s0x%x</pre></a>' \
							% (op.lval + op.pc, '-' * (op.lval < 0), abs(op.lval)))
				elif op.type == 'OP_IMM':
					out.append('<pre class="operand_immediate">%s0x%x</pre>' \
						% ('-' * (op.lval < 0), op.lval))
				else:
					out.append('<pre class="operand">QUALCOSA di tipo %s</pre>' % op.type)

				if i < len(instruction.operand) - 1:
					out.append('<pre>, </pre>')
			out.append('<br/>\n')

		out.append('</body>\n')
		out.append('</html>')

		return ''.join(out)

class Process(object):
	def __init__(self):
		self.sections = intervalmap()

	def addSection(self, section):
		self.sections[section.start : section.end] = section
		section.process = self

	def __getitem__(self, key):
		section = self.sections[key]
		return section.data[key - section.start]

	def __str__(self):
		return '\n'.join(str(section) for interval, section in self.sections.items())

	def getHTML(self):
		return '\n'.join(section.getHTML() for interval, section in self.sections.items())
