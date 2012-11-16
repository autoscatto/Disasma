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

class disasmaentryCommand(sublime_plugin.TextCommand):  
    def run(self, edit,location=""):  
        #self.view.insert(edit, 0, SideBarSelection([]).getSelectedItems()[0])
        #location = SideBarSelection([]).getSelectedItems()[0].path()
        outs=getoutput("objdump -s %s"%location)
        self.view.set_syntax_file("Packages/Disasma/Hex.tmLanguage")
        self.view.insert(edit, 0, outs)  


class disasmaCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			if self.window.num_groups() == 1:
				self.window.run_command('set_layout',
                            {
                                "cols": [0.0, 0.5, 1.0],
                                "rows": [0.0, 1.0],
                                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
                            })
				self.window.run_command('clone_file')
				self.window.run_command('move_to_group', {"group": 1})



			view = self.window.new_file()
			view.set_name(item.name()+".disasm")
			view.run_command('disasmaentry',{"location":item.path()})
			self.window.focus_view(view)

		
		 