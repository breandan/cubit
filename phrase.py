#!/usr/bin/env python

import settings
import result

class Phrase(result.Result):
	'''besides trans being a tuple of srilm indices, add lmstr as the q-str'''

	__slots__ = "lmstr", "pre"
	
	def __init__(self, score=0, trans=()):
		result.Result.__init__(self, score, trans)
		self.pre = 0
		## N.B.: even for non-lm integrated search, it's better off to put in lm scores within phrases
		if True: #not settings.opts.tmonly:
			p, self.lmstr = settings.lm.pq(self.trans)
			self.pre = settings.lm.pre(self.trans)
			## </s> does not count toward length
			l = len(trans) if trans != settings.lm.stopsyms() else 0
			self.score = self.score  + (p ) * settings.model.lm + l * settings.model.lenp
		else:
			self.lmstr = settings.lm.words2indices(self.trans)

	def __str__(self):
		return result.Result.__str__(self) + " (%s)" % str(self.lmstr) 

	def __cmp__(self, other):
		return self._score() - other._score()

	def _score(self):
		return self.score + self.pre * settings.model.lm
