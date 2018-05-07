#!/usr/bin/python3

"""
Try to change the background color to red. This is interesting in order
to know if any operations whatsoever are allowed against the GL functions
object. 
"""

from genericgl import TestApplication
from genericgl import Canvas

import sys

class TestCanvas(Canvas):

    def __init__(self):
        super(TestCanvas,self).__init__()

    def setupGL(self):
        # Tell GL that whenever we run glClear, this is the color that
        # should be used. We only need to do this once. 
        self.gl.glClearColor(1.0, 0.0, 0.0, 1.0)
        self.dumpGLLogMessages("setupGL()")

    def paintGL(self):
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        self.dumpGLLogMessages("paintGL()")

    def resizeGL(self, width, height):
        pass

app = TestApplication(sys.argv, TestCanvas)
app.exec_()
del app
sys.exit()

