from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("Kiwwom 클래스 입니다.")
        
        ## 이벤트 루프 모음
        self.login_event_loop = None
        ## ===
        
        self.get_ocx_instance()
        self.event_slots()
        self.signal_login_commConnect()
        
        
    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        
        
    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
    
    def login_slot(self, errCode):
        print(errors(errCode))
        
        
        ## 0 일때 정상
        self.login_event_loop.exit()
        
    def signal_login_commConnect(self):
        self.dynamicCall("commConnect()")
        
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()
        
         
        
        