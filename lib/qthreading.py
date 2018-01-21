from PyQt5 import QtCore
import lib
import sys

SHOULD_EXIT = {}

class BailOutException(Exception):
	pass

class Thread(QtCore.QThread):
	def __init__(self,fn,parent=None):
		super(Thread, self).__init__(parent)
		self.fn = fn
		
	def run(self):
		try:
			self.fn()
		except BailOutException:
			pass
		except Exception as foo:
			print("CAUGHT NON-BAILOUT EXCEPTION")
			sys.excepthook(*sys.exc_info())

def interruption_point():
	current_thread = QtCore.QThread.currentThread()
	current_thread.priority()
	if current_thread.priority() == QtCore.QThread.IdlePriority:
		print("hit interruption point with idle priority, bailing out")
		raise BailOutException()