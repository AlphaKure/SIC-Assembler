class assembler:
    '''
    參數:
        locationList:存各指令在記憶體位置
        programName:存程式名稱
        startLocation:存程式起始位置
        symbolTable:存本程式所有指令名稱
        machineCode:存本程式所有指令機器碼
        opcodeTable:存opcode值dict
        inputFile:來源檔案位址
        locFile:輸出loc.txt位置
        outputFile:輸出output.txt位置
        objectcodeFile:輸出objectcode.txt位置
    方法:
        calHex:處理16進制轉換等功能
        memoryLocationCal:計算各指令占用記憶體大小
        machineCodeGenerator:處理指令轉機器碼
        createObjectProgram:處理並生成objectcode.txt
        process:主執行程式
    '''
    
    def __init__(self,inputFile:str,outputFile='./output.txt',locFile='./loc.txt',objectcodeFile='./objectcode.txt') -> None:
        '''
            inputFile:來源檔案位址(必填!!!!)
            locFile:輸出loc.txt位置
            outputFile:輸出output.txt位置
            objectcodeFile:輸出objectcode.txt位置
        '''
        
        self.locationList=list()
        self.programName=""
        self.startLocation=""
        self.symbolTable=dict()
        self.machineCode=list()
        self.opcodeTable={"ADD":"18","AND":"40","COMP":"28","DIV":"24","J":"3C","JEQ":"30","JGT":"34","JLT":"38","JSUB":"48","LDA":"00","LDCH":"50","LDL":"08","LDX":"04","MUL":"20","OR":"44","RD":"D8","RSUB":"4C","STA":"0C","STCH":"54","STL":"14","STSW":"E8","STX":"10","SUB":"1C","TD":"E0","TIX":"2C","WD":"DC"}
        self.inputFile=open(inputFile,'r',encoding='utf-8')
        self.outputFile=open(outputFile,'w',encoding='utf-8')
        self.locFile=open(locFile,'w',encoding='utf-8')
        self.objectcodeFile=open(objectcodeFile,'w',encoding='utf-8')
    
    def calHex(self,strHex:str=None,intDec:int=None,bits:int=4)->str:
        '''
        輸入參數:
            1.strHex:16進制字串，預設為None
            2.intDec:10進制整數，預設為None
            3.bits:轉出位元數，預設為4
        輸出:
            你所設定的幾bits16進制字串
            ex: strHex=1,bits=4 ->'0001'
        功能:
            1.只輸入strHex和bits:
                >執行擴充位元
            2.輸入strHex和intDec(bits選填):
                >執行16進制加法
            3.只輸入intDec(bits選填):
                >執行10進制轉16進制
        '''

        if strHex!=None: 
            if intDec!=None:
                # 16進制+10進制
                return self.calHex(intDec=(int(strHex,16)+intDec),bits=bits)
            else:
                # 擴充位元
                while len(strHex)<bits:
                    strHex='0'+strHex
                return strHex.upper()
        if intDec!=None:
            # 10進制轉16進制
            temp=hex(intDec)[2:] # 拔除基底
            while len(temp)<bits:
                temp='0'+temp
            return temp.upper()
        
    def memoryLocationCal(self,chunk:list[str])->int:
        '''
        輸入:
            chunk:每行組合語言指令
        輸出:
            其指令大小
            ex: chunk=['AAA','RESB','69'] -> 69 
        '''

        if chunk[1]=='RESW': # RESW需留大小*3
            return int(chunk[2])*3
        elif chunk[1]=='RESB':
            return int(chunk[2]) # RESB需留大小*1
        elif chunk[1]=='BYTE':
            if chunk[2].startswith('C'): # BYTE中C為char 需佔用C''內字元數*2(ASCII)
                return len(chunk[2].split("'")[1])
            elif chunk[2].startswith('X'): # BYTE中X為Hex 需佔用X''內值字元數*1
                return int(len(chunk[2].split("'")[1])/2)
        else:
            return 3 # 其他指令皆佔3位元(START END等不佔空間指令會在其他程式中忽略)

    def machineCodeGenerator(self,chunk:list[str])->str:
        '''
        輸入:
            chunk:每行組合語言指令
        輸出:
             輸出每行組語轉機器碼
        '''

        nullObjectList={'START','END','RESW','RESB'} # 沒有機器碼的指令 輸出空字串
        if chunk[0]!='.': #非註解行
            if chunk[1] in nullObjectList: 
                return ''
            else:
                if chunk[1]!='BYTE' and chunk[1]!='WORD': 
                    # case1: 非BYTE非WORD
                    if len(chunk)==2: 
                        # 沒有TargetAddress
                        return self.opcodeTable[chunk[1]]+'0000'
                    elif chunk[2] and not chunk[2].endswith(',X'):
                        # 不使用索引定值
                        return self.opcodeTable[chunk[1]]+self.symbolTable[chunk[2]] 
                    else:
                        # 使用索引定值，即TA,X
                        temp=self.calHex(strHex=self.opcodeTable[chunk[1]]+self.symbolTable[chunk[2].split(',')[0]],intDec=32768,bits=6)
                        return temp
                else:
                    if chunk[1]=='WORD':
                        # case2: WORD
                        return self.calHex(strHex=hex(int(chunk[2]))[2:],bits=6)
                    elif chunk[1]=='BYTE' and chunk[2].startswith('C'):
                        # case3: BYTE 內容為char
                        asc=[hex(ord(char))[2:] for char in chunk[2].split("'")[1]] #轉ASCII 1.先拉出每個字元 2.用ord()將各字元轉ascii數值 3. 將數值轉為16進制
                        temp=""
                        for code in asc:
                            temp=temp+code
                        return temp.upper()
                    elif chunk[1]=='BYTE' and chunk[2].startswith('X'):
                        # case4: BYTE 內容為hex
                        return chunk[2].split("'")[1].upper()
        else: # 註解行 不執行轉換
            return None
        
    def createObjectProgram(self)->None:
        '''
        功能:
            處理並生成objectcode.txt
        '''
        while len(self.programName)<6: # 擴充程式名稱
            self.programName=self.programName+' '
        self.objectcodeFile.write(f'H{self.programName}{self.startLocation}{self.calHex(intDec=int(self.locationList[-1],16)-int(self.startLocation,16),bits=6)}\n')
        temp=''
        iter=0
        jumpFlag=False
        firstLocation=self.calHex(strHex=self.startLocation,bits=6)
        for location in self.locationList: 
            if iter!=len(self.locationList)-1:
                if (int(self.locationList[iter+1],16)-int(location,16))>4:
                    # 下一指令位址距離>4 
                    jumpFlag=True
            if self.machineCode[iter]!='' and self.machineCode[iter]!=None:
                if iter!=len(self.locationList)-1: # 不是最後一筆且objectCode不是空或空字串(即指令不是註解或START END RESW RESB)
                    temp=temp+self.machineCode[iter] # 把機器碼push進暫存
            if len(temp)>54 or (iter==len(self.locationList)-1 and temp!='')or jumpFlag:
                # 如果暫存長度>54 或 iter指到最後一筆且暫存不為空 或 指令位址距離>4 
                # 輸出並換行
                self.objectcodeFile.write(f'T{firstLocation}{self.calHex(intDec=len(temp)//2,bits=2)}{temp}\n')
                temp='' # 暫存清零
                jumpFlag=False  
                if iter!=len(self.locationList)-1:
                    firstLocation=self.calHex(strHex=self.locationList[iter+1],bits=6) # 更新開始位置
            iter+=1

        self.objectcodeFile.write(f'E{self.startLocation}\n')
        self.objectcodeFile.close()

    def process(self):
        '''
        主執行程式
        '''
        asmData=self.inputFile.readlines()
        asm=list() # 每行指令分割list
        for data in asmData:
            if len(data.strip().split())!=3: #有三種可能 1.註解行 2.沒有symbol的指令 3.沒有TA的指令(不太影響啦)
                # 把沒有設定symbol的指令加上'-' 使所有指令分割list長度都為3
                if data.strip().split()[0]!='.':
                    data='-'+data
            asm.append(data.strip().split())
        for chunk in asm: 
            if chunk[0]!='.':# 非註解    
                if chunk[1]=='START':
                    # 第一行
                    self.programName=chunk[0]
                    self.startLocation=self.calHex(strHex=chunk[2],bits=6)
                    nowLocation=self.calHex(strHex=chunk[2],bits=4)
                    self.locationList.append(nowLocation)
                else:
                    # 其他行
                    self.locationList.append(nowLocation)
                    nowLocation=self.calHex(strHex=nowLocation,intDec=self.memoryLocationCal(chunk))
            else:
                self.locationList.append(nowLocation)

        #輸出loc.txt
        iter=0
        for line in asmData:
            self.locFile.writelines(f'{self.locationList[iter]} {line} ')
            iter+=1
        self.locFile.close()

        #處理SymbolTable
        iter=0 
        for chunk in asm:
            if chunk[0]!='.' and chunk[0]!='-' and iter!=0: 
                self.symbolTable[chunk[0]]=self.locationList[iter] #找出所有symbol 將symbol位址存入symbolTable
            iter+=1
        
        #生成機器碼
        for chunk in asm:
            self.machineCode.append(self.machineCodeGenerator(chunk))

        #輸出output.txt
        iter=0
        for line in asmData:
            if self.machineCode[iter]==None:
                self.outputFile.writelines(f'{self.locationList[iter]} {line.rstrip()} \n')
            else:
                self.outputFile.writelines(f'{self.locationList[iter]} {line.rstrip()}    {self.machineCode[iter]} \n')
            iter+=1
        self.outputFile.close()
        
        #輸出及生成objectcode.txt
        self.createObjectProgram()

if __name__=='__main__':
    a=assembler('./test.txt')
    a.process()