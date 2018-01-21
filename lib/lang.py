import sys

class StaticMethod(object):
	def __init__(self, f):
		self.f = f
		callingModule = sys.modules[f.__module__]
		if not hasattr(callingModule, "Static"):
			dynamicType = type("Static", tuple(), dict())
			setattr(callingModule, "Static", dynamicType)
		class_Static = getattr(callingModule, "Static")
			
		setattr(class_Static, f.__name__, self)

	def __get__(self, obj, objtype=None):
		return self.f
