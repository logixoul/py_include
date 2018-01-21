"""import os
import glob
__all__ = [ os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py")]"""
import os
#for module in os.listdir(os.path.dirname(__file__)):
#    if module == '__init__.py' or module[-3:] != '.py':
#        continue
#    __import__(module[:-3], locals(), globals())
#del module

import lib.cv3
import lib.cvhelpers
import lib.deferred
import lib.gui
import lib.hdr
import lib.hooks
import lib.ip
import lib.lang
import lib.math
import lib.nphelpers
import lib.numpy_
import lib.openstruct
import lib.qthreading
import lib.threadtasks
import lib.ip_gui

from lib.deferred import write
from lib.openstruct import OpenStruct
from lib.cvhelpers import mm, ssd
from lib.qthreading import interruption_point

def break_():
	import PyQt5.QtCore
	import pdb
	PyQt5.QtCore.pyqtRemoveInputHook()
	pdb.set_trace()
