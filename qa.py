import re 
import os

qa_filename=input('enter qa file name')
if '_qa.txt' not in  qa_filename: raise Exception('not a qa file')
src_filename=input('source file name')
if '_qa.txt' in  src_filename: raise Exception('not a src file')

with open(qa_filename,'r') as f:
    qa_lines=f.readlines()

with open(src_filename,'r') as f:
    src_lines=f.readlines()
    
for i in qa_lines:
    if bool(re.match("id@[0-9]+$",i)):
        for n,j in enumerate(src_lines):
            #print(i,j)
            if i.rstrip() in j.rstrip():
                if src_lines[n+1].rstrip()=='--q--':
                    pass
                else:
                    src_lines[n]=src_lines[n]+'--q--'
                    
with open(src_filename+'qa','w',newline='') as f:
    for line in src_lines:
        line=line.rstrip('\r\n')
        f.write(f"{line}\n")
        
#compare two file except for --q-- 
with open(src_filename,'r') as f:
    src_lines=f.readlines()
with open(src_filename+'qa','r') as f:
    src_lines_qa=f.readlines()
#ignore --q-- lines
src_lines_qa=[ i for i in src_lines_qa if i.rstrip()!='--q--'] 
src_lines=[ i for i in src_lines if i.rstrip()!='--q--'] 
print(src_lines_qa)
if src_lines==src_lines_qa:
    if input('same content do you want to delete back up file y/n ').rstrip().lower()=='y': os.replace(src_filename+'qa',src_filename)
else:
    print('validate two files content does not seem to be same ')

    
        


