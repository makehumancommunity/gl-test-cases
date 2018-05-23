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
from genericgl.testapplication import _TestApplication

import array
import json

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class TestCanvas(RotatableCanvas):

    def __init__(self):

        self.suzanne = Wavefront("../objs/stripped_base_mesh.obj")

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

        self.diffuseStrength = 0.8
        self.ambientStrength = 0.2
        self.specularStrength = 0.1
        self.specularHardness = 6

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

        # Find light setting uniforms
        self.diffuseStrengthUniform = self.program.uniformLocation("diffuseStrength")
        self.ambientStrengthUniform = self.program.uniformLocation("ambientStrength")
        self.specularStrengthUniform = self.program.uniformLocation("specularStrength")
        self.specularHardnessUniform = self.program.uniformLocation("specularHardness")

        # This returns a numpy array with the shape [ [XYZNNN] [XYZNNN] ... ]
        self.vertices2d = self.suzanne.getVertexAndNormalArray()

        # ... so we need to flatten it to an 1d array
        self.vertices = self.suzanne.getVertexAndNormalArray().flatten()

        # Number of elements in the flattened array
        self.verticesLength = self.vertices.size

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

        # What GL datatype should we tell the buffer that we're using? This is necessary, since it
        # might be different on 32-bit and 64-bit machines

        self.glDataType = None # let it crash if it isn't float or double

        if self.vertices.itemsize == 4:
            self.glDataType = self.gl.GL_FLOAT

        if self.vertices.itemsize == 8:
            self.glDataType = self.gl.GL_DOUBLE

        # Total size in bytes for entire array
        self.verticesDataLength = self.vertices.nbytes

        # 2d Array with vertex indices that make up faces
        self.indices2d = self.suzanne.getFaceArray()
        
        # Flattened version suitable for drawElements
        self.indices = self.indices2d.flatten().tolist()

        # Number of elements in the index array. 
        self.numberOfVertices = self.indices2d.size

        # Start specifying the Vertex Array Object (VAO). 
        self.suzanneVAO = QOpenGLVertexArrayObject()
        self.suzanneVAO.create()
        self.suzanneVAO.bind()
 
        # Create a VBO for holding vertex info (both positions and normals)
        self.verticesBuffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.verticesBuffer.create()
        self.verticesBuffer.bind()
        self.verticesBuffer.setUsagePattern(QOpenGLBuffer.StaticDraw)
        self.verticesBuffer.allocate(self.vertices.tobytes(), self.verticesDataLength)

        # Here we specify that there is a program attribute that should get data that is sent
        # to it (by glDraw* operations), and in what form the data will arrive. 
        self.program.enableAttributeArray( self.program.attributeLocation("somePosition") )
        self.program.setAttributeBuffer( self.program.attributeLocation("somePosition"), self.glDataType, 0, 3, self.vertexStride )
        
        # Say that the inputNormal attribute should be read from the same array, that it should take three values at a 
        # time (the normal vector), and that they are of type GL_FLOAT. The same byte offset as for the position info is used, but
        # we now also specify that the normal information starts at normalBytesOffset bytes into each vertex specification
        self.program.enableAttributeArray( self.program.attributeLocation("inputNormal") )
        self.program.setAttributeBuffer( self.program.attributeLocation("inputNormal"), self.glDataType, self.normalBytesOffset, 3, self.vertexStride )
        
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

        # Set light uniforms
        self.program.setUniformValue(self.diffuseStrengthUniform, self.diffuseStrength)
        self.program.setUniformValue(self.ambientStrengthUniform, self.ambientStrength)
        self.program.setUniformValue(self.specularStrengthUniform, self.specularStrength)
        self.program.setUniformValue(self.specularHardnessUniform, float(self.specularHardness))

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

    def updateParameters(self, diffuseStrength, ambientStrength, specularStrength, specularHardness):

        self.diffuseStrength = diffuseStrength
        self.ambientStrength = ambientStrength
        self.specularStrength = specularStrength
        self.specularHardness = specularHardness

        self.update()


class SettingsWidget(QWidget):

    def __init__(self, mainWidget):

        super(SettingsWidget, self).__init__()

        self.mainWidget = mainWidget

        self.layout = QVBoxLayout(self)

        self.diffuseStrength = 0.8
        self.ambientStrength = 0.2
        self.specularStrength = 0.1
        self.specularHardness = 6

        self.diffuseStrengthLabel = QLabel("-")
        self.ambientStrengthLabel = QLabel("-")
        self.specularStrengthLabel = QLabel("-")
        self.specularHardnessLabel = QLabel("-")
        
        self.diffuseStrengthSlider = QScrollBar(Qt.Horizontal)
        self.ambientStrengthSlider = QScrollBar(Qt.Horizontal)
        self.specularStrengthSlider = QScrollBar(Qt.Horizontal)
        self.specularHardnessSlider = QScrollBar(Qt.Horizontal)

        self.diffuseStrengthSlider.setMinimum(0)
        self.diffuseStrengthSlider.setMaximum(10)
        self.diffuseStrengthSlider.setPageStep(1)
        self.diffuseStrengthSlider.setSingleStep(1)
        self.diffuseStrengthSlider.setValue(int(10 * self.diffuseStrength))
        self.diffuseStrengthSlider.valueChanged.connect(self.sliderMoved)

        self.ambientStrengthSlider.setMinimum(0)
        self.ambientStrengthSlider.setMaximum(10)
        self.ambientStrengthSlider.setPageStep(1)
        self.ambientStrengthSlider.setSingleStep(1)
        self.ambientStrengthSlider.setValue(int(10 * self.ambientStrength))
        self.ambientStrengthSlider.valueChanged.connect(self.sliderMoved)

        self.specularStrengthSlider.setMinimum(0)
        self.specularStrengthSlider.setMaximum(10)
        self.specularStrengthSlider.setPageStep(1)
        self.specularStrengthSlider.setSingleStep(1)
        self.specularStrengthSlider.setValue(int(10 * self.specularStrength))
        self.specularStrengthSlider.valueChanged.connect(self.sliderMoved)

        self.specularHardnessSlider.setMinimum(1)
        self.specularHardnessSlider.setMaximum(64)
        self.specularHardnessSlider.setPageStep(1)
        self.specularHardnessSlider.setSingleStep(1)
        self.specularHardnessSlider.setValue(self.specularHardness)
        self.specularHardnessSlider.valueChanged.connect(self.sliderMoved)

        self.layout.addWidget(self.diffuseStrengthLabel)
        self.layout.addWidget(self.diffuseStrengthSlider)
        self.layout.addWidget(self.ambientStrengthLabel)
        self.layout.addWidget(self.ambientStrengthSlider)
        self.layout.addWidget(self.specularStrengthLabel)
        self.layout.addWidget(self.specularStrengthSlider)
        self.layout.addWidget(self.specularHardnessLabel)
        self.layout.addWidget(self.specularHardnessSlider)

        self.layout.addStretch()    
        self.resize(600, 600);

        self.updateLabels()

    # Override if necessary                                                                                        
    def minimumSizeHint(self):                                                                                     
        return QSize(200, 200)                                                                                       

    def sizeHint(self):                                                                                            
        return QSize(600, 600)

    def updateLabels(self):
        self.diffuseStrengthLabel.setText("diffuseStrength: " + str(self.diffuseStrength))
        self.ambientStrengthLabel.setText("<br />ambientStrength: " + str(self.ambientStrength))
        self.specularStrengthLabel.setText("<br />specularStrength: " + str(self.specularStrength))
        self.specularHardnessLabel.setText("<br />specularHardness: " + str(self.specularHardness))

    def sliderMoved(self):

        self.diffuseStrength = self.diffuseStrengthSlider.value() / 10
        self.ambientStrength = self.ambientStrengthSlider.value() / 10
        self.specularStrength = self.specularStrengthSlider.value() / 10
        self.specularHardness = self.specularHardnessSlider.value()

        self.updateLabels()

        self.mainWidget.updateParameters(self.diffuseStrength, self.ambientStrength, self.specularStrength, self.specularHardness)


class SettingsApplication(_TestApplication):

    def __init__(self, args, glWidget = QOpenGLWidget):

        super(SettingsApplication, self).__init__(args, glWidget)

        self.settingsWidget = SettingsWidget(self.mainWidget)
        self.layout.addWidget(self.settingsWidget)
        self.mainWin.resize(1200,600)


app = SettingsApplication(sys.argv, TestCanvas)
app.exec_()
del app
sys.exit()

