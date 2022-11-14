class assembler:
    
    def __init__(self,inputFile:str,outputFile='./output.txt',locFile='./loc.txt',objectcodeFile='./objectcode.txt') -> None:
        
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

        if strHex!=None: 
            if intDec!=None:
                return self.calHex(intDec=(int(strHex,16)+intDec),bits=bits)
            else:
                while len(strHex)<bits:
                    strHex='0'+strHex
                return strHex.upper()
        if intDec!=None:
            temp=hex(intDec)[2:] 
            while len(temp)<bits:
                temp='0'+temp
            return temp.upper()
        
    def memoryLocationCal(self,chunk:list[str])->int:

        if chunk[1]=='RESW': 
            return int(chunk[2])*3
        elif chunk[1]=='RESB':
            return int(chunk[2]) 
        elif chunk[1]=='BYTE':
            if chunk[2].startswith('C'): 
                return len(chunk[2].split("'")[1])
            elif chunk[2].startswith('X'): 
                return int(len(chunk[2].split("'")[1])/2)
        else:
            return 3 

    def machineCodeGenerator(self,chunk:list[str])->str:

        nullObjectList={'START','END','RESW','RESB'} 
        if chunk[0]!='.': 
            if chunk[1] in nullObjectList: 
                return ''
            else:
                if chunk[1]!='BYTE' and chunk[1]!='WORD': 
                    if len(chunk)==2: 
                        return self.opcodeTable[chunk[1]]+'0000'
                    elif chunk[2] and not chunk[2].endswith(',X'):
                        return self.opcodeTable[chunk[1]]+self.symbolTable[chunk[2]] 
                    else:
                        temp=self.calHex(strHex=self.opcodeTable[chunk[1]]+self.symbolTable[chunk[2].split(',')[0]],intDec=32768,bits=6)
                        return temp
                else:
                    if chunk[1]=='WORD':
                        return self.calHex(strHex=hex(int(chunk[2]))[2:],bits=6)
                    elif chunk[1]=='BYTE' and chunk[2].startswith('C'):
                        asc=[hex(ord(char))[2:] for char in chunk[2].split("'")[1]] 
                        temp=""
                        for code in asc:
                            temp=temp+code
                        return temp.upper()
                    elif chunk[1]=='BYTE' and chunk[2].startswith('X'):
                        return chunk[2].split("'")[1].upper()
        else:
            return None
        
    def createObjectProgram(self)->None:
        
        while len(self.programName)<6:
            self.programName=self.programName+' '
        self.objectcodeFile.write(f'H{self.programName}{self.startLocation}{self.calHex(intDec=int(self.locationList[-1],16)-int(self.startLocation,16),bits=6)}\n')
        iter=0
        temp=''
        loc=self.startLocation
        for code in self.machineCode:
            if code==None:
                pass
            elif code=='':
                if temp!='':
                    self.objectcodeFile.write(f'T{loc}{self.calHex(intDec=len(temp)//2,bits=2)}{temp}\n')
                    temp=''
                if iter!=len(self.machineCode)-1:
                    loc=self.calHex(strHex=self.locationList[iter+1],bits=6)
            else:
                if len(temp+code)>60:
                    self.objectcodeFile.write(f'T{loc}{self.calHex(intDec=len(temp)//2,bits=2)}{temp}\n')
                    temp=''
                    loc=self.calHex(strHex=self.locationList[iter],bits=6)
                temp=temp+code
            iter+=1
        self.objectcodeFile.write(f'E{self.startLocation}\n')
        self.objectcodeFile.close()

    def process(self):

        asmData=self.inputFile.readlines()
        asm=list() 
        for data in asmData:
            if len(data.strip().split())<3: 
                if data.strip().split()[0]!='.':
                    data='-'+data
            asm.append(data.strip().split())
        for chunk in asm: 
            if chunk[0]!='.':
                if chunk[1]=='START':
                    self.programName=chunk[0]
                    self.startLocation=self.calHex(strHex=chunk[2],bits=6)
                    nowLocation=self.calHex(strHex=chunk[2],bits=4)
                    self.locationList.append(nowLocation)
                else:
                    self.locationList.append(nowLocation)
                    if chunk[0]!='-':
                        self.symbolTable[chunk[0]]=nowLocation
                    nowLocation=self.calHex(strHex=nowLocation,intDec=self.memoryLocationCal(chunk))
            else:
                self.locationList.append(nowLocation)

        for chunk in asm:
            self.machineCode.append(self.machineCodeGenerator(chunk))

        iter=0
        for line in asmData:
            if self.machineCode[iter]!=None:
                self.outputFile.writelines(f'{self.locationList[iter]} {line.rstrip()}    {self.machineCode[iter]} \n')
                self.locFile.writelines(f'{self.locationList[iter]} {line} ')
            iter+=1
        self.outputFile.close()
        self.locFile.close()

        self.createObjectProgram()

if __name__=='__main__':
    a=assembler('./testdata/monday.txt'
                ,outputFile='./output/output.txt'
                ,locFile='./output/loc.txt'
                ,objectcodeFile='./output/objectcode.txt'
                )
    a.process()