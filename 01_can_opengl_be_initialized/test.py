#!/usr/bin/python3

"""
This test only displays a window with a black square, which is an instance
of the Canvas in genericgl. GL functions have at this point been initialized.
"""

import sys
import os.path
sys.path.append('/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1]))

from genericgl import TestApplication
from genericgl import Canvas


class TestCanvas(Canvas):

    def __init__(self):
        super(TestCanvas,self).__init__()

    def setupGL(self):
        pass

    def paintGL(self):
        pass

    def resizeGL(self, width, height):
        pass

app = TestApplication(sys.argv, TestCanvas)
app.exec_()
del app
sys.exit()

