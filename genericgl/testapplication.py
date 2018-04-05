#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication, QWidget, QOpenGLWidget, QVBoxLayout
from PyQt5.QtGui import QSurfaceFormat, QOpenGLContext
from PyQt5.QtCore import QT_VERSION_STR

import sys

class _TestApplication(QApplication):

    mainWin = None

    def __init__(self, args, glWidget = QOpenGLWidget):
        super(_TestApplication,self).__init__(args)

        self.debugMembers = False

        self.mainWin = QWidget()
        self.mainWin.resize(600,600)
        self.mainWin.setWindowTitle('TestApplication')

        self.mainWidget = glWidget()

        self.layout = QVBoxLayout(self.mainWin)
        self.layout.addWidget(self.mainWidget)

        self.mainWin.show()

        ctx = QOpenGLContext.currentContext()
        print("GL CURRENT CONTEXT   : " + str(ctx))

        format = ctx.format()

        print("EFFECTIVE GL VERSION : " + str(ctx.format().version()))


def TestApplication(args, glWidgetClass = QOpenGLWidget, requestedGLVersion = (2,0)):

    print("EFFECTIVE QT VERSION : " + str(QT_VERSION_STR))
    print("REQUESTED GL VERSION : " + str(requestedGLVersion))

    glType = QOpenGLContext.openGLModuleType()

    format = QSurfaceFormat()
    format.setDepthBufferSize(24)

    if glType == QOpenGLContext.LibGL:
        print("OPENGL MODULE TYPE   : LibGL")
        format.setVersion(requestedGLVersion[0],requestedGLVersion[1]);
        format.setProfile(QSurfaceFormat.CompatibilityProfile);
    else:
        print("OPENGL MODULE TYPE   : LibGLES")
        format.setVersion(2,0);

    QSurfaceFormat.setDefaultFormat(format);

    app = _TestApplication(args, glWidgetClass)
    app.exec_()
    del app
    sys.exit()


