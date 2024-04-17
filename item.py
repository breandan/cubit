#!/usr/bin/env python

import sys
import math

logs = sys.stderr

import settings 

import result
import cover
	
class Item(object):
	'''an item in deduction, or a vertex in the graph.
	to be augmented with LM words to LM_Item'''

	def __init__(self, cov=None, backp=None, res=result.Result()):
		''' default params are for the initial item.
		last is the last ending position +1.'''
		if cov is None:
			cov = cover.default()  ## mono or not
		self.cover = cov
			
		self.backp = backp
		self.res = res
		self.len = len(self.cover)   # number of source words covered (binning according to this)

		## signature: don't include res!
		self.hashval = hash(self.cover)

		## n.B. will not change
		self._score = self.res.score + self.cover.futurecost  # if not settings.opts.nofuture else 0)

	def trans(self):
		return str(self.res.trans.naked())
	
	def __hash__(self):
		return self.hashval
				
	def __str__(self):
		return "(%d, %s): %s" % (self.len, self.cover, self.res)
	
	def __lt__(self, other):
		return self.score() < other.score()

	def __eq__(self, other):
		'''comparing signature, for recombo'''
		return self.cover.__eq__(other.cover)

	def __sub__(self, other):
		return self.score() - other.score()

	__cmp__ = __sub__

	def score(self):
 		## to include future cost
 		return self._score

	@staticmethod
	def additional_score(dist, phrase):
		## N.B.: phrase.score already included lm and lenp
		return phrase.score + dist * settings.model.distort # + \
##			   phrase.pre * settings.model.lm    ## outside estimate for tmonly!!! should be deleted in 2nd pass

	
	def advance(self, (i, j), dist, phrase):
		''' return the new item after applying the phrase'''

		add_score = self.additional_score(dist, phrase)
		
		newitem = Item(self.cover.advance((i, j)), self, \
						 self.res.advance(add_score, phrase.trans))

		newitem.step = (add_score, phrase.trans, (i, j))
		newitem.precost = phrase.pre * settings.model.lm
		return newitem

	def ranges(self):
		return self.cover.ranges()
	
	def backtrace(self):
		''' return a str '''
		if self.backp is None:
			return ""
		return self.backp.backtrace() \
			   + " %s |%5lf|%d|%d|" % (self.step[1], \
									  self.step[0], self.step[2][0], self.step[2][1]) 
