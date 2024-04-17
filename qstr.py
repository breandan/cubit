#!/usr/bin/env python

from idmap import IdMap

class QStr(tuple):
	''' a wrapper for lm str; easier for printing '''

	lm = IdMap()

	@staticmethod
 	def fromwords(s):
 		if type(s) is str:
 			s = s.split()
		return QStr(QStr.lm.words2indices(s))
					   
	def __str__(self):
		return self.lm.ppqstr(self)

	def naked(self):
		''' no </s>'''
		return self.lm.ppqstr(self[:-1])

	def __add__(self, other):
		# caution
		return QStr(tuple(self) + other)

	def __eq__(self, other):
		return tuple.__eq__(self, other)

	def __hash__(self):
		return tuple.__hash__(self)
