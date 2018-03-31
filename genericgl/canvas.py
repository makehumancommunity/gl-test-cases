#/usr/bin/python3

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Canvas(QOpenGLWidget):

    def __init__(self, parent=None, app=None):

        print("\n\nINITIALIZATION OF GL CANVAS STARTS HERE\n\n")
        self.app = app

        super(Canvas, self).__init__(parent)

    # Override if necessary
    def minimumSizeHint(self):
        return QSize(50, 50)

    # Override if necessary
    def sizeHint(self):
        return QSize(600, 600)

    # Do not override this, instead override setupGL
    def initializeGL(self):
        self.profile = QOpenGLVersionProfile()
        self.profile.setVersion(2,0)
        self.gl = self.context().versionFunctions(self.profile)
        self.gl.initializeOpenGLFunctions()

        print("------")
        print("PROFILE   : " + str(self.profile))
        print("FUNCTIONS : " + str(self.gl))
        print("------\n")

        self.setupGL()

        print("\n\nAT THIS POINT THE GL CONTEXT SHOULD BE FULLY SET UP\n\n")

    # Override this
    def setupGL(self):
        print("WARNING: Running the generic setupGL. You probably wanted to override this.")

    # Override this
    def paintGL(self):
        print("WARNING: Running the generic paintGL. You probably wanted to override this.")

    # Override this
    def resizeGL(self, width, height):
        print("WARNING: Running the generic resizeGL. You probably wanted to override this.")

