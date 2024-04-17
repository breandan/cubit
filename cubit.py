#!/usr/bin/env python

import sys, os

sys.path.append(os.environ["NEWCODE"])
sys.path.append(os.environ["NEWCODE"] + "/tools")

from phrase_table import *
from lattice import Lattice
import decoder

from result import Result
import settings

import mymonitor, time

def main():
	Lattice.ptable = Phrase_Table(settings.opts.ptfile)

	t0 = mymonitor.cpu()	

	if settings.opts.forced:
		forcedfile = open(settings.opts.forced)
	for sid, line in enumerate(sys.stdin):
		t1 = mymonitor.cpu()
		
		source = line.split()
		if source[0][0] == "#":
			continue
		lattice = Lattice(source)
		lattice.pp()		

		#exit (0)

		settings.setn(len(source))

		forced = forcedfile.readline() if settings.opts.forced else None
		
  		item = decoder.search(lattice, forced)
		if item is not None:
			s = item.res.naked()
			print s.split("\t")[1]			
			print >> logs, "sent #%d\t%s" % (sid + 1, s)
			decoder.print_stats()
			if settings.opts.trace:
				print >> logs, item.backtrace()
		else:
			print "translation failed!"

		print >> logs, "len = %d time = %.3lf" % (settings.n, mymonitor.cpu() - t1)
		decoder.clear()

	print >> logs, "total time = %.3lf" % (mymonitor.cpu() - t0)
	decoder.cum_stats()
		#break

if __name__ == "__main__":

	try:
## 		import psyco
## 		psyco.full()
		pass
	except:
		pass
	
	settings.args() # also starts the
	
	if settings.opts.profiling:
		import hotshot
		import hotshot.stats

		prof = hotshot.Profile("wrap.prof")

		prof.runcall(main)

		prof.close()
		stats = hotshot.stats.load("wrap.prof")
		stats.strip_dirs().sort_stats('time', 'calls').print_stats(50)

	else:
		main()
