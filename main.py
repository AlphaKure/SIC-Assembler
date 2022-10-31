class num:

    def __init__(self):
        self.decNum:int=0
        self.hexNum:str='0000'
    
    def setHex(self,setHex:str,passSaveDec=False):
        if len(setHex)>4:
            print('[error] Hex overflow!')
            return 
        else:
            self.hexNum=setHex
            if not passSaveDec:
                self.decNum=int(setHex,16)
            while len(self.hexNum)<4:
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

opcode={}

def main(path):
    nowLocation=num()
    locationList=list()
    programName=""
    symbolTable=dict()
    asmFile=open(path,'r',encoding='utf-8')
    asmData=asmFile.readlines()
    asm=[data.strip().split() for data in asmData]
    for chunk in asm: 
        if chunk[0]!='.':    
            if chunk[1]=='START':
                programName=chunk[0]
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
                
            

    
if __name__=='__main__':
    main('./test.txt')