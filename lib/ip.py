import cv2, numpy, numpy as np
import lib.cv3 as cv3
import sys
import lib

thismodule = sys.modules[__name__]

"""def luminanceBlendLAB(lSource, abSource):
		lib.write("WARNING: CONVERTING TO 8 BIT")
		lSourceLAB = cv2.cvtColor(lSource, cv.CV_BGR2Lab)
		abSourceLAB = cv2.cvtColor(abSource, cv.CV_BGR2Lab)
		lSourceLAB[:,:,1:3] = abSourceLAB[:,:,1:3]
		return cv2.cvtColor(lSourceLAB, cv.CV_Lab2BGR)"""
	
def luminanceBlendHLS(lSource, abSource):
		lSourceH, lSourceL, lSourceS = cv2.split(cv2.cvtColor(lSource, cv2.COLOR_BGR2HLS))
		abSourceH, abSourceL, abSourceS = cv2.split(cv2.cvtColor(abSource, cv2.COLOR_BGR2HLS))
		#abSourceH = cv2.split(cv2.cvtColor(abSource*.1, cv.CV_BGR2HLS))[0]
		resultHLS = cv3.merge([abSourceH, lSourceL, abSourceS])
		return cv2.cvtColor(resultHLS, cv2.COLOR_HLS2BGR)
	
def luminanceBlendHSV(lSource, abSource):
		lSourceH, lSourceS, lSourceV = cv2.split(cv2.cvtColor(lSource, cv2.COLOR_BGR2HSV))
		abSourceH, abSourceS, abSourceV = cv2.split(cv2.cvtColor(abSource, cv2.COLOR_BGR2HSV))
		resultHLS = cv3.merge([abSourceH, abSourceS, lSourceV])
		return cv2.cvtColor(resultHLS, cv2.COLOR_HSV2BGR)
	
def to01(src):
	amin, amax = np.amin(src), np.amax(src)
	return (src - amin) / (amax - amin)

def clamp01(src):
	return np.maximum(0.0, np.minimum(1.0, src))
	
"""def luminanceBlendXYZ_(lSource, chromSource):
		lSourceLinear = pow(lSource, 2.2)
		chromSourceLinear = pow(chromSource, 2.2)
		lSourceL = cv2.cvtColor(lSourceLinear, cv.CV_BGR2XYZ)[:,:,1]
		chromSourceL = cv2.cvtColor(chromSourceLinear, cv.CV_BGR2XYZ)[:,:,1]
		chromArray = chromSourceLinear / cv3.merge([chromSourceL]*3)
		chromArray = numpy.nan_to_num(chromArray)
		resultLinear = (chromArray * cv3.merge([lSourceL]*3))
		result = pow(resultLinear, 1.0 / 2.2)
		return result"""

def luminanceBlendXYZ_(Lpic, pic):
	pic_g = linToGrayscale(pic)
	return pic * lib.math.safeDiv(Lpic, pic_g)

def getLuminance(img):
	imgLinear = pow(img, 2.2)
	return cv2.cvtColor(imgLinear, cv.CV_BGR2XYZ)[:,:,1]

def getLuminanceHLS(img):
	return cv2.cvtColor(img, cv.CV_BGR2HLS)[:,:,1]

METHOD_LUMINANCE = object()
METHOD_HLS = object()
def toGrayscale(img, method=thismodule.METHOD_LUMINANCE):
	if(method is thismodule.METHOD_LUMINANCE):
		L = linGetLuminance(img)
		Lrgb = cv3.merge([L, L, L])
		return Lrgb
	if(method is thismodule.METHOD_HLS):
		lightness = getLuminanceHLS(img)
		srgb = cv3.merge([lightness, lightness, lightness])
		return srgb
	else:
		raise Exception()
		
def linGetLuminance(img):
	return cv2.cvtColor(img, cv2.COLOR_BGR2XYZ)[:,:,1]

def linToGrayscale(img):
	L = linGetLuminance(img)
	return cv3.merge([L, L, L])
	

# to convert from some colorspace other that rgb, attach a srcSpace attr to img before passing it here.
"""def convertColorspace(img, srcSpaceArg = None, dstSpace):
	srcSpace = srcSpaceArg if srcSpaceArg is not None else "RGB"
	spaces = (srcSpace, dstSpace)
	if spaces == ("RGB", "HLS"):
		
	else
		raise Exception()"""
	
