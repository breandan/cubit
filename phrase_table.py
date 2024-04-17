#!/usr/bin/env python

## pharaoh phrase-table is in probabilities!!!

import sys, os, math

sys.path.append(os.environ["NEWCODE"])
from myutils import getfile
from vector import Vector

from phrase import Phrase
from qstr import QStr

logs = sys.stderr

#TM_weights = [None, (1.0, ), None, None, None, (0.0, 0.0, 0.9, 0.5, 0)]

from container import Container
import settings

class Phrase_Table(list):

	'''self.table is first indexed by source phrase length, then by source phrase, and then map to a Phrase.
	phrase.trans is represented as a QStr (srilm indices)'''

	def __init__(self, filename, max_len=7):

		self.table = [{} for i in range(max_len + 1)]
		self.max_len = max_len
		self.read(filename)		

	def __getitem__(self, i):
		return self.table[i]			

	def read(self, filename):

		from settings import model

		## N.B.: assuming grouped (not necessarily sorted) by source!
		print >> logs, "reading phrase table from %s ..." % filename
		ptfile = getfile(filename)
		fall_thres = pruned = 0

		last = ()
		for i, line in enumerate(ptfile):
			source, target, weights = line.split("|||")
			source = tuple(source.split())
			if source != last:
				if last != ():
					self.table[ll][last].prune()
					pruned += self.table[ll][last].pruned
					
				ll = len(source)
				self.table[ll][source] = Container(settings.opts.ttable_limit)				

			if ll <= self.max_len:
				weights = weights.split()
				score = Vector(map(lambda x : -math.log(float(x)), weights)) * model.tm
				if score > settings.opts.ttable_thres:
					fall_thres += 1
					continue
				
				target = QStr.fromwords(target)
				phr = Phrase(score, target)
				self.table[ll][source].append(phr)

			last = source

		self.table[ll][last].prune()
		pruned += self.table[ll][last].pruned

		print >> logs, "phrase-table: %d read, %d stored (pass thres+hist)." % \
			  (i+1, i+1 - fall_thres - pruned)

##		self.pp()

	def pp(self):
		for i in range(self.max_len + 1):
			print >> logs, "len %d" % i
			for src in self[i]:
				print >> logs, "  %s -> %d translations" % (" ".join(src), len(self[i][src]))
				for phrase in self[i][src].items():
					print >> logs, "     ", phrase
	
if __name__ == "__main__":

	ptable = Phrase_Table(settings.opts.ptfile)
