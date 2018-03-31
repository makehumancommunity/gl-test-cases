#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication, QWidget, QOpenGLWidget, QVBoxLayout

class TestApplication(QApplication):

    mainWin = None

    def __init__(self, args, glWidget = QOpenGLWidget ):
        super(TestApplication,self).__init__(args)

        self.mainWin = QWidget()
        self.mainWin.resize(600,600)
        self.mainWin.setWindowTitle('TestApplication')

        self.mainWidget = glWidget()

        self.layout = QVBoxLayout(self.mainWin)
        self.layout.addWidget(self.mainWidget)

        self.mainWin.show()


