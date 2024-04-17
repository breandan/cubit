#!/usr/bin/env python

import sys
import math

logs = sys.stderr

from lattice import Lattice
import result
import settings
from log import logging
from container import Container

cum_tot = cum_score = 0

class Bin(object):

	### N.B. this design is very suspicious, which requires the identity x: x maintained all the time
	### a more intuitive way is x.cover : x
	
	def __init__(self, iden, hist=None, prob=None):
		
		self.id = iden
		self.best = None
		self.table = {}  ## mapping from item ('s signature) to item
		self.prob_beam = prob
		self.hist_beam = hist		

		## stats (.pruned and .discarded in Container)
		self.added = 0
		self.merged = 0
		self.discarded = 0
		self.pruned = 0
		self.total = 0
		
		self.sorted = None

   	def append(self, item):
		self.total += 1
		if settings.opts.forced is None or forced.find(item.trans()) >= 0:
			if self.pass_prob(item): #$ and self.pass_hist(item):
				if item not in self.table or item < self.table[item]:
					if item in self.table:
						logging(6, 3, lambda x: (">> replaced %s" % self.table[item]))

						## N.B.: tricky! if you don't delete, old item will still be the key,
						## which will be used in items(); not recommended for future
						del self.table[item]

						self.merged += 1
					self.table[item] = item  ## TODO: forest
					self.added += 1
					if self.best is None or item < self.best:
						self.best = item
					return 1
				else:
					logging(6, 3, lambda x: ("-- merged with %s" % self.table[item]))
					self.merged += 1
					return 2
			return 3

	def pass_prob(self, item):
		if (self.prob_beam is None) or (self.best is None) or (item - self.best < self.prob_beam):
			return True
		logging(6, 3, lambda x:("<< discarded (threshold = %.2lf, best = %.2lf)" \
				% (self.best.score() + self.prob_beam, self.best.score())))
		self.discarded += 1
		return False
	
	def best_res(self):
		if self.best is not None:
			return self.best.res
		return None

	def prob_prune(self):
		if self.prob_beam is not None:
			for x in self.table.keys():
				if not self.pass_prob(x):
					del self.table[x]
					self.discarded += 1

	def pruned_items(self):

		if self.sorted is None:
			self.prob_prune()		
			size = len(self.table)		
			a = [(x.score(), x) for x in self.table]
			a.sort()
			a = [y[1] for y in a]
			if self.hist_beam is not None:
				if size > self.hist_beam:
					for x in a[self.hist_beam:]:
						del self.table[x]
					del a[self.hist_beam:]
					self.pruned += size - self.hist_beam

			self.sorted = a

		return self.sorted

	def __len__(self):
		return len(self.table)

	def group_covers(self):
		''' group items in a bin by cover vector (signature)'''

		self.pruned_items()
		self.covermap = {}
		for it in self.sorted:
			if it.cover not in self.covermap:
				self.covermap[it.cover] = [it]
			else:
				self.covermap[it.cover].append(it)

def forward_search(lattice):
	for i in range(n+1):
		logging(2, 0, lambda x: ("items with length %d" % i))
		
		affected_bins = set()
		
		for st in chart[i].pruned_items():
			logging(3, 1, lambda x: ("from %s" % st, st.score()))
			## using item to generate new item
		
			for rang, dist in st.ranges():
				logging(4, 2, lambda x: ("range = (%d, %d)" % rang))

				for phrase in lattice[rang].items():
					newitem = st.advance(rang, dist, phrase)
					logging(4, 3, lambda x:("to", newitem,  "%.2lf" % newitem.score()))

					chart [newitem.len].append(newitem)
					
					affected_bins.add(newitem.len)

	for j in affected_bins:
		chart[j].prob_prune()

def backward_search(lattice):
	'''naive backward-star version of pharaoh'''
	
	chart[0].group_covers()
	for i in range(1, n+2):
		logging(2, 0, lambda x:("to items with length %d" % i))

		for j in range(max(0, i-7), i):
			for cov in chart[j].covermap:
				for (rang, dist) in cov.ranges():
					if (rang[1] - rang[0] == i - j) and len(lattice[rang]) > 0:
# 						print rang
						for st in chart[j].covermap[cov]:
							logging(3, 1, lambda x:("from", st))
							for phrase in lattice[rang].items():
								newitem = st.advance(rang, dist, phrase)
								logging(4, 2, lambda x:("to", newitem, "%.2lf" % newitem.score()))

								chart [i].append(newitem)

		chart[i].group_covers()
		
def online_cube(lattice):

	global tot_cube
	tot_cube = 0
	
	from state import Edge, GroupEdge, State, GroupState
	import heapq
	
	k, alpha = settings.opts.beam_hist, settings.opts.beam_prob
	
	chart[0].group_covers()
	for i in range(1, n+2):
		logging(2, 0, lambda x:("to items with length %d" % i))

		heap = []

		# for all previous bins
		for j in range(max(0, i-7), i):			
			for cov in chart[j].covermap:				
				for (rang, dist) in cov.ranges():
					if (rang[1] - rang[0] == i - j) and len(lattice[rang]) > 0:
#						print cov, rang
						for phrase in lattice[rang].items():
							items = chart[j].covermap[cov]
							edge = Edge(rang, dist, phrase, items)
							state = State(edge, 0)
							heap.append((state.score(), state))

							tot_cube += 1

		heapq.heapify(heap)

		while heap:			
			_, state = heapq.heappop(heap)
			item = state.item
			tryadd = chart[i].append(item)
			if len(chart[i]) > k or tryadd == 3:
				break
			for newstate in state.succ():
				logging(4, 0, lambda x: (newstate, ))
				heapq.heappush(heap, (newstate.score(), newstate))

				tot_cube += 1

		chart[i].group_covers()

def search(lattice, ff=None):
	from item import Item
	from lmitem import LMItem

	global forced
	if ff:		
		forced = ff.strip() + " </s>"
		print >> logs, "forced decoding:", forced
		
	global n, chart  ## will be used extensively in other classes as decoder.n
	n = settings.n

	chart = [Bin(i, hist=settings.opts.beam_hist, prob=settings.opts.beam_prob) for i in range(n + 2)]
	# 0 - initial ==> n - goal
	
 	chart [0].append(Item() if (settings.opts.tmonly or settings.opts.method == "lazy") else LMItem())

	if settings.opts.method == "cube":
		online_cube(lattice)
	elif settings.opts.method == "lazy":
		from lazy import *
		return lazy(chart, lattice)
		
	elif settings.opts.method == "back":
		backward_search(lattice)
	else:
		forward_search(lattice)
	
	return chart[n+1].best

def print_stats():
	global cum_tot, cum_score
	stats = {}
	print >> logs, "HYP: ",
	## note: total != added + discarded + pruned + merged (double-counting)
	if settings.opts.method != "lazy":
		if settings.opts.method == "cube":
			stats["total"] = tot_cube
			print >> logs, " " * 65, "total = %d\tscore = %.3lf" % (tot_cube, chart[n+1].best.score())
		else:			
			for item in "added", "discarded", "pruned", "merged", "total":
				stats[item] = sum(b.__dict__[item] for b in chart)
				print >> logs, "%s = %d\t" % (item, stats[item]),
			print >> logs, "score = %.3lf" % (chart[n+1].best.score())

		cum_tot += stats["total"]
		cum_score += chart[n+1].best.score()

		if settings.opts.print_items:
			for i in range(n+2):
				print >> logs, "length ", i
				for x in chart[i].pruned_items():
					print >> logs, "\t", x
	else:
		import lazy
		print >> logs, " "* 65, "total = %d\tscore = %.3lf" % (lazy.tot_push, lazy.result.score())
		cum_tot += lazy.tot_push
		cum_score += lazy.result.score()
		
def cum_stats():
	print >> logs, "cumulative total = %d score = %.5lf" % (cum_tot, cum_score)
	
def clear():
	settings.lm.clear()
	import cover
	cover.Cover.clear()
	#	del chart
