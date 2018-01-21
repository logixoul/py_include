import pyglet
import numpy, numpy as np

def image_np2pg(npImage):
	assert(npImage.shape[2] == 3)
	assert(npImage.dtype == np.float32)
	w = npImage.shape[1]; h = npImage.shape[0]; format_ = 'RGB'
	pitch = -w * len(format_)
	npImage8 = (npImage * 255.0).astype(np.uint8)

	image = pyglet.image.ImageData(w, h, format_, str(npImage8.data), pitch)
	return image