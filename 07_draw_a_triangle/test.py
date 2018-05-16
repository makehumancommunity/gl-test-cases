#!/usr/bin/python3

"""
Draw a triangle using a vertex array buffer. 
"""

import sys
import os.path
sys.path.append('/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1]))

from genericgl import TestApplication
from genericgl import Canvas
from genericgl import info

import array

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

        # Use array rather than list in order to get control over actual data size
        self.vertices = array.array('f', [-0.5, -0.5, 0.0, 0.5, 0.5, 0.0, 0.5, -0.5, 0.0])

        # Buffer info returns a tuple where the second part is number of elements in the array
        self.verticesLength = self.vertices.buffer_info()[1]

        # Size in bytes for each element
        self.verticesItemSize = self.vertices.itemsize

        # Total size in bytes for entire array
        self.verticesDataLength = self.verticesLength * self.verticesItemSize

        # Number of vertices in the array
        self.numberOfVertices = int(self.verticesLength / 3)

        # Tell gl to prepare a buffer
        self.vertexBuffer = self.gl.glGenBuffers(1)

        # Say that the buffer is of type GL_ARRAY_BUFFER
        self.gl.glBindBuffer(self.gl.GL_ARRAY_BUFFER, self.vertexBuffer)

        # Copy data into the buffer
        self.gl.glBufferData(self.gl.GL_ARRAY_BUFFER, self.verticesDataLength, self.vertices.tobytes(), self.gl.GL_STATIC_DRAW)

        # Say that the somePosition attribute should be read from the current array, that it should take three values at a
        # time (x, y, z), and that they are of the type GL_FLOAT
        self.gl.glVertexAttribPointer(self.somePosition, 3, self.gl.GL_FLOAT, False, 0, 0)

        # When reading from the current data, start at position 0
        self.gl.glEnableVertexAttribArray(0)

        # Tell GL that whenever we run glClear, this is the color that
        # should be used. We only need to do this once. 
        self.gl.glClearColor(0.1, 0.1, 0.1, 1.0)

        self.dumpGLLogMessages("setupGL()")

    def paintGL(self):
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        
        # Draw a triangle starting at vertex number. Since we enabled attribarrays, it will fetch data from the array buffer
        self.gl.glDrawArrays(self.gl.GL_TRIANGLES, 0, self.numberOfVertices)

        self.dumpGLLogMessages("paintGL()")

    def resizeGL(self, width, height):
        pass

app = TestApplication(sys.argv, TestCanvas)
app.exec_()
del app
sys.exit()

