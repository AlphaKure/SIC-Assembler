def transHex(inputHex:str=None,dec:int=None,bits=4)->str:
    if inputHex!=None:
        if dec!=None:
            return transHex(dec=(int(inputHex,16)+dec),bits=bits)
        else:
            while len(inputHex)<bits:
                inputHex='0'+inputHex
            return inputHex.upper()
    if dec!=None:
        temp=hex(dec)[2:]
        while len(temp)<bits:
            temp='0'+temp
        return temp.upper()

def commandLocCal(chunk:list[str])->int:
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
                    temp=transHex(inputHex=opTable[chunk[1]]+symbolTable[chunk[2].split(',')[0]],bits=6)
                    temp=transHex(inputHex=temp,dec=32768,bits=6)
                    return temp
            else:
                if chunk[1]=='WORD':
                    temp=transHex(inputHex=hex(int(chunk[2]))[2:],bits=6)
                    return temp
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
                                
def createObjectProgram(objectProgramFile,programName,startLocation,objectFunc:list,locationList):
    while len(programName)<6:
        programName=programName+' '
    objectProgramFile.write(f'H{programName}{startLocation}{transHex(dec=int(locationList[-1],16)-int(startLocation,16),bits=6)}\n')
    temp=''
    iter=0
    jumpFlag=False
    firstlocation=transHex(inputHex=locationList[iter],bits=6)
    for location in locationList:
        if iter!=len(locationList)-1:
            if (int(locationList[iter+1],16)-int(location,16))>4:
                jumpFlag=True
        if objectFunc[iter]!='' and objectFunc[iter]!=None:
            if iter!=len(locationList)-1:
                temp=temp+objectFunc[iter]
        if len(temp)>55 or (iter==len(locationList)-1 and temp!='')or jumpFlag:
            objectProgramFile.write(f'T{firstlocation}{transHex(dec=len(temp)//2,bits=2)}{temp}\n')
            temp=''
            jumpFlag=False
            if iter!=len(locationList)-1:
                firstlocation=transHex(inputHex=locationList[iter+1],bits=6)
        iter+=1

    objectProgramFile.write(f'E{startLocation}\n')
    objectProgramFile.close()

def main(inputFile):

    locationFile=open('./loc.txt','w',encoding='utf-8')
    outputFile=open('./output.txt','w',encoding='utf-8')
    objectcodeFile=open('./objectcode.txt','w',encoding='utf-8')

    locationList=list()
    programName=""
    symbolTable=dict()
    objectFunC=list()
    asmFile=open(inputFile,'r',encoding='utf-8')
    asmData=asmFile.readlines()
    asm=list()
    for data in asmData:
        if len(data.strip().split())!=3:
            if data.strip().split()[0]!='.':
                data='-'+data
        asm.append(data.strip().split())
    for chunk in asm: 
        if chunk[0]!='.':    
            if chunk[1]=='START':
                programName=chunk[0]
                startLocation=transHex(inputHex=chunk[2],bits=6)
                nowLocation=transHex(inputHex=chunk[2],bits=4)
                locationList.append(nowLocation)
            else:
                locationList.append(nowLocation)
                nowLocation=transHex(inputHex=nowLocation,dec=commandLocCal(chunk))
        else:
            locationList.append(nowLocation)

    #輸出loc.txt
    iter=0
    for line in asmData:
        locationFile.writelines(f'{locationList[iter]} {line} ')
        iter+=1
    locationFile.close()

    #寫SymbolTable
    iter=0 
    for chunk in asm:
        if chunk[0]!='.' and chunk[0]!='-' and iter!=0:
            symbolTable[chunk[0]]=locationList[iter]
        iter+=1
    
    #生成指令碼
    for chunk in asm:
        objectFunC.append(opcodeGen(chunk=chunk,symbolTable=symbolTable))

    #輸出output.txt
    iter=0
    for line in asmData:
        if objectFunC[iter]==None:
            outputFile.writelines(f'{locationList[iter]} {line.rstrip()} \n')
        else:
            outputFile.writelines(f'{locationList[iter]} {line.rstrip()}    {objectFunC[iter]} \n')
        iter+=1
    outputFile.close()
    
    #輸出及生成objectcode.txt
    createObjectProgram(objectcodeFile,programName,startLocation,objectFunC,locationList)

    #print(objectFunC)


if __name__=='__main__':
    main('./test.txt')