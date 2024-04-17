#!/usr/bin/env python

import sys

logs = sys.stderr
import settings

##symbols = ["|", "-", "!", "+"]
symbols = ["  "] 

def logging(level, dep, func):
	'''lazy function; avoids calculation of stuff in func in case not to print'''
	if level <= settings.opts.debug_level:
		print >> logs, " ".join([symbols[i % len(symbols)] for i in range(dep)]),
		fields = func(None)
		print >> logs, "".join(map(str, fields))
