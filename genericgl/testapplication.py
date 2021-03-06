#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication, QWidget, QOpenGLWidget, QHBoxLayout
from PyQt5.QtGui import QSurfaceFormat, QOpenGLContext
from PyQt5.QtCore import QT_VERSION_STR

from .simpledebug import info

import sys

class _TestApplication(QApplication):

    mainWin = None

    def __init__(self, args, glWidget = QOpenGLWidget, requestedGLVersion = (2,1)):
        super(_TestApplication,self).__init__(args)

        glType = QOpenGLContext.openGLModuleType()
    
        format = QSurfaceFormat()
        format.setDepthBufferSize(24)
    
        if glType == QOpenGLContext.LibGL:
            info("OPENGL MODULE TYPE","LibGL")
            format.setVersion(requestedGLVersion[0],requestedGLVersion[1]);
            format.setProfile(QSurfaceFormat.CompatibilityProfile);
            format.setOption(QSurfaceFormat.DebugContext);
            QSurfaceFormat.setDefaultFormat(format);
        else:
            info("OPENGL MODULE TYPE","Unknown or LibGLES  <--- this is likely to cause problems down the line")

        self.debugMembers = False

        self.mainWin = QWidget()

        if glWidget == QOpenGLWidget:
            # Only hard code size if we're not using a canvas
            self.mainWin.resize(600,600)

        self.mainWin.setWindowTitle('TestApplication')

        self.mainWidget = glWidget()

        self.layout = QHBoxLayout(self.mainWin)
        self.layout.addWidget(self.mainWidget)

        self.mainWin.show()

        ctx = QOpenGLContext.currentContext()
        info("GL CURRENT CONTEXT",ctx)

        format = ctx.format()

        info("EFFECTIVE GL VERSION",ctx.format().version())

        self.aboutToQuit.connect(self.applicationClosing)

    def applicationClosing(self, *args):

        info("APPLICATION","about to be destroyed")

        if not self.mainWidget is None and hasattr(self.mainWidget, "_on_destroyed"):
            self.mainWidget._on_destroyed()


def TestApplication(args, glWidgetClass = QOpenGLWidget, requestedGLVersion = (2,1)):

    info("EFFECTIVE QT VERSION",QT_VERSION_STR)
    info("REQUESTED GL VERSION",requestedGLVersion)

    app = _TestApplication(args, glWidgetClass, requestedGLVersion)
    app.exec_()
    del app
    sys.exit()


