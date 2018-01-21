import numpy, numpy as np
import lib

"""def binOperator(image1, image2, op):
	#return numpy.frompyfunc(op, 2, 1)(image1, image2)
	image3 = numpy.zeros_like(image1)
	for x in xrange(image3.shape[0]):
		if x%100==0: lib.write("x=", x)
		for y in xrange(image3.shape[1]):
			for c in xrange(image3.shape[2]):
				coords = (x, y, c)
				image3[coords] = op(image1[coords], image2[coords])
	return image3"""

def normrange(obj):
	dtype = None
	if type(obj) is numpy.dtype:
		dtype = obj
	elif type(obj) is numpy.ndarray:
		dtype = obj.dtype
	class Range:
		def __init__(self, min, max):
			self.min = min
			self.max = max
	
	ranges = {
		numpy.dtype(numpy.uint8): Range(0, 255),
		numpy.dtype(numpy.uint16): Range(0, 65535),
		numpy.dtype(numpy.float32): Range(0.0, 1.0)
		}
	return ranges[dtype]

def normmin(obj):
	return normrange(obj).min

def normmax(obj):
	return normrange(obj).max

def convertAndNormalize(img, dest_dtype = np.float32):
	return img.astype(dest_dtype) / normmax(img.dtype)

def getSigmaForRadius(ksize):
	# http://docs.opencv.org/modules/imgproc/doc/filtering.html#Mat getGaussianKernel(int ksize, double sigma, int ktype)
	raise Exception()
	return 0.3*((ksize-1)*0.5 - 1) + 0.8

def getSigmaForDiameter(ksize):
	# http://docs.opencv.org/modules/imgproc/doc/filtering.html#Mat getGaussianKernel(int ksize, double sigma, int ktype)
	return 0.3*((ksize-1)*0.5 - 1) + 0.8

#def threshold_f_gt(img, scalar):
	#img2 = numpy.maximum(img - scalar)
	
def mm(img, desc=None):
	text = "amin,amax=%s,%s"%(np.amin(img),np.amax(img))
	if desc is not None:
		text = "[" + desc + "]" + text
	text = "[lib.mm] " + text
	print(text)
	
def ssd(desc, img):
	text = "shape,strides,dtype=%s,%s,%s"%(img.shape,img.strides,img.dtype)
	if desc is not None:
		text = "[" + desc + "]" + text
	text = "[lib.ssd] " + text
	print(text)