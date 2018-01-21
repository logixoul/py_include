from lib.qthreading import interruption_point

class ImgPack:
	def __init__(self):
		self.imgs = []
	def __setitem__(self, item, value):
		self.imgs.append((item, value))
		interruption_point()
	def showLab(self, item, value):
		self[item] = Static.lab2bgr(value)
	def show_in_ui(self, mdi):
		for img in self.imgs:
			mdi.imshow(img[0], img[1])
