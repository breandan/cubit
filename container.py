#!/usr/bin/env python

import sys
from log import logging

class Container(object):
	'''actually an "interface" which has a histogram beam feature. shared by Bin and phrase_table'''

	def __init__(self, beam=None):
		self.hist_beam = beam
		self.table = []
		self.pruned = 0
		self.best = None
		self.sorted = False
		
	def prune(self):
		if self.hist_beam is not None:
			size = len(self.table)
			if size > self.hist_beam:
				self.sort()
				del self.table[self.hist_beam:]
				self.pruned += size - self.hist_beam

	def append(self, x):
		'''to be polished by subclasses'''
		if self.table and x < self.table[-1]:
			self.sorted = False   ### :)
		self.table.append(x)
		if self.best is None or x < self.best:
			self.best = x			

	def sort(self):
		if not self.sorted:
			##self.table.sort()

			a = [(x.score, x) for x in self.table]
			a.sort()
			self.table = [y[1] for y in a]			
			self.sorted = True

	def items(self):
		## N.B.: although identity mapping by def., sometimes nasty things will happen (replacement)
		## so values() instead of keys()
		self.sort()
		return self.table

	def __len__(self):
		return len(self.table)
