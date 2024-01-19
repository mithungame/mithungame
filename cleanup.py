import glob,os,re,shutil
i=input("1 data 2 private data").rstrip()
all_path={ '1' : r'C:\Users\mithu\Downloads\track\projects\d3\core\data' , '2' : r'C:\Users\mithu\Downloads\track\projects\d3\privateData' } 
base_path=all_path[i]
file_path=base_path+'\\*.txt'
file_list=glob.glob(file_path)
latest=dict()
for i in file_list:
    filename=os.path.basename(i)
    filename_parts=re.split('[_.]',filename)
    version=None
    if filename_parts[-1]=='txt' and filename_parts[-2]=='data' and len(filename_parts)==4:
        version=int(filename_parts[1])
        curfilename=filename_parts[0]+'_<N>_'+filename_parts[2]+'.'+filename_parts[3]
    elif len(filename_parts)==3:
        version=int(filename_parts[1])
        curfilename=filename_parts[0]+'_<N>'+'.'+filename_parts[2]
    else:
        raise Exception('incorrect file format:'+i)
    curfilename=os.path.join(os.path.dirname(i),curfilename)
    if curfilename in latest:
        if latest[curfilename]<version:
            latest[curfilename]=version
    else:
        latest[curfilename]=version
        
new_files=[]

for k,v in latest.items():
    new_files.append(k.replace("<N>",str(v)))
old_files=[]
old_files=list(  set(file_list) ^ set(new_files)  )

old_files.sort()
for i in old_files:
    print('moving..',os.path.basename(i))
    shutil.move(i,os.path.join(base_path,'old',os.path.basename(i)))