#!/usr/bin/env python

import sys, os

sys.path.append(os.environ["NEWCODE"])
from myutils import getfile
from vector import Vector

import result
import phrase
import settings
import qstr
from container import Container

from log import logging

class Lattice(list):
	'''phrase-lattice, 2D table. (not to be confused with search chart)'''

	ptable = None
	max_len = None
	lm = None
	this = None    # current lattice
	
	def __getslice__(self, i, j):
		## self[i:j]
		return self.table[i][j]

	def __getitem__(self, (i, j)):
		## self[(i,j)]
		return self.table[i][j]
	
	def __init__(self, source):

		Lattice.this = self

		self.__class__.max_len = self.ptable.max_len
		self.source = source
		self.n = len(source)
		self.table = [[Container() for i in range(self.n + 2)] for j in range(self.n + 2)]   # 2D empty table

		for i in xrange(self.n):
			for j in xrange(i + 1, min(i + self.ptable.max_len, self.n + 1)):
				sub = tuple(source [i : j])
				if sub in self.ptable[j - i]:
					logging(6, 0, lambda x:(i, j, " ".join(sub)))
					self.table[i][j] = self.ptable[j - i][sub]
				elif j == i+1:
					## uncovered single word
					logging(6, 0, lambda x:("uncovered word", source[i:j]))
					self.table[i][j].append(phrase.Phrase(settings.opts.unk_cost, qstr.QStr.fromwords(source[i:j])))		
		stopsyms = settings.lm.stopsyms()
		self.table[self.n][self.n+1].append(phrase.Phrase(0, stopsyms))

		self.shortest()   # zeroth-pass


	def shortest(self):
		self.cost = {}   # 2D table
		for l in range(self.n):
			for i in range(self.n - l):
				j = i + l + 1
				best = self.table[i][j].best
				best = best._score() if best else 1e100 ## +inf
				for k in range(i + 1, j):   ## i+1 till j-1
					best = min(best, self.cost[(i, k)] + self.cost[(k, j)])
				self.cost[(i, j)]= best
		self.cost[(self.n, self.n+1)] = 0 ## </s>
		
	def pp(self):
		for i in xrange(self.n):
			for j in xrange(i+1, self.n + 1):
				logging(4, 0, lambda x:("%d-%d: %s" % (i, j, " ".join(self.source[i : j]))))
				logging(4, 2, lambda x:("best cost", self.cost[(i, j)]))
				if self[i:j]:
					logging(4, 2, lambda x:("%d translations" % len(self[i:j])))
					for phrase in self[i:j].items():
						logging(4, 4, lambda x:(str(phrase)))
				else:
					logging(4, 0, lambda x:(""))

