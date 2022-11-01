class num:

    def __init__(self):
        self.decNum:int=0
        self.hexNum:str='000000'
    
    def setHex(self,setHex:str,passSaveDec=False,maxlen=4):
        if len(setHex)>maxlen:
            print('[error] Hex overflow!')
            return 
        else:
            self.hexNum=setHex
            if not passSaveDec:
                self.decNum=int(setHex,16)
            while len(self.hexNum)<maxlen:
                self.hexNum='0'+self.hexNum
    
    def next(self,step=3):
        self.decNum+=step
        self.setHex(hex(self.decNum)[2:],passSaveDec=True)

def resChecker(chunk:list[str])->int:
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

def opcodeGen(chunk:list[str],symbolTable):
    opTable={"ADD":"18","AND":"40","COMP":"28","DIV":"24","J":"3C","JEQ":"30","JGT":"34","JLT":"38","JSUB":"48","LDA":"00","LDCH":"50","LDL":"08","LDX":"04","MUL":"20","OR":"44","RD":"D8","RSUB":"4C","STA":"0C","STCH":"54","STL":"14","STSW":"E8","STX":"10","SUB":"1C","TD":"E0","TIX":"2C","WD":"DC"}
    nullObjectList={'START','END','RESW','RESB'}
    if chunk[0]!='.':
        if chunk[1] in nullObjectList:
            return ''
        else:
            if chunk[1]!='BYTE' and chunk[1]!='WORD':
                if len(chunk)==2:
                    return opTable[chunk[1]]+'0000'
                elif chunk[2] and not chunk[2].endswith(',X'):
                    return opTable[chunk[1]]+symbolTable[chunk[2]] 
                else:
                    temp=num()
                    temp.setHex(opTable[chunk]+symbolTable[chunk[2].split(',')[1]])
                    temp.next(step=32768)
                    return temp.hexNum
            else:
                if chunk[1]=='WORD':
                    temp=num()
                    temp.setHex(hex(int(chunk[2],base=16))[2:],maxlen=6)
                    return temp.hexNum
                elif chunk[1]=='BYTE' and chunk[2].startswith('C'):
                    asc=[hex(ord(char))[2:] for char in chunk[2].split("'")[1]]
                    temp=""
                    for code in asc:
                        temp=temp+code
                    return temp
                elif chunk[1]=='BYTE' and chunk[2].startswith('X'):
                    return chunk[2].split("'")[1]
    else:
        return ''
                
                
        

def main(path):
    nowLocation=num()
    startLocation=num()
    locationList=list()
    programName=""
    symbolTable=dict()
    objectFunC=list()
    asmFile=open(path,'r',encoding='utf-8')
    asmData=asmFile.readlines()
    asm=[data.strip().split() for data in asmData]
    for chunk in asm: 
        if chunk[0]!='.':    
            if chunk[1]=='START':
                programName=chunk[0]
                startLocation.setHex(chunk[2],maxlen=6)
                nowLocation.setHex(chunk[2])
                locationList.append(nowLocation.hexNum)
            else:
                locationList.append(nowLocation.hexNum)
                nowLocation.next(step=resChecker(chunk))
        else:
            locationList.append(nowLocation.hexNum)
    
            
    locationOutput=open('./loc.txt','w',encoding='utf-8')
    symTableOutput=open('./SYMTable.txt','w',encoding='utf-8')

    iter=0
    for line in asmData:
        locationOutput.writelines(f'{locationList[iter]} {line}')
        iter+=1
    locationOutput.close()
    asmFile.close()

    iter=0
    for chunk in asm:
        if chunk[0]!='.' and chunk[0]!='-' and iter!=0:
            symTableOutput.writelines(f'{chunk[0]} 0x{locationList[iter]}\n')
            symbolTable[chunk[0]]=locationList[iter]
        iter+=1
    symTableOutput.close()

    for chunk in asm:
        objectFunC.append(opcodeGen(chunk=chunk,symbolTable=symbolTable))

    #print(objectFunC)
                
            

    
if __name__=='__main__':
    main('./test.txt')