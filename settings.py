#!/usr/bin/env python

import sys, math

logs = sys.stderr

class Model(object):
	__slots__ = "tm", "lm", "lenp", "distort"	

n = 0

def setn(nn):
	global n
	n = nn
	
def startlm(filename, order=3):
	from ngramtools import Ngram
	global lm

	lm = Ngram(3, filename)

	#Phrase_Table.lm = LMState.lm = Result.lm = Lattice.lm = decoder.lm = lm

debugLM = False


def args():
	import optparse
	optparser = optparse.OptionParser(usage="usage: cat input | %prog [options]")

	optparser.add_option("-t", "--trace", dest="trace", default=False, \
						 help="print (back-)trace", action="store_true")
	optparser.add_option("", "--nofuture", dest="nofuture", default=False, \
						 help="do not use future cost estimation", action="store_true")
	optparser.add_option("", "--tmonly", dest="tmonly", default=False, \
						 help="first-pass is no LM but w/ length penalty", action="store_true")
	optparser.add_option("-v", "--verbose", dest="debug_level", type=int, default=0, help="verbose level")

	optparser.add_option("-d", "", dest="weight_distort", default=0.1, type=float, help="distortion model weight")
	optparser.add_option("-w", "", dest="weight_lenp", default=-1, type=float, help="length penalty weight (-)")
	optparser.add_option("", "--lmw", dest="weight_lm", default=1, type=float, help="language model weight")
	optparser.add_option("", "--tmw", dest="weight_tm", default="1.0", type=str, help="translation model weights")

	optparser.add_option("-s", "--stack", dest="beam_hist", default=100, type=int, help="histogram beam of bins")
	optparser.add_option("-b", "--beam", dest="beam_prob", default=1e-4, type=float, help="prob beams of bins")

	optparser.add_option("", "--ttable-limit", dest="ttable_limit", type=int, default=100, \
						 help="size of the histogram beams of phrase-table")
	optparser.add_option("", "--ttable-threshold", dest="ttable_thres", type=float, default=1e-100, \
						 help="(absolute) probabilitistic threshold of bins")

	optparser.add_option("", "--dl", dest="max_distort", type=int, default=0, help="distortion limit")
	optparser.add_option("-o", "--order", dest="order", type=int, default=3, help="order of ngram")

	optparser.add_option("", "--lmfile", dest="lmfile", default="small.srilm", help="srilm file")	
	optparser.add_option("", "--pt", dest="ptfile", default="phrase-table", help="phrase table file")	

	optparser.add_option("", "--unk-cost", dest="unk_cost", default=0, type=float, help="cost of an unknown source word")

	optparser.add_option("", "--method", dest="method", default="forward", help="search option")

	optparser.add_option("", "--forced", dest="forced", default=None, help="forced decoding file")

	optparser.add_option("", "--profile", dest="profiling", default=False, \
						 help="profile", action="store_true")
	optparser.add_option("", "--items", dest="print_items", default=False, \
						 help="print items in each bin in sorted order", action="store_true")
	
	global opts, model
	
	(opts, args) = optparser.parse_args()

	#### writing params into logs

	print >> logs

 	print >> logs, "weight-d (d): %.2lf" % opts.weight_distort
 	print >> logs, "weight-l (lmw): %.2lf" % opts.weight_lm
 	print >> logs, "weight-t (tmw): %s" % opts.weight_tm
 	print >> logs, "weight-w (w): %.2lf" % opts.weight_distort

	print >> logs

	print >> logs, "beam-hist (s): %d" % opts.beam_hist
	print >> logs, "beam-prob (b): %lf" % opts.beam_prob	

	print >> logs

	###########################
	
	opts.weight_tm = map(float, opts.weight_tm.split())
	
	model = Model()
	model.tm, model.lm, model.lenp, model.distort = \
			  opts.weight_tm, opts.weight_lm * math.log(10), opts.weight_lenp, opts.weight_distort

	opts.ttable_thres = - math.log(opts.ttable_thres)
	opts.beam_prob = - math.log(opts.beam_prob)	

	if True :#not opts.tmonly:
		startlm(opts.lmfile, opts.order)
	else:
		from idmap import IdMap
		global lm
		lm = IdMap()

	opts.monotone = (opts.max_distort == 0)

