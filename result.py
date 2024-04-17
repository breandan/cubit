#!/usr/bin/env python

'''this representation is used for both result and phrase.'''

import settings
from qstr import QStr

class Result(object):
	'''a phrase (only the target side), because the phrase-table is indexed by the source-side'''

	__slots__ = "score", "trans"
	## note: trans is a tuple (of ints)!

	def __init__(self, score=0, trans=QStr()):

		self.score = score		
		self.trans = trans		

	def __str__(self, precision=2):
		format = "%%.%dlf \"%%s\"" % precision
		return format % (self.score, self.trans)

	def advance(self, score, trans):
		return Result(self.score + score, self.trans + trans)

	def naked(self):
		## no </s> and no ""
		return "%.5lf\t%s" % (self.score, self.trans.naked())
