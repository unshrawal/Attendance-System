import sys
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
import cv2
import numpy as np
from functools import partial
from ui_mainwindow import Ui_MainWindow
from helper import Verdict
import xlsxwriter
import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.Worker1 = Worker1()
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.ui.pushButton.clicked.connect(self.buttonPress)
        self.ui.pushButton_2.clicked.connect(self.train)
        self.ui.pushButton_3.clicked.connect(self.onClearExcel)
        self.ui.pushButton_4.clicked.connect(self.exportExcel)

        self.workbook = xlsxwriter.Workbook('Attendance.xlsx')
        self.worksheet = self.workbook.add_worksheet()
        """
        action = QAction("Start recording", self)
        action.triggered.connect(self.onStartRecording)
        self.ui.menubar.addAction(action)
        """
        self.unique_names = set()
        self.trainingPic = None
        self.w = None
        self.curNames = []
        self.currentRow = 0
    def ImageUpdateSlot(self, Image, basicImage, names):
        if len(names) != 1:
            self.ui.pushButton.setDisabled(True)
        else:
            self.ui.pushButton.setDisabled(False)

        
        current_time = datetime.datetime.now()
        time_string = current_time.strftime('%H:%M:%S')

        for i in names:
            if i not in self.unique_names:
                self.unique_names.add(i)
                self.worksheet.write_row(self.currentRow, 0, (i, time_string))
                self.currentRow += 1

        self.ui.label.setPixmap(QPixmap.fromImage(Image))
        self.currentImage = basicImage
    def CancelFeed(self):
        self.Worker1.stop()
    def buttonPress(self):
        self.trainingPics = self.currentImage
    def train(self):
        if self.w is None:
            self.w = AnotherWindow(self.trainingPic)
            self.w.show()
    def onClearExcel(self):
        self.unique_names = set()
        for row in range(self.worksheet.dim_rowmax):
            for col in range(self.worksheet.dim_colmax):
                self.worksheet.write(row, col, "")
    def exportExcel(self):
        self.workbook.close()

class Worker1(QThread):
    ImageUpdate = Signal(QImage, QImage, list)
    def run(self):
        self.ThreadActive = True
        Capture = cv2.VideoCapture(0)
        while self.ThreadActive:
            ret, frame = Capture.read()
            if ret:
                process = v.process(frame.copy())
                newFrame = process[0]
                locs = process[2]
                names = process[1]
                Image = cv2.cvtColor(newFrame, cv2.COLOR_BGR2RGB)
                ConvertToQtFormat = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(781, 581, Qt.KeepAspectRatio)
                basicImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                basicConvertToQtFormat = QImage(basicImage.data, basicImage.shape[1], basicImage.shape[0], QImage.Format_RGB888)
                basicPic = basicConvertToQtFormat.scaled(781, 581, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic, basicPic, names)
    def stop(self):
        self.ThreadActive = False
        self.quit()

class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, trainingPic):
        super().__init__()
        layout = QVBoxLayout()
        self.pixmap = QPixmap(trainingPic)
        self.label2 = QLabel(self)
        self.label2.setPixmap(self.pixmap)
        self.label2.resize(self.pixmap.width(), self.pixmap.height())
        self.textBox = QLineEdit(self)
        self.button = QPushButton("Submit", self)
        self.button.clicked.connect(partial(v.store, trainingPic, self.textBox))
        self.button.clicked.connect(lambda:self.close())
        layout.addWidget(self.label2)
        layout.addWidget(self.textBox)
        layout.addWidget(self.button)
        self.setLayout(layout)

if __name__ == "__main__":
    v = Verdict()
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())