#from __future__ import prints_function

import sublime, sublime_plugin
from sidebar.SideBarItem import SideBarItem
from sidebar.SideBarSelection import SideBarSelection
from sidebar.SideBarProject import SideBarProject
import sys, logging
import cStringIO
import os, errno, re
import shutil
from commands import *
import pickle
import gzip
import subprocess
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

class MachOFatHeader(NamedStruct):
	endianness = '>'
	definition = (
		('magic', 'I'),
		('numberOfArchs', 'I')
	)

class MachOFatArchsTable(NamedStruct):
	endianness = '>'
	definition = (
		('cputype', 'i'),
		('cpusubtype', 'i'),
		('offset', 'I'),
		('size', 'I'),
		('alignment', 'I'),
	)

class MachOHeader(NamedStruct):
	endianness = '<'
	definition = (
		('magic', 'I'),
		('cputype', 'i'),
		('cpusubtype', 'i'),
		('filetype', 'I'),
		('numberOfCommands', 'I'),
		('sizeOfCommands', 'I'),
		('flags', 'I'),
	)

class MachOCommand(NamedStruct):
	endianness = '<'
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I')
	)

class MachOSegmentCommand(MachOCommand):
	endianness = '<'
	definition = (
		('cmd', 'I'),
		('cmdsize', 'I'),
		('segname', '16s'),
		('vmaddr', 'I'),
		('vmsize', 'I'),
		('fileoff', 'I'),
		('filesize', 'I'),
		('maxprot', 'I'),
		('initprot', 'I'),
		('nsects', 'I'),
		('flags', 'I'),
	)

def ParseMachOCommand(data, offset):
	commands = {
		1: MachOSegmentCommand,
	}

	command = MachOCommand(data, offset)
	commandClass = commands.get(command.cmd, MachOCommand)
	command = commandClass(data, offset)

	return command, offset + command.cmdsize


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


def loadMachOFatFile(filename):
	# load the fat mach-o file

	inputfile = open(filename, 'r').read()
	header = MachOFatHeader(inputfile)
	
	if header.magic != 0xcafebabe:
		return None

	for i in xrange(header.numberOfArchs):
		arch = MachOFatArchsTable(inputfile, 8 + 20 * i)

		if arch.cputype == 7: # 7 == intel 32 bit
			return loadMachOFileData(inputfile[arch.offset:arch.offset + arch.size])

	return None

class disasmaentryCommand(sublime_plugin.TextCommand):  
    def run(self, edit,location=""):  
        #self.view.insert(edit, 0, SideBarSelection([]).getSelectedItems()[0])
        #location = SideBarSelection([]).getSelectedItems()[0].path()
        #outs=getoutput("objdump -s %s"%location)

        outs = loadMachOFatFile(location) or "qualche errore"
        self.view.set_syntax_file("Packages/Disasma/Disasma.tmLanguage")
        self.view.insert(edit, 0, outs )  


class disasmaCommand(sublime_plugin.WindowCommand):
    def run(self, paths = []):
        for item in SideBarSelection(paths).getSelectedItems():
            if self.window.num_groups() == 1:
                self.window.run_command('set_layout',
                            {
                                "cols": [0.0, 0.2, 1.0],
                                "rows": [0.0, 0.2],
                                "cells": [[0, 0, 0.2, 1], [0.2, 0, 2, 1]]
                            })
                #self.window.run_command('clone_file')

            view = self.window.new_file()
            view.set_name(item.name()+".disasm")
            view.set_syntax_file("Packages/Disasma/Disasma.tmLanguage")
            view.run_command('disasmaentry',{"location":item.path()})
            self.window.run_command('move_to_group', {"group": 1})
            self.window.focus_view(view)
