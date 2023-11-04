from flask import Flask , redirect , url_for , request , render_template 
import yaml
import os,platform
import random
from flask_cors import CORS, cross_origin
app=Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/",  defaults={'path': ''})        
@app.route("/", methods=['POST','GET'])
def home():
    return render_template('index.html')

        
@app.route("/post_json",  defaults={'path': ''})        
@app.route("/post_json", methods=['POST','GET'])
def process_json():
    content_type = request.headers.get('Content-Type')
    print(content_type,request.get_json())
    if (content_type == 'application/json'):
        json = request.get_json()
        #json={'fileName':'a__regtr_vd_100.txt'}
        filename_p1=json['fileName'].split('.')[0]
        filename_ext=json['fileName'].split('.')[1]
        filename_p2='_'.join(filename_p1.split('_')[:-1])+'_'+str(int(filename_p1.split('_')[-1])+1) if '_' in filename_p1 and filename_p1.split('_')[-1].isnumeric()  else filename_p1+'_1' 
        newfilename=filename_p2+'.'+filename_ext
        newpurefilename=filename_p2+'_data.'+filename_ext
        datadir='C:\\Users\\mithu\\Desktop\\d3\\'+ '\\'.join(json['location'].split(','))
        try:
            with open(os.path.join(datadir,newfilename),'w',newline='') as f:
                f.write(str(json['data']))
        except UnicodeEncodeError as e:
            print('unicode error')
            data = str(json['data'])[e.start-10:e.start]
            print(data)
        '''puredata=[ i if i[0:6]!='#?#box' else list(filter(lambda d:'name@' in d,i.split('#')))[0] for i in json['data'].split('\n') ]'''
        puredata=[]
        foundbubble=False
        firstBox=True
        for i in json['data'].split('\n'):
            print(i)
            if i[0:6]=='#?#box':
                if '#type@bubble' in i: foundbubble=True
                if not firstBox and not foundbubble: puredata.append('')
                firstBox=False
                if foundbubble:
                    temp = list(filter(lambda d:'name@' in d,i.split('#')))[0] 
                    puredata.append ( temp.split(':')[1] )
                else:
                    puredata.append ( list(filter(lambda d:'name@' in d,i.split('#')))[0] )
            else:
            
                if foundbubble and i.rstrip()=='content':
                    pass
                else:
                    puredata.append (i)
                foundbubble=False
        print(puredata)
        with open(os.path.join(datadir,newpurefilename),'w',newline='') as f:
            for i in puredata:
                print(i,file=f,end='\n')
        return({'status':'success'})
if __name__ == '__main__' : 
    app.run(debug=True)