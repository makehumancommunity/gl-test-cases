#!/usr/bin/python3

"""
Try to draw a ten pixel wide red dot at the center of the canvas. 
For reference: the coordinates, color and size of the dot are 
set in the shaders, not in the python source. 
"""

from genericgl import TestApplication
from genericgl import Canvas
from genericgl import info

import sys

from PyQt5.QtGui import QOpenGLShaderProgram, QOpenGLShader

class TestCanvas(Canvas):

    def __init__(self):

        with open("vertex.glsl","r") as f:
            self.vertexShaderSource = f.read()

        with open("fragment.glsl","r") as f:
            self.fragmentShaderSource = f.read()

        if self.vertexShaderSource is None:
            raise Exception("Could not load the source for the vertex shader")

        if self.fragmentShaderSource is None:
            raise Exception("Could not load the source for the fragment shader")

        super(TestCanvas,self).__init__()

    def setupGL(self):

        # Take point size instructions in shaders into account
        self.gl.glEnable(self.gl.GL_POINT_SIZE)
        self.gl.glEnable(self.gl.GL_VERTEX_PROGRAM_POINT_SIZE)

        self.program = QOpenGLShaderProgram(self.context())
        info("PROGRAM",self.program)

        # addShaderFromSourceCode() only returns a bool telling whether everything went well

        if self.program.addShaderFromSourceCode(QOpenGLShader.Vertex, self.vertexShaderSource):
            info("VERTEX SHADER","Managed to load and parse the vertex shader")

        if self.program.addShaderFromSourceCode(QOpenGLShader.Fragment, self.fragmentShaderSource):
            info("FRAGMENT SHADER","Managed to load and parse the fragment shader")

        # Compile and bind the shader program to the current context
        self.program.link()
        self.program.bind()

        # Bind the shader attribute to a python variable
        self.somePosition = self.gl.glGetAttribLocation(self.program.programId(), "somePosition")

        # Tell GL that whenever we run glClear, this is the color that
        # should be used. We only need to do this once. 
        self.gl.glClearColor(0.1, 0.1, 0.1, 1.0)

    def paintGL(self):
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        
        # Assign a value to the shader parameter
        self.gl.glVertexAttrib3f(self.somePosition, 0.5, 0.5, 0.0)

        # Mode, starting at vertex number, number of vertices to draw
        self.gl.glDrawArrays(self.gl.GL_POINTS,0,1)

    def resizeGL(self, width, height):
        pass

app = TestApplication(sys.argv, TestCanvas)
app.exec_()
del app
sys.exit()

