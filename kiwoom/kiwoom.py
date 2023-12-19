from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *



class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("Kiwwom 클래스 입니다.")
        

        
        ## 이벤트 루프 모음
        self.login_event_loop = None
        self.detail_account_info_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()
        ## ===
        
        ## 변수모음
        self.account_num = None
        self.account_stock_dic = {}
        self.not_account_stock_dic = {}
        ## ===
        
        ## 종목분석용
        self.calcul_data = []
        
        
        
        ## 계좌관련 변수
        self.use_money = 0
        self.use_money_percent = 0.5
        ## ===
        
        ## 스크린번호
        self.screen_my_info = "2000"
        self.screen_calculation_stock = "4000"
        
        
        
        self.get_ocx_instance()
        self.event_slots()
        
        self.signal_login_commConnect()
        
        self.get_account_info() ## 로그인후 계정정보 읽어오기 실행
        self.detail_account_info() ## 예수금 가지고 오기
        self.detail_account_mystock() ## 계좌평가 잔고 내역 요청
        
        ## self.not_concaluded_account() ## 미체결 요청
        ## 시간간격 주기 (5초)
        ## QTimer.singleShot(5000, self.not_concaluded_account)
        
        

        self.calculator_fnc() ## 종목분석용, 임시용으로 실행

        pass
        
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
       self.dynamicCall("CommRqData(string,string,int,string)","예수금상세현황요청","opw00001","0",self.screen_my_info)
       
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
        
        self.dynamicCall("CommRqData(string,string,int,string)","계좌평가잔고내역요청","opw00018",sPrevNext,self.screen_my_info)

        ## 이벤트 루프 호출        
        self.detail_account_info_event_loop.exec_() 
        pass ## 함수종료
        
    ## 미체결 조회
    def not_concaluded_account(self, sPrevNext="0"):
        print("미체결 잔고조회")
        self.dynamicCall("SetInputValue(string,string)","계좌번호",self.account_num)
        self.dynamicCall("SetInputValue(string,string)","체결구분","1")
        self.dynamicCall("SetInputValue(string,string)","매매구분","0")
        
        self.dynamicCall("CommRqData(string,string,int,string)","실시간미체결요청","opw10075",sPrevNext,self.screen_my_info)
        ## 이벤트 루프 호출        
        self.detail_account_info_event_loop.exec_() 
        
        pass
    
    
    
    
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
                self.detail_account_info_event_loop.exit()
                
        ## === 실기간미체결요청    
        if sRQName == "실시간미체결요청":
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)",sTrCode, sRQName)
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"종목번호")
                code = code.strip()[1:] ## 문자열 앞뒤 공백제거하고, 앞글자의 한자리 제거
                
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"종목명")
                code_nm = code_nm.strip()
                
                order_num = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"주문번호")
                order_num = order_num.strip()
                
                ## 접수->확인->체결
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"주문상태")
                order_status = order_status.strip()
            
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"주문수량")
                order_quantity = int(order_quantity.strip())
                
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"주문가격")
                order_price = order_price.strip().lstrip('+').lstrip('-')
                
                ## 매도, 매수, 정정, 취소
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"주문구분")
                order_gubun = order_gubun.strip()
                
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"미체결수량")
                not_quantity = not_quantity.strip()
                
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"체결량")
                ok_quantity = ok_quantity.strip()
                
                if order_num in self.not_account_stock_dic:
                    pass
                else:
                    self.not_account_stock_dic[order_num] = {}
                
                self.not_account_stock_dic[order_num].update({"종목코드":code})
                self.not_account_stock_dic[order_num].update({"종목명":code_nm})
                self.not_account_stock_dic[order_num].update({"주문번호":order_num})
                self.not_account_stock_dic[order_num].update({"주문상태":order_status})
                self.not_account_stock_dic[order_num].update({"주문수량":order_quantity})
                self.not_account_stock_dic[order_num].update({"주문가격":order_price})
                self.not_account_stock_dic[order_num].update({"주문구분":order_gubun})
                self.not_account_stock_dic[order_num].update({"체결량":ok_quantity})
                
                cnt += 1
                
                print("미체결 종목 : %s" % self.not_account_stock_dic[order_num])
                
            ## 데이터 수신후, 이벤트 루프 종료
            self.detail_account_info_event_loop.exit()
        
        ## 주식일봉차트조회
        if sRQName == "주식일봉차트조회":            
        
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,0,"종목코드")
            code = code.strip()
            
            print("%s 일봉데이터 요청" % code)
            
            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print("남은 일자 수 %s" % cnt)
            
            ## data = self.dynamicCall("GetCommDataEx(QString, QString)", sTrCode, sRQName)
            ## [["",현재가,거래량, 거래대금,날짜,시가,고가,저가,""] [] ]
            
            ## 한번 조회시 600일 단위로 데이터를 받을 수 있다.
            for i in range(cnt):
                data = []
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"현재가")
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"거래대금")
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"일자")
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"시가")
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"고가")
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,i,"저가")
                
                data.append("") ## 양식을 맞추기 위해서 삽입
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")
                
                self.calcul_data.append(data.copy())
                
            print(len(self.calcul_data))
                
            
            
            ## 다음페이지가 있는 경우 경우 추가 요청
            if sPrevNext == "2" :
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else :
                ## 데이터 수신이 완료된 경우, 이평선 로직 작성
                print("총 일수  %s" % len(self.calcul_data))
                pass_success = False
                
                ## 120일 이평선을 그리 만큼의 데이터가 있는지 체크
                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False
                else:
                    # 120일 이상 되면은
                    total_price = 0
                    for value in self.calcul_data[:120]:
                        total_price += int(value[1])
                    moving_average_price = total_price / 120
                    
                    # 오늘자 주가가 120일 이평선에 걸쳐 있는지 확인
                    bottom_stock_price = False
                    check_price = None
                    if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(self.calcul_data[0][6]):
                        print("오늘의 주가가 120 이평선에 걸쳐 있는지 확인")
                        bottom_stock_price = True
                        check_price = int(self.calcul_data[0][6])
                    
                    ## 과거 일봉드이 120일 이평선 보다 밑에 있는지 확인
                    ## 그렇게 확인을 하다가 일봉이 120일 이펴언 보다 위에 있으면 계산진행
                    
                    prev_price = None # 과거의 일봉 저가
                    
                    if bottom_stock_price == True:
                        
                        moving_average_price_prev= 0
                        price_top_moving = False
                        idx = 1
                        
                        
                        while True:
                            if len(self.calcul_data[idx:]) < 120: #120일치가 있는지 계속 확인
                                print("120일치가 없음!")
                                break
                            
                            total_price = 0
                            for value in self.calcul_data[idx:120+idx]:
                                total_price += int(value[1])
                                
                            moving_average_price_prev = total_price / 120
                            
                            ## 20일 정도는 이평선 아래에 유지하고 있는지 확인
                            if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <= 20 :
                                print("20일 동안 주가가 120일 이평선과 같거나 위에 있으면 조건 통과 못함")
                                price_top_moving = False
                                break
                            
                            elif int(self.calcul_data[idx][7]) > moving_average_price_prev and idx > 20:
                                print("120일 이평선 위에 있는 일봉 확인됨")
                                price_top_moving = True
                                prev_price = int(self.calcul_data[idx][7]) # 찾아낸 저가 가격을 저장함
                                break
                            
                            idx += 1
                            
                        ## 해당 부분 이평선이 가장 최근 일자의 이평선 가격보다 낮은지 확인
                        if price_top_moving == True:
                            if moving_average_price > moving_average_price_prev and check_price > prev_price :
                                print("포착된 이평선의 가격이 오늘자(최근일자) 이평선 가격보다 낮은 것 확인됨")
                                print("포착된 부분의 일봉 저가각 오늘자 일봉의 고가보다 낮은지 확인됨")
                                pass_success = True
                      
                        
                if pass_success == True:
                    print("조건부 통과됨")
                            
                    code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)
                            
                    f = open("files/condition_stock.txt", "a", encoding="utf8")
                    f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()
                elif pass_success == False:
                    print("조건부 통과 못함.xxx")
                
                self.calcul_data.clear()
                                
           
                    
                
                ## 데이터 수신후, 이벤트 루프 종료
                self.calculator_event_loop.exit()
            
            

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
    
    def stop_screen_cancel(self, sScrNo=None):
        self.dynamicCall("DisconnectRealData(QString)",sScrNo)
        
    
    ## 종목 가지고 오기
    def get_code_list_by_market(self, market_code):
        '''
        종목 코드목록 반환
        '''
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(";")[:-1]
        print(code_list)
        return code_list
    
    def calculator_fnc(self):
        code_list = self.get_code_list_by_market("10") ## 코스닥
        print("코스닥 갯수 %s" % len(code_list))
        
        
        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)
            print("%s / %s : Kosdaq Stock %s is updating" % (idx+1, len(code_list), code) )
        
            self.day_kiwoom_db(code=code)
            
        
    ## 과거 데이터 가지고 오기(tr요청)
    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        print("과거 데이터 가지고 오기")
        QTest.qWait(3600) ## 3.6초마다 지연
        
        self.dynamicCall("SetInputValue(string,string)","종목코드",code)
        self.dynamicCall("SetInputValue(string,string)","수정주가구분","1")
        
        ## 오늘 날짜가 아닌 경우에
        if date != None :            
            self.dynamicCall("SetInputValue(string,string)","기준일자",date)
        
        self.dynamicCall("CommRqData(string,string,int,string)","주식일봉차트조회","opt10081",sPrevNext,self.screen_calculation_stock)
        
        
        ## 이벤트 루프 호출        
        self.calculator_event_loop.exec_() 
        
         
        
        