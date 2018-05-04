#!/usr/bin/python3

"""
This test only displays a window with a black square, which is a generic
QOpenGLWidget. GL functions have at this point not been initialized.
"""

from PyQt5.QtWidgets import QApplication, QWidget, QOpenGLWidget, QVBoxLayout
from PyQt5.QtGui import QOpenGLContext
from PyQt5.QtCore import QT_VERSION_STR

import sys

class TestApplication(QApplication):

    mainWin = None

    def __init__(self, args):
        super(TestApplication,self).__init__(args)

        print("EFFECTIVE QT VERSION : " + str(QT_VERSION_STR))

        self.mainWin = QWidget()
        self.mainWin.resize(600,600)
        self.mainWin.setWindowTitle('Minimal GL test')

        self.mainWidget = QOpenGLWidget()
        self.layout = QVBoxLayout(self.mainWin)
        self.layout.addWidget(self.mainWidget)

        self.mainWin.show()

        ctx = QOpenGLContext.currentContext()
        format = ctx.format()

        print("EFFECTIVE GL VERSION : " + str(ctx.format().version()))

app = TestApplication(sys.argv)
app.exec_()
del app

sys.exit()

