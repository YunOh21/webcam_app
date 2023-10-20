from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

import sys
import time


class CameraThread(QThread):
    update = pyqtSignal()
    
    def __init__(self, sec=0, parent=None):
        super().__init__()
        self.main = parent
        self.running = True
        
    def run(self):
        if self.running == False:
            self.running = True
        while self.running:
            self.update.emit()
            time.sleep(0.05)
            
    def stop(self):
        self.running = False