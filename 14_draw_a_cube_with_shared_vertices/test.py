#!/usr/bin/python3

"""
Use Qt's wrappers for Vertex Array Objects (VAO) and Vertex Buffer Objects (VBO) to
draw a multicolored cube with shared vertices for corners. Note that contrary to 
earlier experiments, we're using drawElements rather than drawArrays. 
"""

import sys
import os.path
sys.path.append('/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1]))

from genericgl import TestApplication
from genericgl import RotatableCanvas
from genericgl import info

import array

from PyQt5.QtGui import *
from PyQt5.QtCore import *


class TestCanvas(RotatableCanvas):

    def __init__(self):

        with open("vertex.glsl","r") as f:
            self.vertexShaderSource = f.read()

        with open("fragment.glsl","r") as f:
            self.fragmentShaderSource = f.read()

        if self.vertexShaderSource is None:
            raise Exception("Could not load the source for the vertex shader")

        if self.fragmentShaderSource is None:
            raise Exception("Could not load the source for the fragment shader")

        # Use an initial scale assuming width = height (should always be overwritten
        # in the resizeGL method below)
        self.currentScaling = QVector4D(1.0, 1.0, 1.0, 1.0)

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

        # Find the uniform location for controling the viewport scale of the vertex positions
        self.viewportScaling = self.program.uniformLocation("viewportScaling")

        # Find the uniform location for controling the rotation of the object
        self.objectRotation = self.program.uniformLocation("objectRotation")

        # Location and color for vertices. We specity vertices independently of
        # faces, so it does not matter in which order they occur. 
        self.vertices = array.array('f', [
            -0.5,-0.5,-0.5,   1.0, 0.0, 0.0, 1.0, # Front bottom left is red
            -0.5, 0.5,-0.5,   0.0, 1.0, 0.0, 1.0, # Front top left is green
             0.5, 0.5,-0.5,   0.0, 0.0, 1.0, 1.0, # Front top right is blue
             0.5,-0.5,-0.5,   1.0, 1.0, 0.0, 1.0, # Front bottom right is yellow
            -0.5,-0.5, 0.5,   0.0, 1.0, 1.0, 1.0, # Back bottom left is cyan
            -0.5, 0.5, 0.5,   1.0, 1.0, 1.0, 1.0, # Back top left is white
             0.5, 0.5, 0.5,   1.0, 0.0, 1.0, 1.0, # Back top right is purple
             0.5,-0.5, 0.5,   0.5, 0.5, 0.5, 1.0  # Back bottom right is gray
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

        # How many bytes are there in between vertex location specifications
        self.vertexStride = self.vertices.itemsize * 7  # (7 because XYZRGBA)

        # Total size in bytes for entire array
        self.verticesDataLength = self.verticesLength * self.vertices.itemsize

        # Create an array with unsigned short values for specifying each face 
        # of the cube
        self.indices = array.array('H', [
            0, 1, 2, 3,    # Front face
            4, 5, 6, 7,    # Back face
            1, 0, 4, 5,    # Left face
            2, 3, 7, 6,    # Right face
            1, 2, 6, 5,    # Top face
            0, 3, 7, 4     # Bottom face
        ])

        # Number of vertices in the index array. Note that this is different
        # from the number of vertices in the *vertex* array (which are 8 in 
        # total). In the *index* array, each vertex can be counted multiple 
        # times. So for 6 faces with 4 vertices each, we have 24 vertices 
        # specified by their indexes. 
        self.numberOfVertices = self.indices.buffer_info()[1]

        # Start specifying the Vertex Array Object (VAO). 
        self.cubeVAO = QOpenGLVertexArrayObject()
        self.cubeVAO.create()
        self.cubeVAO.bind()
 
        # Create a VBO for holding vertex position info
        self.verticesBuffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.verticesBuffer.create()
        self.verticesBuffer.bind()
        self.verticesBuffer.setUsagePattern(QOpenGLBuffer.StaticDraw)
        self.verticesBuffer.allocate(self.vertices.tobytes(), self.verticesDataLength)

        # Here we specify that there is a program attribute that should get data that is sent
        # to it (by glDraw* operations), and in what form the data will arrive. 
        self.program.enableAttributeArray( self.program.attributeLocation("somePosition") )
        self.program.setAttributeBuffer( self.program.attributeLocation("somePosition"), self.gl.GL_FLOAT, 0, 3, self.vertexStride )
        
        # Say that the inputColor attribute should be read from the same array, that it should take four values at a 
        # time (r, g, b, a), and that they are of type GL_FLOAT. The same byte offset as for the position info is used, but
        # we now also specify that the color information starts at colorBytesOffset bytes into each vertex specification
        self.program.enableAttributeArray( self.program.attributeLocation("inputColor") )
        self.program.setAttributeBuffer( self.program.attributeLocation("inputColor"), self.gl.GL_FLOAT, self.colorBytesOffset, 4, self.vertexStride )
        
        # Once we have set up everything related to the VBOs, we can release that and the 
        # related VAO.
        self.verticesBuffer.release()
        self.cubeVAO.release()
     
        # Release the program until we need to actually draw something. 
        self.program.release()

        self.gl.glClearColor(0.1, 0.1, 0.1, 1.0)

        self.dumpGLLogMessages("setupGL()")

    def paintGL(self):
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        
        # We re-enable the program and use it for all draw operations (both VAOs use
        # this program)
        self.program.bind()

        # Set current rotation as a uniform
        self.currentRotation = QVector3D(self.xRot / 16, self.yRot / 16, self.zRot / 16)
        self.program.setUniformValue(self.objectRotation, self.currentRotation)

        # Before painting we set the scaling "uniform" parameter in the vertex shader.
        # This will be used to scale the vertex positions. 
        self.program.setUniformValue(self.viewportScaling, self.currentScaling)
 
        # Activate the VAO
        self.cubeVAO.bind()

        # Draw the VAO. It will remember which VBO was specified for it. Note the use
        # of glDrawElements rather than glDrawArrays. 
        self.gl.glDrawElements(self.gl.GL_QUADS, self.numberOfVertices, self.gl.GL_UNSIGNED_SHORT, self.indices)

        # Release the VAO
        self.cubeVAO.release()

        # Release the program
        self.program.release()

        self.dumpGLLogMessages("paintGL()")

    def resizeGL(self, width, height):
        scaleX = 1.0
        scaleY = 1.0
        scaleZ = 1.0 # Will always be 1.0 since we don't scale depth
        scaleW = 1.0 # A global scale factor, also always 1.0

        if width > height:
            scaleX = height / width
        else:
            scaleY = width / height

        self.currentScaling = QVector4D(scaleX, scaleY, scaleZ, scaleW)

        # Redraw since we changed the value of the scaling uniform
        self.update()

    def closeGL(self):
        # We need to explicitly destroy VAOs, VBOs and programs. Otherwise we'll get a 
        # segfault or another similar crash.
        self.cubeVAO.destroy()
        self.verticesBuffer.destroy()
        del self.program

app = TestApplication(sys.argv, TestCanvas)
app.exec_()
del app
sys.exit()

