from lib.lang import StaticMethod
import numpy, numpy as np
import lib.ip as ip
import lib

def luminanceReinhard(img):
	L = ip.linToGrayscale(img)
	L2 = L / (L + 1.0)
	return img * lib.math.safeDiv(L2, L)

def reinhard(img):
	lib.write("[rh] amax = ", np.amax(img))
	lib.write("[rh] amin = ", np.amin(img))
	return img / (img + 1.0)

def invReinhard(img, highestL):
	# 1/(1-k*1)=highestL
	#1-k*1=1/highestL
	#k=1-1/highestL
	k = 1.0-1.0/highestL
	return img / (1.0 - k * img)

