import cv2, numpy

# returns something that cv2.cvtColor accepts
def merge(seq):
	first = seq[0]
	shape = (first.shape[0], first.shape[1], len(seq))
	result = numpy.empty(shape, first.dtype)
	for i in range(len(seq)):
		result[:,:,i] = seq[i]
	return result
	
# not sure if cv2.split does copying. this func here doesn't.
def split(arr):
	seq = []
	numCh = arr.shape[2]
	for i in xrange(numCh):
		seq.append(arr[:,:,i])
	return seq