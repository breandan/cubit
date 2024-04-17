#!/usr/bin/env python

import  decoder
from log import logging

class GroupEdge(object):
	__slots__ = "fr", "to", "rang", "items", "rules", "visited"

	def __init__(self, (f, t), rules):
		self.fr, self.to = f, t
		self.rang = (f, t)
		self.rules = rules
		self.items = decoder.chart[f].pruned_items()
		self.visited = set()

	def __str__(self):
		return "(%d, %d)" % self.rang
	
class Edge(object):
	__slots__ = "fr", "to", "rang", "dist", "phrase", "items"

	def __init__(self, (f, t), dist, ph, items):
		self.fr, self.to = f, t
		self.dist = dist
		self.rang = (f, t)		
		self.phrase = ph
		self.items = items #decoder.chart[f].pruned_items()

	def __str__(self):
		return "(%d, %d) = %s" % (self.fr, self.to, self.phrase)

class State(object):

	def __init__(self, edge, vecj):
		## use edge to advance item in chart[from][vecj]

		self.edge = edge
		self.vecj = vecj

		logging(6, 0, lambda x: ("(%s, %d)" % (edge, vecj)))
		
		self.item = edge.items[vecj].advance(edge.rang, edge.dist, edge.phrase)

	def score(self):
		return self.item.score()

	def succ(self):
		''' successor'''

		if len(self.edge.items) > self.vecj + 1:
			yield State(self.edge, self.vecj + 1)

	def __str__(self):
		return "%s @ %s -> %s" % (self.edge, self.vecj, self.item)

class GroupState(object):
	'''2D square pruning: need to check duplicates'''

	def __init__(self, edge, vecj):
		## use edge to advance item in chart[from][vecj]

		self.edge = edge
		self.vecj = vecj

		logging(6, 0, lambda x: ("(%s, %d)" % (edge, vecj)))

		a, b = vecj
		self.item = edge.items[a].advance(edge.rang, 0, edge.rules[b])
		edge.visited.add(vecj)

	def score(self):
		return (self.item.score(), self.vecj)   ## vecj ordering important for 2D, 3D...

	def succ(self):
		''' successor(s)'''
		
		a, b = self.vecj
		if len(decoder.chart[self.edge.fr]) > a + 1:
			if (a+1, b) not in self.edge.visited:
				yield GroupState(self.edge, (a + 1, b))
		if len(self.edge.rules) > b + 1:
			if (a, b+1) not in self.edge.visited:
				yield GroupState(self.edge, (a, b + 1))

	def __str__(self):
		return "%s @ %s -> %s" % (self.edge, self.vecj, self.item)
