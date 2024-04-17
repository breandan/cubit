#/usr/bin/env python

import sys, math

import settings
from lattice import Lattice


class Cover(object):
	'''coverage vector (wrapper) now also includes "last", so that Cover is the only signature.
	N.B.: must be cover | set (returning cover), not set | cover (returning set)'''

	repos = {}

	@staticmethod
	def clear():
		Cover.repos = {}

	def copyfrom(self, other):
		self.ss = other.ss
		self.last = other.last
		self.len = other.len
		self.hashval = other.hashval

		self.first_uncov = other.first_uncov

		self.futurecost = other.futurecost
		self._ranges = other._ranges
		
	def __init__(self, ss=set(), last=0):
		if (tuple(ss), last) in Cover.repos:
			self.copyfrom(Cover.repos[(tuple(ss), last)])

		else:
			self._ranges = None
			self.ss = ss
			self.last = last
			self.len = len(ss)
			self.hashval = hash((tuple(self.ss), self.last))

			self.first_uncov = min(self.uncovered())

			uncov = self.uncovered_ranges()
			cov = self.uncovered_ranges(straight=False)
			self.futurecost = sum([Lattice.this.cost[x] for x in uncov])

			dist = abs(last - self.first_uncov) # + abs(self.len - self.first_uncov)
			for (i, j) in cov:
				if i > self.first_uncov:
					dist += abs(j - i)
			if self.len < settings.n and (settings.n-1) in ss:
				dist += settings.n * 10

			self.futurecost += dist * settings.opts.weight_distort
		
			Cover.repos[(tuple(ss), last)] = self

	def uncovered_ranges(self, straight=True):
		last_unc = 0
		unc = False
		res = []
		if not straight:
			s = self.uncovered()
		else:
			s = self.ss | set([settings.n])
		for i in range(settings.n+1):
			if i in s:
				if unc:
					res.append( (last_unc, i) )
				unc = False
			else:
				if not unc:
					last_unc = i
				unc = True
		return res
				
	def uncovered(self):
		## complement set
		return set(range(settings.n + 2)) - self.ss
	
	def __hash__(self):
		return self.hashval

	def ranges(self):
		'''yielding feasible ranges (with dist), based on last position, cover, and max-distortion-limit'''
		## start range = [last - max + 1, last + max + 1]
		if self._ranges is None:
			n = settings.n
			max_distort = settings.opts.max_distort
			res = []
			if len(self) == n:
				### '''final </s>'''
				### N.B.: Koehn bug: not counting the final distortion
				res = [((n, n + 1), n - self.last)]
			else:
				irange = range(max(0, self.last - max_distort), \
							   min(n, self.last + max_distort + 1))

				if self.first_uncov not in irange:
					irange += [self.first_uncov]

				for i in irange:
					## make sure you can get back (not exact!)
					maxright = self.first_uncov + max_distort if i > self.first_uncov else n

					for j in xrange(i + 1, min(n, i + Lattice.max_len) + 1):
						if (j - 1) not in self.ss and j <= maxright:
							res.append (((i, j), abs(i - self.last)))
						else:
							break  # stop here, try next i
			self._ranges = res
		return self._ranges

	def advance(self, (i, j)):
		c = Cover(self.ss | set(range(i,j)), j)
		return c
	
	def __str__(self):
		s = "".join(["*" if i in self.ss else "_" for i in range(settings.n)])
		return s[:self.last] + "." + s[self.last:] + "(%d)" % self.first_uncov

	def __len__(self):
		return self.len

	def __eq__(self, other):
		return self.last == other.last and self.ss == other.ss
	

class MonoCover(Cover):
	'''basically, nothing in the signature if monotone.'''

	def __init__(self, last=0):
		self.futurecost = 0  ## all equiv., no need for future cost
		self.last = last
		self.hashval = last
		self._ranges = None

	def ranges(self):
		if self._ranges is None:
			n = settings.n		
			res = []
			if len(self) == n:
				### '''final </s>'''
				### N.B.: Koehn bug: not counting the final distortion
				res = [((n, n + 1), 0)] #n - self.last)  
			else:
				for i in xrange(self.last + 1, min(self.last + Lattice.max_len, n+1)):
					res.append( ((self.last, i), 0))
			self._ranges = res
		return self._ranges

	def advance(self, (i, j)):
		return MonoCover(j)
	
	def __str__(self):
		return "@%d" % self.last

	def __len__(self):
		return self.last

	def __eq__(self, other):
		return self.last == other.last
	

def default():
	return Cover() if not settings.opts.monotone else MonoCover()
