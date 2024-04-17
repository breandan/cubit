#!/usr/bin/env python

import sys, os
logs = sys.stderr

sys.path.append(os.environ["NEWCODE"])
from vector import Vector
import math

all_scores = True
maxd = 7
TM_weights = (0.0, 0.0, 0.9, 0.5, 0)
ttable_limit = 100
ttable_thres = 1e-10

def read_input():
	
	inputfile = open(sys.argv[1])
	for line in inputfile:
		words = tuple(line.split())

		for l in range(1, maxd + 1):
			for i in range(len(words) - l + 1):
				dicts[l].add(words[i: i+l])
				
def check(words):
	ll = len(words)
	if ll > maxd:
		print >> logs, "%d (> %d words): %s" % (ll, maxd, line)
		global toolong, maxlen
		toolong += 1
		if ll > maxlen:
			maxlen = ll
		return check(words[:maxd]) and check(words[-maxd:]) ## approx; caution recursion
	else:
		return words in dicts[ll]

def extract_phrase(line):
	source, target, scores = line.split("|||")
	return tuple(source.split()), target, (Vector(map(lambda x: -math.log(float(x)), scores.split())) * TM_weights, scores.strip())

def prune_print(curr):
	a = [(x[2][0], x[0], x[1], x[2][0], x[2][1]) for x in curr if x[2] > ttable_thres]
	a.sort()
	for i in range(min(len(a), ttable_limit)):
		logscore, s, t, probscore, allscores = a[i]
		print "%s ||| %s ||| " % (" ".join(s), t),
		if all_scores:
			print allscores
		else:
			print "%.5lf" % probscore


if __name__ == "__main__":

	dicts = [set() for i in range(maxd+1)]
	read_input()
	##print dicts[2]; exit(0)

	good = bad = total = toolong = maxlen = 0
	last = None
	curr = []
	for i, line in enumerate(sys.stdin):
		source, target, score = extract_phrase(line)
		if source == last:
			if lastisgood:
				curr.append((source, target, score))
				good += 1
			else:
				bad += 1						   
		else:
			if curr:
				prune_print(curr)
				curr = []
			if check(source):
				lastisgood = True
				curr = [(source, target, score)]
				good += 1
			else:
				lastisgood = False
				bad += 1
				
		last = source

		if i % 100000 == 0:
			print >> logs, "sofar = %d, good = %d, bad = %d" % (i, good, bad)
			print >> logs, "%d phrases longer than %d words; max = %d" % (toolong, maxd, maxlen)

	prune_print(curr) ## don't forget last
	
	print >> logs, "total = %d, good = %d, bad = %d" % (i, good, bad)
	print >> logs, "%d phrases longer than %d words; max = %d" % (toolong, maxd, maxlen)
