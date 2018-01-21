import sys
import numpy, numpy as np

pymath = sys.modules["math"]
_log = pymath.log
_exp = pymath.exp

def lmap(val, ifrom, ito, ofrom, oto):
	if ifrom==ito:
		return (ofrom+oto) * .5;
	in01 = (val-ifrom)/float(ito-ifrom);
	return ofrom + in01 * (oto-ofrom);

def lerp(a, b, f):
	return a + (b-a) * f

def expRange(a, b, f):
	return _exp(lerp(_log(a), _log(b), f))

def safeDiv(numerator, denominator):
	denominator2 = np.where(numerator == 0.0, 1.0, denominator) # where num was zero, set denom to 1
	return numerator / denominator2
