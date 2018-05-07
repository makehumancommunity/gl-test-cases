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

    def dumpGLLogMessages(self, location = None):

        currentError = self.gl.glGetError()
        while currentError != self.gl.GL_NO_ERROR:
            msg = "UNKNOWN GL ERROR"
            if currentError == self.gl.GL_INVALID_OPERATION:
                msg = "GL_INVALID_OPERATION"
            if currentError == self.gl.GL_INVALID_ENUM:
                msg = "GL_INVALID_ENUM"
            if currentError == self.gl.GL_INVALID_VALUE:
                msg = "GL_INVALID_VALUE"
            if currentError == self.gl.GL_OUT_OF_MEMORY:
                msg = "GL_OUT_OF_MEMORY"
            if currentError == self.gl.GL_INVALID_FRAMEBUFFER_OPERATION:
                msg = "GL_INVALID_FRAMEBUFFER_OPERATION"

            if location is None:
                print("\n" + msg + "!\n")
            else:
                print("\n" + msg + " at location \"" + location + "\"!\n")

            currentError = self.gl.glGetError()

        if self.glLog is None:
            return

        messages = self.glLog.loggedMessages()
        if not messages is None and len(messages) > 0:
            if location is None:
                print("\n--- LOG MESSAGES ---")
            else:
                print("\n--- " + location + " ---")
            for message in messages:
                print(message.message())                

            print("---\n")

    # Do not override this, instead override setupGL
    def initializeGL(self):

        self.glLog = QOpenGLDebugLogger(self);
        if not self.glLog.initialize():
            info("GL DEBUG LOGGER","Unable to initialize GL logging")
            self.glLog = None
        else:
            self.glLog.enableMessages(sources = QOpenGLDebugMessage.AnySource, types = QOpenGLDebugMessage.AnyType, severities = QOpenGLDebugMessage.AnySeverity)

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

        # Enable GL capabilities we need
        self.gl.glEnable(self.gl.GL_DEBUG_OUTPUT_SYNCHRONOUS);
        self.gl.glEnable(self.gl.GL_DEPTH_TEST);
        self.gl.glEnable(self.gl.GL_VERTEX_PROGRAM_POINT_SIZE)

        info("PROFILE",self.profile)
        info("FUNCTIONS",self.gl)

        self.dumpGLLogMessages("initializeGL()")

        glVer = self.gl.glGetString(self.gl.GL_VERSION)
        glLangVer = self.gl.glGetString(self.gl.GL_SHADING_LANGUAGE_VERSION)
        glVendor = self.gl.glGetString(self.gl.GL_VENDOR)
        glRenderer = self.gl.glGetString(self.gl.GL_RENDERER)

        info("GL_VERSION", glVer)
        info("GL_SHADING_LANGUAGE_VERSION",glLangVer)
        info("GL_VENDOR", glVendor)
        info("GL_RENDERER", glRenderer)

        self.setupGL()

    # Override this
    def setupGL(self):
        info("CANVAS","setupGL() is not overridden")

    # Override this
    def paintGL(self):
        info("CANVAS","setupGL() is not overridden")

    # Override this
    def resizeGL(self, width, height):
        info("CANVAS","setupGL() is not overridden")

