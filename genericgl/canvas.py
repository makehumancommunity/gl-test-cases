#/usr/bin/python3

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Canvas(QOpenGLWidget):

    def __init__(self, parent=None, app=None, requestedVersion=(2,0)):

        self.app = app
        self.requestedVersion = requestedVersion

        super(Canvas, self).__init__(parent)

    # Override if necessary
    def minimumSizeHint(self):
        print("Canvas minimumSizeHint")
        return QSize(50, 50)

    # Override if necessary
    def sizeHint(self):
        print("Canvas sizeHint")
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

        print("PROFILE              : " + str(self.profile))
        print("FUNCTIONS            : " + str(self.gl))

        self.setupGL()

        print("GL_SHADING_LANG..    : " + str(self.gl.GL_SHADING_LANGUAGE_VERSION))
        

    # Override this
    def setupGL(self):
        print("WARNING: Running the generic setupGL. You probably wanted to override this.")

    # Override this
    def paintGL(self):
        print("WARNING: Running the generic paintGL. You probably wanted to override this.")

    # Override this
    def resizeGL(self, width, height):
        print("WARNING: Running the generic resizeGL. You probably wanted to override this.")

