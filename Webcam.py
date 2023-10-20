from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

import sys
import cv2, imutils
import numpy as np
from datetime import datetime as dt

from CameraThread import *


from_class = uic.loadUiType("Webcam.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.isCameraOn = False
        self.isRecStart = False
        
        self.pixmap = QPixmap()
        
        self.cameraThread = CameraThread(self)
        self.cameraThread.daemon = True
        self.cameraThread.update.connect(self.showCamera)
        
        # 기본 기능
        self.btnHome.clicked.connect(self.goHome)
        self.btnCamera.clicked.connect(self.goCamera)
        self.btnGallery.clicked.connect(self.goGallery)
        self.btnPhoto.clicked.connect(self.takePic)
        self.btnSave.clicked.connect(self.savePic)
        self.btnCancel.clicked.connect(self.cancelPic)
        self.btnPlay.clicked.connect(self.playVideo)
        self.btnRec.clicked.connect(self.recVideo)
        
        # 필터
        self.btnRed.clicked.connect(self.toRed)
        self.btnGreen.clicked.connect(self.toGreen)
        self.btnBlue.clicked.connect(self.toBlue)
        self.btnGray.clicked.connect(self.toGray)
        
        self.btnInit()

    
    def toRed(self):
        print("red")
        
        
    def toGreen(self):
        print("green")
        
        
    def toBlue(self):
        print("blue")
        
        
    def toGray(self):
        self.qimage_edited = self.qimage.convertToFormat(QImage.Format_Grayscale8)
        self.pixmap_edited_org = self.pixmap.fromImage(self.qimage_edited)
        self.pixmap_edited = self.pixmap_edited_org.scaled(self.label.width(), self.label.height())
        self.label.setPixmap(self.pixmap_edited)
        
        # 저장, 취소 버튼 표출
        self.btnSave.show()  # 취소 시 원본 이미지로 돌아감
        self.btnCancel.show()  # 저장 시 현재 이미지를 저장
        
        self.mode = "editPic"
        
        
    def btnInit(self):
        # 초기화면: 카메라/갤러리 외 숨김
        self.btnCamera.show()
        self.btnGallery.show()
        self.btnHome.hide()
        self.btnPhoto.hide()
        self.btnVideo.hide()
        self.btnSave.hide()
        self.btnCancel.hide()
        self.btnRec.hide()
        self.btnPlay.hide()
        self.recLabel.hide()
        
        
    def showCamera(self):
        retval, self.image = self.video.read()
        if retval:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            
            h, w, c = self.image.shape
            self.qimage = QImage(self.image.data, w, h, w*c, QImage.Format_RGB888)
            
            self.pixmap = self.pixmap.fromImage(self.qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())
            
            self.label.setPixmap(self.pixmap)
        
        
    def stopCamera(self):
        self.isCameraOn = False
        self.cameraThread.stop()
        self.video.release()
    
    
    def goHome(self):
        self.btnInit()
        self.stopCamera()
        self.label.clear()
        
        
    def startCamera(self):
        self.isCameraOn = True
        self.cameraThread.start()
        self.video = cv2.VideoCapture(0)
        
        
    def takePic(self):
        self.stopCamera()
        
        # 비디오는 지우고 home, save, cancel만 보이게
        self.btnVideo.hide()
        self.btnSave.show()
        self.btnCancel.show()
        
        self.mode = "takePic"
        
        
    def savePic(self):
        self.now = dt.now().strftime("%Y%m%d_%H%M%S%f")
        filename = self.now + ".png"
        name = QFileDialog.getSaveFileName(self, "Save Image", "./" + filename)[0]
        
        if self.mode == "takePic":
            self.pixmap.save(name)
        else:  # self.mode == "editPic"
            self.pixmap_edited_org.save(name)
        
        
    def cancelPic(self):
        if self.mode == "takePic":
            self.label.clear()
        else:  # self.mode == "editPic"
            self.label.setPixmap(self.pixmap)
    
    
    def takeVideo(self):
        self.isRecStart = True
        self.recLabel.show()
        self.recordingStart()
            
    
    def goCamera(self):
        # 홈, 사진, 영상 버튼만 보이게
        self.btnHome.show()
        self.btnPhoto.show()
        self.btnVideo.show()
        
        self.btnCamera.hide()
        self.btnGallery.hide()
        self.btnRec.hide()
        
        self.startCamera()
        
    
    def goGallery(self):
        # 사진 또는 영상을 조회한 상태
        # 홈, 편집 버튼만 보이게
        self.btnHome.show()
        self.btnGallery.show()  # 다른 파일을 열어보고 싶을 수 있음
        
        self.btnPhoto.hide()
        self.btnVideo.hide()
        self.btnCamera.hide()
        self.btnRec.hide()
        
        # 이미지와 사진 모두 인식
        file = QFileDialog.getOpenFileName(filter="Image (*.png *.jpg *.jpeg *.avi)")[0]

        if file.lower().endswith(".avi"):  # 영상이면
            self.video = cv2.VideoCapture(file)

            if self.video.isOpened():  # VideoCapture 인스턴스 생성 확인
                self.showThumbnail()
                
        else:  # 이미지이면
            image = cv2.imread(file)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            h, w, c = image.shape
            self.qimage = QImage(image.data, w, h, w*c, QImage.Format_RGB888)

            self.pixmap = self.pixmap.fromImage(self.qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())

            self.label.setPixmap(self.pixmap)
            
            
    def showThumbnail(self):
        ret, frame = self.video.read()
        
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            self.qimage = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

            self.pixmap = QPixmap.fromImage(self.qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())
            
            self.label.setPixmap(self.pixmap)
            
        self.btnPlay.show()
                
                
    def playVideo(self):
        while True:
            ret, frame = self.video.read()
            
            if not ret:
                break
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            h, w, c = frame.shape
            bytes_per_line = 3 * w
            self.qimage = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            self.pixmap = QPixmap.fromImage(self.qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())
            
            self.label.setPixmap(self.pixmap)
            QApplication.processEvents()  # prevent GUI freeze

            time.sleep(0.05)  # 저장된 동영상에 맞게 setting

        self.video.release()
        
        
    def recVideo(self):
        if self.isRecStart == False:
            self.isRecStart = True
            self.recLabel.show()
        else:
            self.isRecStart = False
            self.recLabel.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    
    sys.exit(app.exec_())