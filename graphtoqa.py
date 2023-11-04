import os 

def check_file_format_violation_data(list_of_files):
    parts = [ i.split('_') for i in list_of_files ]
    #ignore data files
    parts = [ i for i in parts if i[-1] != 'data.txt' ]
    #check if file has only 2 parts <filename>_<n.txt> 
    #check if n.txt's format
    for  i in parts:
        if len(i) > 2 or not isinstance(int(i[-1].split('.')[0]),int) or i[-1].split('.')[1] != 'txt':
            print(i+' violated file format')
            raise Exception("file is not of format <filename>_<n.txt> ")

def fetch_latest_file(list_of_files):
    parts = [ i.split('_') for i in list_of_files ]
    max_version_files = dict()
    for i in parts:
        filename = i[0]
        version = int(i[1].split('.')[0])
        # max logic
        if filename in max_version_files:
            if version > max_version_files[filename]:
                max_version_files[ filename ] = version
        else :
            max_version_files[ filename ] = version
    return [k+'_'+str(v)+'.txt' for k,v in max_version_files.items()]
    
def check_file_format_violation_qa(list_of_files):
    parts = [i.split('.') for i in list_of_files ]
    for i in parts:
        print(i)
        if re.findall('[^a-zA-Z0-9]', i[0]) or i[1] != 'txt':
            raise Exception("file is not of format <filename>_.txt ")
    

data_path = os.path.join( os.getcwd() , 'data')
qa_path = os.path.join( os.getcwd() , 'qa')
data_files = os.listdir(data_path)
check_file_format_violation_data(data_files)
data_files = fetch_latest_file(data_files)
qa_files = os.listdir(qa_path)
check_file_format_violation_qa(qa_files)
