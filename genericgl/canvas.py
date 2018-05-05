#/usr/bin/python3

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from .simpledebug import info

class Canvas(QOpenGLWidget):

    def __init__(self, parent=None, app=None, requestedGLVersion=(2,1)):

        self.app = app
        self.requestedVersion = requestedGLVersion

        super(Canvas, self).__init__(parent)

    # Override if necessary
    def minimumSizeHint(self):
        info("CANVAS","minimumSizeHint() is not overridden")
        return QSize(50, 50)

    # Override if necessary
    def sizeHint(self):
        info("CANVAS","sizeHint() is not overridden")
        return QSize(600, 600)

    # Do not override this, instead override setupGL
    def initializeGL(self):

        if self.app and self.app.debugMembers:

            print("\n--- MEMBERS IN CANVAS ---")
            for member in dir(self):
                print(member)
            print ("---\n")
    
            print("\n--- MEMBERS IN CONTEXT ---")
            ctx = self.context()
            for member in dir(ctx):
                print(member)
            print ("---\n")

        self.profile = QOpenGLVersionProfile()
        self.profile.setVersion(self.requestedVersion[0],self.requestedVersion[1])
        self.gl = self.context().versionFunctions(self.profile)
        self.gl.initializeOpenGLFunctions()

        info("PROFILE",self.profile)
        info("FUNCTIONS",self.gl)

        self.setupGL()

        glVer = self.gl.glGetString(self.gl.GL_VERSION)
        glLangVer = self.gl.glGetString(self.gl.GL_SHADING_LANGUAGE_VERSION)
        glVendor = self.gl.glGetString(self.gl.GL_VENDOR)
        glRenderer = self.gl.glGetString(self.gl.GL_RENDERER)

        info("GL_VERSION", glVer)
        info("GL_SHADING_LANGUAGE_VERSION",glLangVer)
        info("GL_VENDOR", glVendor)
        info("GL_RENDERER", glRenderer)
        

    # Override this
    def setupGL(self):
        info("CANVAS","setupGL() is not overridden")

    # Override this
    def paintGL(self):
        info("CANVAS","setupGL() is not overridden")

    # Override this
    def resizeGL(self, width, height):
        info("CANVAS","setupGL() is not overridden")

