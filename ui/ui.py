from kiwoom.kiwoom import *
from kiwoom.OldData import *

#from PyQt5.QtWidgets import *
import sys
from PyQt5.QtWidgets import *

class Ui_class():
    def __init__(self):
        print("ui 클래스")
                
        self.app = QApplication(sys.argv)        
        self.kiwoom = Kiwoom()
        
        
        # while True:
        #     number = input("숫자를 입력하세요: ")
        #     print(number)
            
        #     if number and int(number) == 0 :
        #         break
            
        #     if number and int(number) == 1:
        #         self.kiwoom.detail_account_info()
            
        print("kiwoom running...")
        self.app.exec_()   

