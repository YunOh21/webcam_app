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
        
        # 카메라 보이기
        self.cameraThread = CameraThread(self)
        self.cameraThread.daemon = True
        self.cameraThread.update.connect(self.showCamera)
        
        # 영상 촬영
        self.recordThread = CameraThread(self)
        self.recordThread.daemon = True
        self.recordThread.update.connect(self.updateRecording)
        
        # 기본 기능
        self.btnHome.clicked.connect(self.goHome)
        self.btnCamera.clicked.connect(self.goCamera)
        self.btnGallery.clicked.connect(self.goGallery)
        self.btnPhoto.clicked.connect(self.takePic)
        self.btnRec.clicked.connect(self.takeVideo)
        
        self.btnSaveAs.clicked.connect(self.savePicAs)
        self.btnSave.clicked.connect(self.savePic)
        self.btnCancel.clicked.connect(self.cancelPic)
        
        self.btnPlayControl.clicked.connect(self.controlVideo)
        
        # 필터
        self.btnRed.clicked.connect(self.toRed)  # to do
        self.btnGreen.clicked.connect(self.toGreen)  # to do
        self.btnBlue.clicked.connect(self.toBlue)  # to do
        self.btnGray.clicked.connect(self.toGray)
        
        self.btnInit()
        self.editEnabled(False)  # 편집 기능은 사진이나 영상이 있을 때 활성화
        
        
    def editEnabled(self, bool):
        # 현재 구현되지 않은 버튼은 비활성화
        self.btnRed.setEnabled(False)
        self.btnGreen.setEnabled(False)
        self.btnBlue.setEnabled(False)
        self.btnGray.setEnabled(bool)
        self.btnBinary.setEnabled(False)
        self.btnBlur.setEnabled(False)
        self.btnCanny.setEnabled(False)
        self.btnDraw.setEnabled(False)
        self.btnCutPhoto.setEnabled(False)
        self.btnScan.setEnabled(False)
        self.btnCutVideo.setEnabled(False)

    
    def toRed(self):
        print("red")
        
        
    def toGreen(self):
        print("green")
        
        
    def toBlue(self):
        print("blue")
        
        
    def toGray(self):
        self.qimage_edited = self.qimage.convertToFormat(QImage.Format_Grayscale16)
        self.pixmap_edited_org = self.pixmap.fromImage(self.qimage_edited)
        self.pixmap_edited = self.pixmap_edited_org.scaled(self.label.width(), self.label.height())
        self.label.setPixmap(self.pixmap_edited)
        
        # 저장, 취소 버튼 표출
        self.btnSaveAs.show()  # 저장 시 현재 이미지를 새 파일로 저장(단, 사이즈 변형은 x)
        self.btnSave.show()  # 저장 시 기존 파일을 현재 이미지로 변경(단, 사이즈 변형은 x)
        self.btnCancel.show()  # 취소 시 원본 이미지로 돌아감
        
        self.mode = "editPic"
        
        
    def btnInit(self):
        # 초기화면: 카메라/갤러리 외 숨김
        self.btnCamera.show()
        self.btnGallery.show()
        self.btnHome.hide()
        self.btnPhoto.hide()
        self.btnRec.hide()
        self.btnSaveAs.hide()
        self.btnSave.hide()
        self.btnCancel.hide()
        self.btnPlayControl.hide()
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
        if self.isCameraOn:
            self.stopCamera()
        self.label.clear()
        
        
    def startCamera(self):
        self.isCameraOn = True
        self.cameraThread.start()
        self.video = cv2.VideoCapture(0)
        
        
    def takePic(self):
        self.stopCamera()
        
        # 비디오는 지우고 home, save, cancel만 보이게
        self.btnRec.hide()
        self.btnSave.show()
        self.btnCancel.show()
        
        self.mode = "takePic"
        
        
    def savePic(self):
        if self.mode == "takePic":
            self.now = dt.now().strftime("%Y%m%d_%H%M%S%f")
            filename = self.now + ".png"
            name = QFileDialog.getSaveFileName(self, "Save Image", "./" + filename)[0]
            self.pixmap.save(name)
        else:  # self.mode == "editPic"
            self.pixmap_edited_org.save(self.file)  # 원본 파일 덮어쓰기
            
            
    def savePicAs(self):
        self.now = dt.now().strftime("%Y%m%d_%H%M%S%f")
        filename = self.now + ".png"
        name = QFileDialog.getSaveFileName(self, "Save Image", "./" + filename)[0]

        self.pixmap_edited_org.save(name)
        
        
    def cancelPic(self):
        if self.mode == "takePic":
            self.label.clear()
            # 사진 저장/취소 버튼 안 보이게 하기
            self.btnSave.hide()
            self.btnCancel.hide()
            self.btnRec.show()
            
            # 카메라 재시작
            self.startCamera()
        else:  # self.mode == "editPic"
            self.label.setPixmap(self.pixmap)
            
    
    def goCamera(self):
        # 홈, 사진, 영상 버튼만 보이게
        self.btnHome.show()
        self.btnPhoto.show()
        self.btnRec.show()
        
        self.btnCamera.hide()
        self.btnGallery.hide()
        
        self.startCamera()
        
    
    def goGallery(self):
        # 사진 또는 영상을 조회한 상태
        # 홈, 편집 버튼만 보이게
        self.btnHome.show()
        self.btnGallery.show()  # 다른 파일을 열어보고 싶을 수 있음
        
        self.btnPhoto.hide()
        self.btnRec.hide()
        self.btnCamera.hide()
        
        # 이미지와 사진 모두 인식
        self.file = QFileDialog.getOpenFileName(filter="Image (*.png *.jpg *.jpeg *.avi)")[0]
        
        if self.file != '':  # 선택 없이 창 닫을 경우 아래 동작x
            self.editEnabled(True)
            if self.file.lower().endswith(".avi"):  # 영상이면
                self.video = cv2.VideoCapture(self.file)

                if self.video.isOpened():  # VideoCapture 인스턴스 생성 확인
                    self.showThumbnail()
                    
            else:  # 이미지이면
                self.btnPlayControl.hide()
                
                image = cv2.imread(self.file)
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
            
            h, w, c = frame.shape
            bytes_per_line = 3 * w
            self.qimage = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            self.pixmap = QPixmap.fromImage(self.qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())
            
            self.label.setPixmap(self.pixmap)
            
        self.btnPlayControl.show()
        self.btnPlayControl.setText("▶") 
                
                
    def controlVideo(self):
        if self.btnPlayControl.text() == "▶":
            self.playVideo()
        else:
            self.pauseVideo()
    
    
    def playVideo(self):
        self.isVideoEnd = False
        self.btnPlayControl.setText("❚❚")  # to-do: 일시정지
        
        while self.isVideoEnd == False:
            ret, frame = self.video.read()
            
            if not ret:
                self.isVideoEnd = True
                self.btnPlayControl.setText("▶")
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
        
        
    def pauseVideo(self):
        self.isVideoEnd = True
        self.btnPlayControl.setText("▶")
    
    # 영상 촬영
    def recordingStart(self):
        self.btnRec.setText("REC OFF")
        
        self.isRecStart = True
        self.recordThread.running = True
        self.recordThread.start()
        
        self.now = dt.now().strftime("%Y%m%d_%H%M%S")
        filename = self.now + ".avi"
        self.fourcc = cv2.VideoWriter_fourcc(*"XVID")
        
        w = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.writer = cv2.VideoWriter(filename, self.fourcc, 20.0, (w, h))
        
        self.isRecLabelOn = True
        self.recLabelTime = 0
        
        
    def recordingStop(self):
        self.btnRec.setText("REC ON")
        self.recLabel.hide()
        self.recordThread.running = False
        self.isRecStart = False
        self.writer.release()
        
        
    def takeVideo(self):
        if self.isRecStart == False:
            self.recordingStart()
        else:
            self.recordingStop()
        
        
    def updateRecording(self):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.writer.write(self.image)
        
        self.recLabelTime += 1
        
        # recordThread가 실행되는 동안 REC 문구 깜빡깜빡
        if self.recLabelTime == 5 and self.isRecLabelOn:
            self.recLabelTime = 0
            self.isRecLabelOn = False
            self.recLabel.show()
        elif self.recLabelTime == 5 and self.isRecLabelOn == False:
            self.recLabelTime = 0
            self.isRecLabelOn = True
            self.recLabel.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    
    sys.exit(app.exec_())