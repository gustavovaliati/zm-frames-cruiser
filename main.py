from PyQt5.QtWidgets import (QMainWindow, QWidget, QAction, QFileDialog, QApplication, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QShortcut, QSpinBox, QFrame)
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5 import QtCore

import sys, glob, os, argparse

class ControlsWidget(QWidget):
    def __init__(self, parent):
        super(ControlsWidget, self).__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout(self)



        nextImageBtn = QPushButton('Next >>', self)
        nextImageBtn.setToolTip('Jump to the next frame.')
        nextImageBtn.clicked.connect(self.parent.nextImage)

        previousImageBtn = QPushButton('<< Previous', self)
        previousImageBtn.setToolTip('Jump to the previous frame.')
        previousImageBtn.clicked.connect(self.parent.previousImage)

        gotToBtn = QPushButton('Go to', self)
        gotToBtn.setToolTip('Jump to the specified frame.')
        gotToBtn.clicked.connect(self.goToAction)

        hLine = QFrame()
        hLine.setFrameShape(QFrame.HLine)
        hLine.setFrameShadow(QFrame.Sunken)

        self.operatorSpin = QSpinBox(self)
        self.operatorSpin.setToolTip('The number of frames to pass through on a single jump.')
        self.operatorSpin.setMinimum(1)
        self.operatorSpin.setMaximum(1000)

        self.gotToSpin = QSpinBox(self)
        self.gotToSpin.setToolTip('The frame to jump in.')

        vbox.addWidget(self.operatorSpin)
        vbox.addWidget(nextImageBtn)
        vbox.addWidget(previousImageBtn)
        vbox.addWidget(hLine)
        vbox.addWidget(self.gotToSpin)
        vbox.addWidget(gotToBtn)
        vbox.addStretch()

        self.setLayout(vbox)

    def goToAction(self):
        self.parent.goToImage(self.gotToSpin.value() - 1)

class ImageWidget(QWidget):
    def __init__(self, parent):
        super(ImageWidget, self).__init__(parent)
        self.parent = parent
        self.imageIndex = -1
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout(self)
        self.pixmap = QPixmap()
        self.controlsWidget = ControlsWidget(self)

        self.lbl = QLabel(self)
        self.lbl.setPixmap(self.pixmap)

        hbox.addWidget(self.lbl)
        hbox.addWidget(self.controlsWidget)

        self.setLayout(hbox)

    def loadImage(self, index):
        self.pixmap.load(self.imageList[index])
        self.lbl.setPixmap(self.pixmap)
        statusBarMessage = '[{}/{}] {}'.format(index+1, self.imageListLength, self.imageList[index])
        self.parent.statusBar().showMessage(statusBarMessage)

    def goToImage(self, localIndex):
        if localIndex >= 0 and localIndex < self.imageListLength:
            self.loadImage(localIndex)
            self.imageIndex = localIndex

    def slideToImage(self, operator):
        localIndex = self.imageIndex + operator
        self.goToImage(localIndex)

    def nextImage(self):
        self.slideToImage(self.controlsWidget.operatorSpin.value())

    def previousImage(self):
        self.slideToImage(self.controlsWidget.operatorSpin.value() * -1)

    def setImageList(self, imageList):
        self.imageList = imageList
        self.imageList.sort()
        self.imageListLength = len(self.imageList)
        print("Found {} jpg images.".format(self.imageListLength))
        self.controlsWidget.gotToSpin.setMinimum(1)
        self.controlsWidget.gotToSpin.setMaximum(self.imageListLength)
        self.goToImage(0)

class MainWindow(QMainWindow):

    def __init__(self, workdir):
        super().__init__()

        self.workdir = workdir
        self.initUI()

        nextImageShortcut = QShortcut(QKeySequence("Right"),self, self.mainWidget.nextImage)
        prevImageShortcut = QShortcut(QKeySequence("Left"),self, self.mainWidget.previousImage)

    def initUI(self):
        self.statusBar()

        openFile = QAction('Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)

        self.mainWidget = ImageWidget(self)
        self.setCentralWidget(self.mainWidget)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('ZM Frame Cruiser')
        self.show()

        if self.workdir:
            self.loadImageList()

    def showDialog(self):
        self.workdir = QFileDialog.getExistingDirectory(self, 'Open directory', '/home', QFileDialog.ShowDirsOnly)
        print("Selected working dir: {}".format(self.workdir))
        self.loadImageList()

    def loadImageList(self):
        imageList = glob.glob(os.path.join(self.workdir, '**/*.jpg'), recursive=True)
        self.mainWidget.setImageList(imageList)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--directory",
                    required = False,
                    default = False,
                    help = "The directory containing the images.",
                    dest='workdir')
    args = vars(ap.parse_args())

    app = QApplication(sys.argv)
    ex = MainWindow(args['workdir'])
    sys.exit(app.exec_())
