#!/usr/bin/python

# see https://code.djangoproject.com/wiki/ProfilingDjango

import hotshot.stats
import sys

stats = hotshot.stats.load(sys.argv[1])
#stats.strip_dirs()
stats.sort_stats('time', 'calls')
stats.print_stats(20)
