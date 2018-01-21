from PyQt5 import QtWidgets, QtCore, QtGui
import sys, ctypes, os
import numpy
import cv2
import lib.interop
import lib
from lib import threadtasks
from lib.lang import StaticMethod

app = None
mdi = None
options = None
def init():
	import signal
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	global app
	app = QtWidgets.QApplication(sys.argv)
	global mdi
	mdi = MDI()
	global options
	options = mdi.options

def mainLoop():
	app.exec_()

_this_module = sys.modules[__name__]

class SliderSet:
	WINDOW_NAME = "slider"
	def __init__(self, onMoved):
		self.widget = QtWidgets.QWidget()
		self.widget.setMinimumWidth(300)
		self.layout = QtWidgets.QFormLayout(self.widget)
		self.onMoved = onMoved
	
	def addSlider(self, name, min, max, initialValue, valueMapper=lambda x: x, flags=0):
		if not hasattr(valueMapper, '__call__'):
			raise Exception("passed args in wrong order?")
		if flags & FSLIDER == FSLIDER:
			self._addSliderF(name, min, max, initialValue, valueMapper)
		else:
			self._addSliderI(name, min, max, initialValue, valueMapper)
	
	def _addSliderI(self, name, min, max, initialValue, valueMapper):
		def forwardOnmoved(slider, value):
			global mdi
			setattr(mdi.options, name, valueMapper(value))
			self.onMoved(name, valueMapper(value))
			status(str(valueMapper(value)))
		slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
		slider.setRange(min, max)
		self.layout.addRow(name, slider)
		slider.setTracking(False)
		slider.sliderMoved.connect(lambda value: forwardOnmoved(slider, value))
		slider.setValue(initialValue)
		global mdi
		setattr(mdi.options, name, valueMapper(initialValue))
	
	SLIDER_IMPL_MAX=10000
	def _addSliderF(self, name, min, max, initialValue, valueMapper):
		min = float(min)
		max = float(max)
		initialValue = float(initialValue)
		def mapToRequestedRange(sliderVal, requestedMin, requestedMax):
			return lib.math.lerp(requestedMin, requestedMax, sliderVal / float(SliderSet.SLIDER_IMPL_MAX))
		def mapToImplRange(val, requestedMin, requestedMax):
			result = lib.math.lmap(val, requestedMin, requestedMax, 0.0, float(SliderSet.SLIDER_IMPL_MAX))
			result = int(result)
			return result
		def forwardOnmoved(slider, implValue, min_, max_):
			global mdi
			value = mapToRequestedRange(implValue, min_, max_)
			setattr(mdi.options, name, valueMapper(value))
			self.onMoved(name, valueMapper(value))
			status("slider value",str(valueMapper(value)))
		slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
		#slider.setRange(min, max)
		slider.setRange(0, SliderSet.SLIDER_IMPL_MAX)
		self.layout.addRow(name, slider)
		slider.setTracking(False)
		slider.sliderMoved.connect(lambda value: forwardOnmoved(slider, value, min, max))
		slider.setValue(mapToImplRange(initialValue, min, max))
		global mdi
		setattr(mdi.options, name, valueMapper(initialValue))
		
class MDI(QtWidgets.QWidget):
	class OptionsClass:
		def get(self, name, min, max, initialValue, valueMapper=lambda x: x, flags=0):
			if not hasattr(self, name):
				mdi.addSlider(name, min, max, initialValue, valueMapper, flags)
			return getattr(self, name)
	def __init__(self):
		super(MDI, self).__init__()
		
		#===================== PUBLIC EVENTS ==========================
		self.onNewImage = lambda img: None
		self.onKey = lambda key: None
		self.onMoved = lambda slider, val: None
		#==============================================================
		self.options = MDI.OptionsClass()
		
		
		self.layout = QtWidgets.QHBoxLayout()
		
		self.sidebar = QtWidgets.QVBoxLayout()
		self.sliders = SliderSet(lambda slider, value: self.onMoved(slider, value))
		
		self.layout.addLayout(self.sidebar)
		self.sidebar.addWidget(self.sliders.widget)
		
		self.setLayout(self.layout)
		self.tabWidget = QtWidgets.QTabWidget()
		self.layout.addWidget(self.tabWidget, 1)
		
		paste = QtWidgets.QPushButton("paste")
		paste.clicked.connect(self.pasteImage)
		self.sidebar.addWidget(paste)
		
		zoomToFit = QtWidgets.QPushButton("actual size")
		zoomToFit.clicked.connect(self.zoomToFit)
		self.sidebar.addWidget(zoomToFit)
		self.progressbar = QtWidgets.QProgressBar()
		self.progressbar.setMinimum(0)
		self.progressbar.setMaximum(0)
		
		self.statusbar = QtWidgets.QLabel("-")
		self.sidebar.addWidget(self.statusbar)
		self.show()
		self.setAcceptDrops(True)
		#shortcut = QtWidgets.QShortcut(QtWidgets.QKeySequence(QtWidgets.QKeySequence.Copy), self)
		shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Paste), self)
		shortcut.activated.connect(self.pasteImage)
		self.connectShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Left), lambda: self.prevNextTab(-1))
		self.connectShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Right), lambda: self.prevNextTab(1))
		self.connectShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Up), lambda: self.quickJump(0))
		self.connectShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Down), lambda: self.quickJumpBack())
		self.connectShortcut(QtGui.QKeySequence(QtCore.Qt.Key_A), lambda: self.zoomToFit())
		#self.connectShortcut(QtWidgets.QKeySequence(Qt.QtWidgets.Key_Control, Qt.QtWidgets.Key_Plus),
		#	lambda: 
		#self.setWindowState(QtCore.Qt.WindowMaximized)
		self.resize(1280, 720)
		self.imageViewers = []
		#self.toolbar = QtWidgets.QToolBar()
		#self.installEventFilter(self)
		self.animation = None
		self.tabs = { } # dict from name to widget
		
		self.statusValues = { } # dict from title to text
		
		self.setInProgress(False)
		
	"""def flashStatus(self):
		del self.animation
		self._status_color = QtWidgets.QColor(255,0,0)
		self.animation = QtCore.QPropertyAnimation(self, "status_color", self)
		self.animation.setDuration(2000)
		self.animation.setStartValue(QtWidgets.QColor(255,0,0,255))
		self.animation.setEndValue(QtWidgets.QColor(255,0,0,0))

		self.animation.start()
	
	@QtCore.pyqtProperty(QtWidgets.QColor)
	def status_color(self):
		return self._status_color
	
	@StaticMethod
	def fmt_css_color(c):
		return "rgba(%s, %s, %s, %s)" % (c.red(), c.green(), c.blue(), c.alpha())
	
	@status_color.setter
	def status_color(self, value):
		self._status_color = value
		self.statusbar.setStyleSheet("background-color: " + Static.fmt_css_color(value))"""
	
	def addSlider(self, name, min, max, initialValue, valueMapper=lambda x: x, flags=0):
		self.sliders.addSlider(name, min, max, initialValue, valueMapper, flags)
		
	def setInProgress(self, enable):
		if enable:
			self.progressbar.setMaximum(0)
		else:
			if self.progressbar.maximum() == 0:
				self.progressbar.setMaximum(1)
		
	def prevNextTab(self, offset):
		index = self.tabWidget.currentIndex() + offset
		index %= self.tabWidget.count()
		self.tabWidget.setCurrentIndex(index)
		
	def quickJump(self, index):
		if self.tabWidget.currentIndex() == index:
			return
		self.beforeQuickJump = self.tabWidget.currentIndex()
		self.tabWidget.setCurrentIndex(index)
		
	def quickJumpBack(self):
		if not hasattr(self, "beforeQuickJump"):
			return
		self.tabWidget.setCurrentIndex(self.beforeQuickJump)
		
	def connectShortcut(self, keyseq, callback): # keyseq is e.g. QtWidgets.QKeySequence.Paste
		shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(keyseq), self)
		shortcut.activated.connect(callback)
	
	#def eachViewer(self, func):
		#for viewer in self.imageViewers:
			#
		
	def zoomToFit(self):
		for viewer in self.imageViewers:
			#viewer.actualSize()
			viewer._view.fitInView(viewer._pixmapItem, QtCore.Qt.KeepAspectRatio)
		lib.write("zoomtofit")
	
	def synchViews(self, srcView, name):
		pass
		"""if hasattr(self, 'currentlySynching') and self.currentlySynching:
			return
		self.currentlySynching = True
		for viewer in self.imageViewers:
			if viewer is srcView:
				continue
			viewer.zoomFactor = srcView.zoomFactor
			viewer.scrollState = srcView.scrollState
		self.currentlySynching = False"""
	
	def pasteImage(self):
		self.status("getting image from clipboard")
		clipboard = QtWidgets.QApplication.clipboard()
		image = clipboard.image()
		if image.isNull():
			return
		self.status("converting to cv format")
		cvImage = lib.interop.all.image_qt2cv(image)
		lib.write("loaded with depth", cvImage.dtype)

		self.status("calling onNewImage")
		self.onNewImage(cvImage)
		self.status("done")
	
	@threadtasks.as_task
	def status(self, title, text):
		self.statusValues[title] = text
		completeText = "\n".join("%s: %s" % (i[0], i[1]) for i in self.statusValues.items())
		self.statusbar.setText(completeText)
		QtWidgets.QApplication.processEvents()
		
	def dragEnterEvent(self, e):
		lib.write("dragenter")
		e.acceptProposedAction()
	
	def dropEvent(self, e):
		lib.write("dropEvent. mime formats:", e.mimeData().formats()[0])
		lib.write("hasimage? ", e.mimeData().hasImage())
		if not e.mimeData().hasImage():
			if e.mimeData().formats().contains("text/uri-list"):
				filePath=e.mimeData().data("text/uri-list")
				filePath=str(filePath)[7:-2].replace("%20", " ")
				#def bytes(s):
				#	return "[%s]" % ", ".join(str(ord(c)) for c in s)
				image = cv2.imread(filePath, cv2.CV_LOAD_IMAGE_UNCHANGED)
				print("imgshape", image.shape)
				import lib.cv3 as cv3
				#r,g,b=cv3.split(image)
				#image = cv3.merge((b,g,r))
				self.onNewImage(image)
				return
			else:
				msgbox("mimedata.hasimage=false")
		qvariant = e.mimeData().imageData()
		lib.write('variant type=', qvariant.type())
		image = QtWidgets.QImage(qvariant)
		lib.write('width=', image.width())
		lib.write('converted,saving')
		cvImage = lib.interop.all.image_qt2cv(image)
		self.onNewImage(cvImage)
		
	def keyPressEvent(self, e):
		if e.key() == QtCore.Qt.Key_Escape:
			QtWidgets.QApplication.exit()
		else:
			self.onKey(e.key())
			
	def closeEvent(self, e):
		QtWidgets.QApplication.exit()
	
	def addTab(self, widget, name):
		self.tabs[name] = widget
		self.imageViewers.append(widget)
		
		tabNames = (self.tabWidget.tabText(i) for i in range(self.tabWidget.count()))
		index = self.tabWidget.addTab(widget, name)
		
		# fix imagewidget fitToWindow problem before tab is first selected
		self.tabWidget.setCurrentIndex(index)
		QtWidgets.QApplication.processEvents()
		
		#widget.transformChanged.connect(lambda: self.synchViews(widget, name))
		#widget.scrollChanged.connect(lambda: self.synchViews(widget, name))
	
	#@threadtasks.as_task
	def imshow(self, name, image):
		widget = None
		if name in self.tabs:
			widget = self.tabs[name]
		else:
			widget = QtWidgets.QLabel()
			self.addTab(widget, name)
		cv2.imwrite("tmpout/" + name + ".png", image)
		widget.pixmap = lib.interop.all.image_cv2qt(image)
		widget.antigc = widget.pixmap
		
# addSlider flags (or-able)
FSLIDER=1

def addSlider(name, min, max, initialValue, valueMapper=lambda x: x, flags=0):
	global mdi
	mdi.sliders.addSlider(name, min, max, initialValue, valueMapper, flags)

def status(str1, str2=None):
	global mdi
	title, text = None, None
	if str2 == None:
		title, text = "status", str1
#		mdi.status("status", str1)
	else:
		title, text = str1, str2
	mdi.status(title, text)

def imshow(name, image):
	global mdi
	mdi.imshow(name, image)
	
@lib.threadtasks.as_task
def msgbox(text):
	global mdi
	#QtWidgets.QMessageBox.information(mdi, "main.py", text)

	msgbox = QtWidgets.QMessageBox(mdi)
	msgbox.setWindowTitle("main.py")
	msgbox.setText(text)
	msgbox.setMinimumWidth(1100)
	msgbox.exec_()
