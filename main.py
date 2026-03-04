from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
import cv2
import sys
import matplotlib.pyplot as plt

qtcreator_file = "design.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)

class DesignWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(DesignWindow, self).__init__()
        self.setupUi(self)

        self.img = None
        self.gray_img = None


        self.BrowseBtn.clicked.connect(self.get_image)
        self.DisplayRedChan.clicked.connect(self.showRedChannel)
        self.DisplayGreenChan.clicked.connect(self.showGreenChannel)
        self.DisplayBlueChan_2.clicked.connect(self.showBlueChannel)
        self.DisplayColorHist.clicked.connect(self.show_HistColor)
        self.DisplayGrayImg.clicked.connect(self.show_UpdatedImgGray)
        self.DisplayGrayHist.clicked.connect(self.show_HistGray)


    def convert_cv_qt(self, cv_image):
        if cv_image is None:
            return QPixmap()
        h, w = cv_image.shape[:2]
        ch = 1 if len(cv_image.shape) == 2 else cv_image.shape[2]
        bytes_per_line = ch * w
        if ch == 1:
            qt_image = QtGui.QImage(cv_image.data, w, h, bytes_per_line, QtGui.QImage.Format_Grayscale8)
        else:
            qt_image = QtGui.QImage(cv_image.data, w, h, bytes_per_line, QtGui.QImage.Format_BGR888)
        return QPixmap.fromImage(qt_image)

    def showDimensions(self):
        if self.img is not None:
            h, w, ch = self.img.shape
            self.Dimensions.setText(f"Hauteur: {h}\nLargeur: {w}\nCanaux: {ch}")


    def get_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg)"
        )

        if file_path:
            self.img = cv2.imread(file_path)
            pixmap = self.convert_cv_qt(self.img)
            pixmap = pixmap.scaled(self.OriginalImg.width(), self.OriginalImg.height(), QtCore.Qt.KeepAspectRatio)
            self.OriginalImg.setPixmap(pixmap)
            self.showDimensions()


    def showRedChannel(self):
        if self.img is not None:
            red = self.img.copy()
            red[:, :, 0] = 0
            red[:, :, 1] = 0
            pixmap = self.convert_cv_qt(red)
            pixmap = pixmap.scaled(self.RedChannel.width(), self.RedChannel.height(), QtCore.Qt.KeepAspectRatioByExpanding)
            self.RedChannel.setPixmap(pixmap)

    def showGreenChannel(self):
        if self.img is not None:
            green = self.img.copy()
            green[:, :, 0] = 0
            green[:, :, 2] = 0
            pixmap = self.convert_cv_qt(green)
            pixmap = pixmap.scaled(self.GreenChannel.width(), self.GreenChannel.height(), QtCore.Qt.KeepAspectRatioByExpanding)
            self.GreenChannel.setPixmap(pixmap)

    def showBlueChannel(self):
        if self.img is not None:
            blue = self.img.copy()
            blue[:, :, 1] = 0
            blue[:, :, 2] = 0
            pixmap = self.convert_cv_qt(blue)
            pixmap = pixmap.scaled(self.BlueChannel.width(), self.BlueChannel.height(), QtCore.Qt.KeepAspectRatioByExpanding)
            self.BlueChannel.setPixmap(pixmap)


    def show_HistColor(self):
        if self.img is not None:
            colors = ('b', 'g', 'r')
            plt.figure(figsize=(4, 2))
            for i, col in enumerate(colors):
                hist = cv2.calcHist([self.img], [i], None, [256], [0, 256])
                plt.plot(hist, color=col)
                plt.xlim([0, 256])
            plt.title("Histogramme Couleur")
            plt.tight_layout()
            plt.savefig("Color_Histogram.png")
            plt.close()
            pixmap = QPixmap("Color_Histogram.png")
            pixmap = pixmap.scaled(self.ColorHist.width(), self.ColorHist.height(), QtCore.Qt.KeepAspectRatio)
            self.ColorHist.setPixmap(pixmap)


    def getContrast(self):
        try:
            text = self.Contrast.toPlainText()
            return max(0.0, float(text)) if text else 1.0
        except ValueError:
            return 1.0

    def getBrightness(self):
        try:
            text = self.Brightness.toPlainText()
            return float(text) if text else 0.0
        except ValueError:
            return 0.0

    def show_UpdatedImgGray(self):
        if self.img is not None:
            self.gray_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            alpha = self.getContrast()
            beta = self.getBrightness()
            updated = cv2.convertScaleAbs(self.gray_img, alpha=alpha, beta=beta)
            pixmap = self.convert_cv_qt(updated)
            pixmap = pixmap.scaled(self.GrayImg.width(), self.GrayImg.height(), QtCore.Qt.KeepAspectRatio)
            self.GrayImg.setPixmap(pixmap)

    def show_HistGray(self):
        if self.img is None:
            return
        if self.gray_img is None:
            self.gray_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        alpha = self.getContrast()
        beta = self.getBrightness()
        updated = cv2.convertScaleAbs(self.gray_img, alpha=alpha, beta=beta)

        hist = cv2.calcHist([updated], [0], None, [256], [0, 256])
        plt.figure(figsize=(4, 2))
        plt.plot(hist, color='k')
        plt.xlim([0, 256])
        plt.title("Histogramme Gris")
        plt.tight_layout()
        plt.savefig("Gray_Histogram.png")
        plt.close()

        pixmap = QPixmap("Gray_Histogram.png")
        pixmap = pixmap.scaled(self.GrayHist.width(), self.GrayHist.height(), QtCore.Qt.KeepAspectRatio)
        self.GrayHist.setPixmap(pixmap)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DesignWindow()
    window.show()
    sys.exit(app.exec_())
