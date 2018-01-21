from PyQt5 import QtCore, QtWidgets
import lib
#from lib.ip_gui import sched

# list of callables
_toExecute = []
mutex = QtCore.QMutex(QtCore.QMutex.Recursive)

class FunctionPostedEvent(QtCore.QEvent):
	EVENT_TYPE = QtCore.QEvent.User + 0
	def __init__(self):
		super(FunctionPostedEvent, self).__init__(FunctionPostedEvent.EVENT_TYPE)

def _executePending():
	global _toExecute
	global mutex
	with QtCore.QMutexLocker(mutex):
		for fn in _toExecute:
			fn()
		_toExecute = []

class _QtReceiver(QtCore.QObject):
	def customEvent(self, e):
		if e.type() == FunctionPostedEvent.EVENT_TYPE:
			_executePending()

# _qtReceiver is created on the mainthread => the postEvent we send to it will be handled in the
# main thread
_qtReceiver = _QtReceiver()

def post(fn):
	global mutex
	with QtCore.QMutexLocker(mutex):
		_toExecute.append(fn)
	# tmp launching as thread, as a workaround for an app that only has a single thread.
	QtWidgets.QApplication.postEvent(_qtReceiver, FunctionPostedEvent())
	
def as_task(fn):
	def wrapped(*args, **kwargs):
		post(lambda: fn(*args, **kwargs))
	return wrapped
