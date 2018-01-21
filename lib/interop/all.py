from PyQt5 import *
import numpy, numpy as np
import os
import cv2
import lib.hooks
import lib

def _chooseTmpFileName():
	name_index = 0
	name = ""
	while True:
		name = "tmp_qimage_file_%s.png" % name_index
		if not os.path.isfile(name):
			return name
		name_index += 1

def _image_qt2cv_generic(qimage):
	#lib.hooks.status("CHECKING if it exists")
	tmpFileName = _chooseTmpFileName()
	lib.hooks.status("saving qimage to disk")
	success = qimage.save(tmpFileName)
	lib.write("saving success? ", success)
	lib.hooks.status("loading image from disk")
	cvImage = cv2.imread(tmpFileName)
	lib.hooks.status("REMOVING")
	os.remove(tmpFileName)
	return cvImage

# http://kogs-www.informatik.uni-hamburg.de/~meine/software/vigraqt/qimage2ndarray.py
def image_qt2cv(qimage):
	dtype = np.uint8
	# FIXME: raise error if alignment does not match
	buf = qimage.bits().asstring(qimage.numBytes())
	result_shape = (qimage.height(), qimage.width())
	temp_shape = (qimage.height(),
				  qimage.bytesPerLine() * 8 / qimage.depth(), 4)
	cvImage = numpy.frombuffer(buf, dtype).reshape(temp_shape)
	cvImage = cvImage[:,:result_shape[1]]
	if qimage.format() == QtGui.QImage.Format_RGB32:
		cvImage = cvImage[...,:3]
	cvImage = cvImage.copy()
	return cvImage

def _image_cv2qt_generic(cvImage):
	tmpFileName = _chooseTmpFileName()
	lib.hooks.status("[image_cv2qt] saving qimage to disk")
	cvImage8u = (np.minimum(cvImage, 1.0) * 255.0).astype(numpy.uint8)
	cv2.imwrite(tmpFileName, cvImage8u)
	lib.hooks.status("[image_cv2qt] loading image from disk")
	qimage = QtGui.QImage(tmpFileName)
	qpixmap = QtGui.QPixmap(qimage)
	lib.hooks.status("REMOVING")
	os.remove(tmpFileName)
	lib.hooks.status("done")
	return qpixmap

def image_cv2qt(cvImage):
	cvImage8u = (np.maximum(np.minimum(cvImage, 1.0), 0.0) * 255.0).astype(numpy.uint8)
	h, w, channels = cvImage.shape
	
	qimage = QtGui.QImage(cvImage8u.data, w, h, w * 3, QtGui.QImage.Format_RGB888)
	qimage = qimage.rgbSwapped()
	qpixmap = QtGui.QPixmap(qimage)
	return qpixmap

"""def convert(self, cvImage):
	cvImageLDR = (cvImage * 255.0).astype(numpy.uint8)
	h, w, channels = cvImage.shape
	cvImageARGB = numpy.empty((h, w, 4), cvImageLDR.dtype, 'C')
	cvImageARGB[...,0:3] = cvImageLDR[...,0:3]
	cvImageARGB[...,3] = 255
	
	qimage = QtGui.QImage(cvImageARGB.data, w, h, QtGui.QImage.Format_RGB32)
	qpixmap = QtGui.QPixmap(qimage)
	qpixmap.antigc = cvImageARGB
	return qpixmap"""