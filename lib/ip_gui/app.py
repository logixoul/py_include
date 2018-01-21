#! /usr/bin/python
import sys
sys.path.append("/home/stefan/include/py") # tmp before restarting ubuntu
import lib.gui as tgui
import colorama

import cv2, math, numpy, itertools
#import lib.ip_gui.sched as sched
from . import sched as sched
import lib
import os, sys, threading
from PyQt5 import QtWidgets, QtCore, QtGui
from lib import qthreading
from lib.lang import StaticMethod
import os
from datetime import datetime
import subprocess

def excepthook(type_,value,traceback_):
	import traceback
	msg = "Unhandled exception: %s" % "".join(traceback.format_exception(type_,value,traceback_, 10))
	print(msg)
	#tgui.msgbox("<pre>" + msg + "</pre>")
	exit()
	
sys.excepthook = excepthook

# usage: instantiate App, call tgui.addSlider(...) some times, call ip_gui.app.run()
class App:
	DEFAULT_QUALITY = 1.0/4.0
	
	def __init__(self, operatorClass):
		self.operatorClass = operatorClass
		#tgui.mdi.options.quality = App.DEFAULT_QUALITY
		
		tgui.mdi.sliders.onMoved = self.sliderMoved
		tgui.addSlider("resolution", 1, 1000, 500)
		
		#tgui.addSlider("method3_thres", 1, 100, 4, lambda x: x / 100.0)
		
		#tgui.mdi.options.iterations	 = 1
		#self.sliders.addSlider("saturation", 0, 100, 70, self.sliderMoved,
		#	valueMapper=lambda value: value / 100.0)
		tgui.mdi.onNewImage = self.onNewImage
		tgui.mdi.onKey = self.onKey
		QtWidgets.QApplication.clipboard().dataChanged.connect(self.onClipboardChanged)
		path=None
		if len(sys.argv) > 1:
			path = sys.argv[1]
		else:
			path = "test1.hdr"
		srcImage=Static.imread(path)
		lib.write("loaded with depth", srcImage.dtype)
		#self.prepareImage()
		self.onNewImage(srcImage)
		self.update()
		
	def prepareImage(self):
		tgui.status("-> float in 0..1")
		img3 = lib.cvhelpers.convertAndNormalize(self.srcImage, numpy.float32)
		self.srcImage = img3
		tgui.status("prepareImage done")
		
	@StaticMethod
	def raiseWindow():
		import subprocess
		subprocess.call("wmctrl -F -a main.py", shell=True)
	
	def onClipboardChanged(self):
		if not QtWidgets.QApplication.clipboard().mimeData().hasImage():
			return
		lib.write("activating")
		Static.raiseWindow()
		tgui.mdi.pasteImage()
		
	def sliderMoved(self, name, value):
		QtWidgets.QApplication.processEvents()
		self.update()
	
	@StaticMethod
	def imread(path):
		return cv2.imread(path, cv2.IMREAD_UNCHANGED)
	
	def get_scaled(self):
		scale1 = float(tgui.mdi.options.resolution) / self.srcImage.shape[1]
		scale2 = float(tgui.mdi.options.resolution) / self.srcImage.shape[0]
		scale = min(scale1, scale2)
		#lib.break_()
		#tgui.status("resizing")
		#import pdb; pdb.set_trace()
		img2 = cv2.resize(self.srcImage, (0, 0), None, scale, scale, cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC)
		return img2
	
	def update(self):
		print('update')
		if not hasattr(self, "srcImage"):
			return
		
		scaledImg = self.get_scaled()
		op = self.operatorClass(scaledImg, tgui.mdi.options)
		thread = sched.thread(op.run)
		thread.finished.connect(lambda: self.onThreadFinished(thread))
		if hasattr(self, 'current_thread'):
			if self.current_thread.isRunning():
				self.current_thread.setPriority(QtCore.QThread.IdlePriority)
		self.current_thread = thread
		thread.op = op
		tgui.mdi.setInProgress(True)
		op.begin_time = datetime.now()
		tgui.mdi.progressbar.setFormat("working")
		
	def onThreadFinished(self, thread):
		if thread is self.current_thread:
			thread.op.imgpack.show_in_ui(tgui.mdi)
			tgui.mdi.setInProgress(False)
			elapsed = datetime.now() - thread.op.begin_time
			tgui.mdi.progressbar.setFormat("%s elapsed" % elapsed)
	
	def onNewImage(self, newImage):
		lib.write("dropped")
		self.srcImage = newImage
		self.prepareImage()
		tgui.srcShape = self.srcImage.shape
		self.update()
		
	def onKey(self, key):
		if key == QtCore.Qt.Key_F5:
			import sys
			operatorModule = sys.modules[self.operatorClass.__module__]
			reload(operatorModule)
			self.operatorClass = getattr(operatorModule, self.operatorClass.__name__)
			#reload(lib)
			tgui.status("reloaded. redoing effect")
			self.update()
			tgui.status("all done")

#app = App()
#tgui.mainLoop()
def run():
	tgui.mainLoop()