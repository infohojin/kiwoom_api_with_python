from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("Kiwwom 클래스 입니다.")
        
        ## 이벤트 루프 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = None
        self.detail_account_info_event_loop_2 = None
        ## ===
        
        ## 변수모음
        self.account_num = None
        self.account_stock_dic = {}
        ## ===
        
        ## 계좌관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5
        ## ===
        
        
        
        

        
        self.get_ocx_instance()
        self.event_slots()
        
        self.signal_login_commConnect()
        
        self.get_account_info() ## 로그인후 계정정보 읽어오기 실행
        self.detail_account_info() ## 예수금 가지고 오기
        self.detail_account_mystock() ## 계좌평가 잔고 내역 요청
        
    ## 예수금상세현황요청
    ## opw00001
    def detail_account_info(self):
       print("예수금을 가지고옵니다.")
       ## 정보입력
       self.dynamicCall("SetInputValue(string,string)","계좌번호",self.account_num)
       self.dynamicCall("SetInputValue(string,string)","비밀번호","0000")
       self.dynamicCall("SetInputValue(string,string)","비밀번호입력매체구분","00")
       self.dynamicCall("SetInputValue(string,string)","조회구분","2") ## 일반조회
       
       ## 요청내용
       ## 내가지은요청이름, TR번호, preNext, 화면번호(아무번호)
       ## 화면번호는 TR들을 그룹으로 만들어 관리할 수 있다. (스크린번호 200 * 호출 100)
       self.dynamicCall("CommRqData(string,string,int,string)","예수금상세현황요청","opw00001","0","2000")
       
       ## 이벤트 루프 호출
       self.detail_account_info_event_loop = QEventLoop()
       self.detail_account_info_event_loop.exec_() 
       
       
       pass
   
    def detail_account_mystock(self, sPrevNext="0"):
        print("계좌평가 잔고내역 요청")
        ## 정보입력
        self.dynamicCall("SetInputValue(string,string)","계좌번호",self.account_num)
        self.dynamicCall("SetInputValue(string,string)","비밀번호","0000")
        self.dynamicCall("SetInputValue(string,string)","비밀번호입력매체구분","00")
        self.dynamicCall("SetInputValue(string,string)","조회구분","2") ## 일반조회
        
        self.dynamicCall("CommRqData(string,string,int,string)","계좌평가잔고내역요청","opw00018",sPrevNext,"2000")

        ## 이벤트 루프 호출
        self.detail_account_info_event_loop_2 = QEventLoop()
        self.detail_account_info_event_loop_2.exec_() 
    
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        '''
        tr요청을 받는 구역. 슬롯정보
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode: 요청id, ㅅㄱzhem
        :param sRecordName: 사용안함
        :param sPrevNext: 다음 페이지가 있는지
        '''
        
        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(string, string, int, string)", sTrCode, sRQName, 0, "예수금")
            print("예수금 %s" % int(deposit))
            
            self.use_money = int(deposit) * self.use_money_percent
            self.use_money = self.use_money / 4
            
            
            
            ok_deposit = self.dynamicCall("GetCommData(string, string, int, string)", sTrCode, sRQName, 0, "출금가능금액")
            print("출금가능금액 %s" % int(ok_deposit))
            
            ## 데이터 수신후, 이벤트 루프 종료
            self.detail_account_info_event_loop.exit()  
        
        ##
        if sRQName == "계좌평가잔고내역요청": 
            total_buy_money = self.dynamicCall("GetCommData(string, string, int, string)", sTrCode, sRQName, 0, "총매입금액")
            print("총매입금액: %s" % int(total_buy_money))
            
            total_profit_loss_rate = self.dynamicCall("GetCommData(string, string, int, string)", sTrCode, sRQName, 0, "총수익율(%)")
            print("총수익율(%s): %s" % ("%", total_profit_loss_rate) )

            
            
            
            ## 계좌평가
            ## 최대 20개까지 카운트, 추가 종목이 있는 경우 sPrevNext가 2로 활성화됨
            ## 종목을 다시 
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)",sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"종목번호")
                code = code.strip()[1:] ## 문자열 앞뒤 공백제거하고, 앞글자의 한자리 제거
                
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"종목명")
                code_nm = code_nm.strip()
                
                stock_quantiny = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"보유수량")
                stock_quantiny = int(stock_quantiny.strip()) ## 정수변환
                
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"매입가")
                buy_price = int(buy_price.strip())
                
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"수익율(%)")
                learn_rate = float(learn_rate.strip())
                
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"현재가")
                current_price = int(current_price.strip())
                
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"매입금액")
                total_chegual_price = int(total_chegual_price.strip())
                
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"매매가능수량")
                possible_quantity = int(possible_quantity.strip())
                
                if code in self.account_stock_dic:
                    pass
                else:
                    self.account_stock_dic.update({code:{}})
                    
                self.account_stock_dic[code].update({"종목명":code_nm})
                self.account_stock_dic[code].update({"보유수량":stock_quantity})
                self.account_stock_dic[code].update({"매입가":buy_price})
                self.account_stock_dic[code].update({"수익율(%)":learn_rate})
                self.account_stock_dic[code].update({"현재가":current_price})
                self.account_stock_dic[code].update({"매입금액":total_chegual_price})
                self.account_stock_dic[code].update({"매매가능수량":possible_quantity})
                
                cnt += 1
                ### end for
                
            print("보유중인 종목수 %s " % cnt)
            
            ## 다음페이지가 있는 경우 경우 추가 요청
            if sPrevNext == "2" :
                self.detail_account_mystock(sPrevNext)
            else :
                ## 데이터 수신후, 이벤트 루프 종료
                self.detail_account_info_event_loop_2.exit()
                
                 
                   
                    
                

                
        
        pass 
            

        
    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        
        
    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        ## Tr데이터 이벤트 연결
        self.OnReceiveTrData.connect(self.trdata_slot)
    
    def login_slot(self, errCode):
        print(errors(errCode))
    
        ## 0 일때 정상
        self.login_event_loop.exit()
        print("loop exit")
        
    def signal_login_commConnect(self):
        self.dynamicCall("commConnect()")
        
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()
        
    ## 계좌정보 가지고오기
    def get_account_info(self):
        account_list = self.dynamicCall("GETLoginInfo(String)", "ACCNO")
        account_numbers = account_list.split(';')
        
        ## 첫번째 계좌번호
        self.account_num = account_numbers[0]
        print("나의 보유 계좌번호 %s" % account_numbers[0])
        
         
        
        