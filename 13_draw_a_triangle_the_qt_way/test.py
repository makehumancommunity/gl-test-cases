#!/usr/bin/python3

"""
This is the same as example 07, except that we use Qt wrappers around VBO and VAO to draw a 
triangle rather than talking directly to opengl.
"""

from genericgl import TestApplication
from genericgl import Canvas
from genericgl import info

import sys
import array

from PyQt5.QtGui import *
from PyQt5.QtCore import *


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

        # Instead of asking GL directly to allocate an array buffer, we ask QT
        # to set up one for us. In GL language we are creating a "VBO" here. 
        self.verticesBuffer = QOpenGLBuffer()
        self.verticesBuffer.create()
        self.verticesBuffer.bind()
        self.verticesBuffer.setUsagePattern(QOpenGLBuffer.StaticDraw)
        self.verticesBuffer.allocate(self.vertices.tobytes(), self.verticesDataLength)
        
        # We then wrap this in another layer to get what GL calls "VBO". The upside
        # of this approach is that we can keep all settings pertaining to the VBO and
        # not have to specify them again at draw time. This will make it a lot easier 
        # to keep multiple VBOs around. 
        self.triangleVAO = QOpenGLVertexArrayObject()
        self.triangleVAO.create()
        self.triangleVAO.bind()
      
        # Operations we perform between bind() and release() of the VAO will be 
        # remembered when we bind it again at a later time. Here we will specify 
        # that there is a program attribute that should get data that is sent
        # to it (by glDraw* operations), and in what form the data will arrive. 
        self.program.enableAttributeArray( self.program.attributeLocation("somePosition") )
        self.program.setAttributeBuffer( self.program.attributeLocation("somePosition"), self.gl.GL_FLOAT, 0, 3, 0 )

        # Once we have set up all object we can release them until we'll need them again at
        # draw time
        self.triangleVAO.release()
        self.verticesBuffer.release()
        self.program.release()

        self.gl.glClearColor(0.1, 0.1, 0.1, 1.0)

        self.dumpGLLogMessages("setupGL()")

    def paintGL(self):
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        
        # We re-enable the program and the VAO. Note that we don't need to re-enable the VBO. 
        self.program.bind()
        self.triangleVAO.bind()

        # Draw a triangle starting at vertex number. Since we enabled attribarrays, it will fetch data from the array buffer
        self.gl.glDrawArrays(self.gl.GL_TRIANGLES, 0, self.numberOfVertices)

        # Release the VAO and the program until the next time we need to draw. 
        self.triangleVAO.release()
        self.program.release()

        self.dumpGLLogMessages("paintGL()")

    def resizeGL(self, width, height):
        pass

    def closeGL(self):
        # We need to explicitly destroy VAOs, VBOs and programs. Otherwise we'll get a 
        # segfault or another similar crash.
        self.triangleVAO.destroy()
        self.verticesBuffer.destroy()
        del self.program

app = TestApplication(sys.argv, TestCanvas)
app.exec_()
del app
sys.exit()

