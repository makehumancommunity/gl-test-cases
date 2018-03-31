#!/usr/bin/python3

"""
This test only displays a window with a black square, which is a generic
QOpenGLWidget. GL functions have at this point not been initialized.
"""

from genericgl import TestApplication
from genericgl import Canvas

import sys

app = TestApplication(sys.argv)
app.exec_()
del app

sys.exit()

