#!/usr/bin/python3

"""
Use directional lighting and ambient lighting to implement
a primitive lighting model. The model is loaded from a 
wavefront obj that was created with Blender.
"""

import sys
import os.path
sys.path.append('/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1]))

from genericgl import TestApplication
from genericgl import RotatableCanvas
from genericgl import info
from genericgl import Wavefront

import array

from PyQt5.QtGui import *
from PyQt5.QtCore import *


class TestCanvas(RotatableCanvas):

    def __init__(self):

        self.suzanne = Wavefront("../objs/suzanne_triangulated.obj")

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

        # This returns an array with order XYZ NNN
        self.vertices = self.suzanne.getVertexAndNormalArray()

        # Buffer info returns a tuple where the second part is number of elements in the array
        self.verticesLength = self.vertices.buffer_info()[1]

        # Each vertex is specified with with six values (xyznnn)
        self.arrayCellsPerVertex = 6

        # Size in bytes for each vertex specification (self.vertices.itemsize is the size in bytes
        # of a single array cell)
        self.vertexSpecificationSize = self.vertices.itemsize * self.arrayCellsPerVertex

        # In bytes, where in a vertex specification does the normal data start? (it starts after 
        # x, y, z.. i.e after 3 array cells)
        self.normalBytesOffset = self.vertices.itemsize * 3

        # How many bytes are there in between vertex location specifications
        self.vertexStride = self.vertices.itemsize * self.arrayCellsPerVertex

        # Total size in bytes for entire array
        self.verticesDataLength = self.verticesLength * self.vertices.itemsize

        # Array with vertex indices that make up faces
        self.indices = self.suzanne.getFaceArray()

        # Number of vertices in the index array. 
        self.numberOfVertices = self.indices.buffer_info()[1]

        # Start specifying the Vertex Array Object (VAO). 
        self.suzanneVAO = QOpenGLVertexArrayObject()
        self.suzanneVAO.create()
        self.suzanneVAO.bind()
 
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
        
        # Say that the inputNormal attribute should be read from the same array, that it should take three values at a 
        # time (the normal vector), and that they are of type GL_FLOAT. The same byte offset as for the position info is used, but
        # we now also specify that the normal information starts at normalBytesOffset bytes into each vertex specification
        self.program.enableAttributeArray( self.program.attributeLocation("inputNormal") )
        self.program.setAttributeBuffer( self.program.attributeLocation("inputNormal"), self.gl.GL_FLOAT, self.normalBytesOffset, 3, self.vertexStride )
        
        # Once we have set up everything related to the VBOs, we can release that and the 
        # related VAO.
        self.verticesBuffer.release()
        self.suzanneVAO.release()
     
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
        self.suzanneVAO.bind()

        # Draw the VAO. It will remember which VBO was specified for it. Note the use
        # of glDrawElements rather than glDrawArrays. 
        self.gl.glDrawElements(self.gl.GL_TRIANGLES, self.numberOfVertices, self.gl.GL_UNSIGNED_SHORT, self.indices)

        # Release the VAO
        self.suzanneVAO.release()

        # Release the program
        self.program.release()

        self.dumpGLLogMessages("paintGL()")

    def resizeGL(self, width, height):
        scaleX = 1.0
        scaleY = 1.0
        scaleZ = 1.0 # Will always be 1.0 since we don't scale depth yet
        scaleW = 1.6 # A global scale factor. Higher = smaller object on screen. 

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
        self.suzanneVAO.destroy()
        self.verticesBuffer.destroy()
        del self.program

app = TestApplication(sys.argv, TestCanvas)
app.exec_()
del app
sys.exit()

