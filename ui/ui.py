from kiwoom.kiwoom import *

#from PyQt5.QtWidgets import *
import sys
from PyQt5.QtWidgets import *

class Ui_class():
    def __init__(self):
        print("ui 클래스")
        
        self.app = QApplication(sys.argv)        
        self.kiwoom = Kiwoom()
        
        self.app.exec_()       
