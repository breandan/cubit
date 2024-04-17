#!/usr/bin/env python

from state import Edge, State
import settings, math
import decoder, cover
from lmitem import *
import heapq
from hashedheap import *

from log import logging

class NewBin(list):

	### N.B. this design is very suspicious, which requires the identity x: x maintained all the time
	### a more intuitive way is x.cover : x
	
	def __init__(self, iden, hist=None, prob=None):

		list.__init__(self)
		self.id = iden
		self.best = None
		self.prob_beam = prob
		self.hist_beam = hist

	def append(self, item):
		list.append(self, item)
		if self.best is None or item < self.best:
			self.best = item

class LazyEdge(Edge):
	__slots__ = "cov" , "dep"

	def __init__(self, (f, t), dist, ph, items, cov, dep=0):
		Edge.__init__(self, (f, t), dist, ph, items)
		self.cov = cov
		self.dep = dep

	def fire(self, vecj):
		if len(self.items) <= vecj and not self.items.fixed:
			lazycube(self.fr, self.cov, vecj, self.dep+1)
		if len(self.items) > vecj:
			return LazyState(self, vecj, self.items[vecj].advance(self.rang, self.dist, self.phrase))
		else:
			return None
		
class LazyState(State):

	def __init__(self, edge, vecj, item, mid=0):
		## use edge to advance item in chart[from][vecj]

		self.edge = edge
		self.vecj = vecj

		logging(6, 0, lambda x: ("(%s, %d)" % (edge, vecj)))

		## replace by fire
		self.item = item #edge.items[vecj].advance(edge.rang, edge.dist, edge.phrase)
		self.mid = mid
		self._mid = None 

	def succ(self):
		''' successor'''

		state = self.edge.fire(self.vecj + 1)
		if state:
			yield state

	def __str__(self):
		return "%s @ %s -> %s" % (self.edge, self.vecj, self.item)

	def score(self):
		return self.item.score() - self.mid

	def midversion(self):
		if self._mid is None:
			midscore = self.score() - self.item.lmcost # - self.item.precost
			self._mid = (midscore, self) #LazyState(self.edge, self.vecj, self.item, mid)
		return self._mid

def lazycube(i, obj_cov, want, dep=0):
	'''i is the bin id; want is the wanted vecj'''
	global tot_push

	def enum(all=False):
		'''move from popped to bin'''
		bound = bin.midheap.peek()[0] if (not all and len(bin.midheap) > 0) else 1e10
		oldlen = len(bin)
		while (bin.popped != []) and bin.popped[0][0] < bound:
			bin.append(heapq.heappop(bin.popped)[1])
		for j in range(oldlen, len(bin)):
			logging(4, dep, lambda x:(i, obj_cov, " %d-th best=%s " % (j, bin[j]), "|p|=%d" % len(bin.popped) ))
		

	def push(state):
		global tot_push
		bin.heap.append((state.score(), state))
		bin.midheap.push(state.midversion())
		tot_push += 1
		logging(4, dep, lambda x: ("push %s " % state, "mid=%.2lf" % state._mid[0], \
								   "|c|=%d" % len(bin.heap)))

	## --------
	logging(2, dep, lambda x:("solving ", i, obj_cov, "  %d-th best" % want))
	
	bin = lmchart[i][obj_cov]
	k, alpha = bin.hist_beam, bin.prob_beam

	if bin.heap is None:
		bin.popped = []
		bin.heap = []
		bin.cache = {}
		bin.midheap = HashedHeap()
	
		for j in range(max(0, i-7), i):
			for cov in chart[j].covermap:				
				for (rang, dist) in cov.ranges():
					if (rang[1] - rang[0] == i - j) and len(lattice[rang]) > 0 and (cov.advance(rang) == obj_cov):
						for phrase in lattice[rang].items():
							#logging(3, dep, lambda x:("%s with %s" % (chart[j].covermap[cov][0], phrase)))
							### fine-grained states
							items = lmchart[j][cov]
							edge = LazyEdge(rang, dist, phrase, items, cov, dep)
							state = edge.fire(0)  # LazyState(edge, 0)
							if state:
								push(state)

		heapq.heapify(bin.heap)

	while len(bin) <= want and bin.heap:			
		_, state = heapq.heappop(bin.heap)
		bin.midheap.delete(state.midversion())

		item = state.item
		if item not in bin.cache or item < bin.cache[item]:
			bin.cache[item] = item
			heapq.heappush(bin.popped, (item.score(), item))
		else:
			logging(4, dep+1, lambda x: "duplicate!")

		logging(4, dep, lambda x: ("pop %s" % state,"|c|=%d" % len(bin.heap), " |p|=%d" % len(bin.popped)))

		
		if len(bin.popped) + len(bin) > k or (bin.best is not None and item - bin.best > alpha):
			bin.fixed = True
			break
		for newstate in state.succ():
			push(newstate)
			
		enum()

	if len(bin) <= want and len(bin.popped) > 0:
		enum(all=True)
	
def lazy(cha, latt):

	n = settings.n
	global lattice, lmchart, chart, tot_push, result
	tot_push = 0
	lattice = latt
	chart = cha
	# narrow-down tm-only beam; should tune these
	for i in range(n+2):
		pass
# 		chart[i].hist_beam /= 2
# 		chart[i].prob_beam -= math.log(10)
	# first-pass
	decoder.online_cube(lattice)
	
	# fine-grained chart
	lmchart = [{} for i in range(n+2)]
##	lmchart = [Bin(i, hist=settings.opts.beam_hist, prob=settings.opts.beam_prob) for i in range(n + 2)]
	for i in range(n+2):
		for cov in chart[i].covermap:
			bin = lmchart[i][cov] = NewBin(i, hist=settings.opts.beam_hist, prob=settings.opts.beam_prob)
			bin.fixed = False
			bin.heap = None

	init_cov = cover.default()
	lmchart[0][init_cov].append(LMItem())
	lmchart[0][init_cov].fixed = True
	# second-pass from final bin
	final_cov = chart[n+1].covermap.keys()[0]
	lazycube(n+1, final_cov, 0)

	result = lmchart[n+1][final_cov].best
	return lmchart[n+1][final_cov].best

