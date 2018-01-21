import cv2, sys

DEBUG_WINDOWS = None
NODEBUG = object()

_this_module = sys.modules[__name__]

def imshow(name, img, nodebug = None):
	if not DEBUG_WINDOWS and nodebug is not NODEBUG:
		return
	cv2.imshow(name, img)
	cv2.waitKey(1)
	
def putText(image, text, place = (0, 30)):
	cv2.putText(
			image,
			text,
			place,
			cv2.FONT_HERSHEY_COMPLEX_SMALL, 
			1,
			(255,255,255),
			1,
			cv2.CV_AA
			)
			
class Window:
	def __init__(self, name, hidden = False):
		#cv2.namedWindow(name)
		self.name = name
		self.hidden = hidden
		
	def hide(self):
		self.hidden = True
		
	def imshow(self, image, nodebug = None):
		if not self.hidden:
			_this_module.imshow(self.name, image, nodebug)
			
class SliderSet:
	WINDOW_NAME = "slider"
	def __init__(self):
		cv2.namedWindow(SliderSet.WINDOW_NAME)
		self._values = { }
	
	def addSlider(self, name, min, max, onMoved):
		def forwardOnmoved(value):
			self._values[name] = value
			onMoved(value)
		cv2.createTrackbar(name, SliderSet.WINDOW_NAME, min, max, forwardOnmoved);
		self._values[name] = min
		
	def __getitem__(self, key):
		return self._values[key]