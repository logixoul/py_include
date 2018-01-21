import numpy
from collections import namedtuple

def range(dtype):
	rangeClass = namedtuple("range", 'min,max')
	try:
		return rangeClass(numpy.iinfo(dtype).min, numpy.iinfo(dtype).max)
	except:
		return rangeClass(numpy.finfo(dtype).min, numpy.finfo(dtype).max)