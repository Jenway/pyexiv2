import platform

# Check the Python interpreter
if not platform.python_version().startswith('3.') or platform.architecture()[0] != '64bit':
    raise RuntimeError("pyexiv2 can only run by Python3(64bit).")

# Recognize the system
sys_name = platform.system() or 'Unknown'
if sys_name == 'Linux':
    import os
    import ctypes
    lib_dir = os.path.dirname(__file__)
    ctypes.CDLL(os.path.join(lib_dir, "linux64/libexiv2.so")) # import libexiv2.so at first, otherwise the Python interpreter can not find it.
    from .linux64 import api
elif sys_name == 'Windows':
    from .win64 import api
else:
    raise RuntimeError("pyexiv2 can only run on Linux(64bit) or Windows(64bit), but your system is {}.".format(sys_name))