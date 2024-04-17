#!/usr/bin/env python

import sys
import math

logs = sys.stderr

import settings
from item import *
from result import Result
import cover

class LMItem(Item):
	'''item augmented with lm string (a tuple)'''

	lm = None
	def __init__(self, cov=None, backp=None, result=Result(), lmstr=None):
		Item.__init__(self, cov, backp, result)
		if lmstr is None:
			lmstr = settings.lm.startsyms()
		self.lmstr = lmstr
		self.hashval = hash((self.hashval, tuple(lmstr)))   # cache: tested
		
	def __eq__(self, other):
		'''signature now includes lmstr'''
		return Item.__eq__(self, other) and self.lmstr.__eq__(other.lmstr)

	def __str__(self):
		return "(%d, %s, %s): %s" % (self.len, self.cover, self.lmstr, self.res)

	def advance(self, (i, j), dist, phrase):
		''' return the new item after applying the phrase'''

		p, q = settings.lm.pq(self.lmstr + phrase.lmstr)
		lmcost = p * settings.model.lm		
		add_score = self.additional_score(dist, phrase) + lmcost

		newitem = LMItem(self.cover.advance((i, j)), self, \
						   self.res.advance(add_score, phrase.trans), \
						   q)
		newitem.step = (add_score, phrase.trans, (i, j))
		newitem.lmcost = lmcost
		newitem.precost = phrase.pre * settings.model.lm

		return newitem

