import os
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__("lib.ip_gui."+module[:-3], locals(), globals())
del module

from lib.ip_gui.imgpack import ImgPack
from lib.ip_gui.app import App
