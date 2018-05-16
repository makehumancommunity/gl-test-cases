#!/usr/bin/python3

"""
Draw a multicolored quad with data about both vertex position (XYZ) and vertex 
color (RGBA) fetched from the same array. See also comments in the shader files. 
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

        # Bind the shader attribute for transfering vertex positions to a python variable
        self.somePosition = self.gl.glGetAttribLocation(self.program.programId(), "somePosition")

        # Bind the shader attribute for transfering vertex colors to a python variable
        self.inputColor = self.gl.glGetAttribLocation(self.program.programId(), "inputColor")

        # Here we mix vertex data (x, y, z) with color data (r, g, b, a).
        self.vertices = array.array('f', [
            -0.5, -0.5, 0.0,   1.0, 0.0, 0.0, 1.0, # Bottom left is red
            -0.5, 0.5, 0.0,    0.0, 1.0, 0.0, 1.0, # Top left is green
            0.5, 0.5, 0.0,     0.0, 0.0, 1.0, 1.0, # Top right is blue
            0.5, -0.5, 0.0,    1.0, 1.0, 0.0, 1.0  # Bottom right is yellow
        ])

        # Buffer info returns a tuple where the second part is number of elements in the array
        self.verticesLength = self.vertices.buffer_info()[1]

        # Each vertex is specified with with seven values (xyzrgba)
        self.arrayCellsPerVertex = 7

        # Size in bytes for each vertex specification (self.vertices.itemsize is the size in bytes
        # of a single array cell)
        self.vertexSpecificationSize = self.vertices.itemsize * self.arrayCellsPerVertex

        # In bytes, where in a vertex specification does the color data start? (it starts after 
        # x, y, z.. i.e after 3 array cells)
        self.colorBytesOffset = self.vertices.itemsize * 3

        # Total size in bytes for entire array
        self.verticesDataLength = self.verticesLength * self.vertices.itemsize

        # Number of vertices in the array
        self.numberOfVertices = int(self.verticesLength / self.arrayCellsPerVertex)

        # Tell gl to prepare a single buffer
        self.vertexBuffer = self.gl.glGenBuffers(1)

        # Say that the buffer is of type GL_ARRAY_BUFFER
        self.gl.glBindBuffer(self.gl.GL_ARRAY_BUFFER, self.vertexBuffer)

        # Copy data into the buffer
        self.gl.glBufferData(self.gl.GL_ARRAY_BUFFER, self.verticesDataLength, self.vertices.tobytes(), self.gl.GL_STATIC_DRAW)

        # Say that the somePosition attribute should be read from the current array, that it should take three values at a
        # time (x, y, z), and that they are of the type GL_FLOAT. We now also specify a byte offset (vertexSpecificationSize)
        # to say that each new vertex specification is starting this many bytes after the prior one.
        self.gl.glVertexAttribPointer(self.somePosition, 3, self.gl.GL_FLOAT, False, self.vertexSpecificationSize, 0)

        # Connect the array to the somePosition variable
        self.gl.glEnableVertexAttribArray(self.somePosition)

        # Say that the inputColor attribute should be read from the current array, that it should take four values at a 
        # time (r, g, b, a), and that they are of type GL_FLOAT. The same byte offset as for the position info is used, but
        # we now also specify that the color information starts at colorBytesOffset bytes into each vertex specification
        self.gl.glVertexAttribPointer(self.inputColor, 4, self.gl.GL_FLOAT, False, self.vertexSpecificationSize, self.colorBytesOffset)

        # Connect the array to the inputColor variable
        self.gl.glEnableVertexAttribArray(self.inputColor)

        # Tell GL that whenever we run glClear, this is the color that
        # should be used. We only need to do this once. 
        self.gl.glClearColor(0.1, 0.1, 0.1, 1.0)

        self.dumpGLLogMessages("setupGL()")

    def paintGL(self):
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        
        # Draw a quad starting at vertex number. Since we enabled attribarrays, it will fetch data from the array buffer
        self.gl.glDrawArrays(self.gl.GL_QUADS, 0, self.numberOfVertices)

        self.dumpGLLogMessages("paintGL()")

    def resizeGL(self, width, height):
        pass

app = TestApplication(sys.argv, TestCanvas)
app.exec_()
del app
sys.exit()

