'''{"data":{"nodeData":[
{"id":"1","x":70,"y":236,"data":{"name":"trip","desc":"list of places to see"},"parent":[],"children":[],"calculatedX":70,"calculatedY":236},
{"id":"0","x":133,"y":300,"data":{"name":"india","desc":"places and resorts"},"parent":["1"],"children":[],"calculatedX":133,"calculatedY":300},
{"id":"2","x":270,"y":293,"data":{"name":"Rajasthan","desc":"high priority"},"parent":["0"],"children":[],"calculatedX":270,"calculatedY":293},
{"id":"root","x":400,"y":250,"data":{"name":"rootNode","desc":"root Node"},"parent":[],"children":[],"calculatedX":400,"calculatedY":250},
{"id":"1671784454215","calculatedX":411,"calculatedY":259,"x":411,"y":259,"data":{"name":"city palace","desc":"water castle , hawa mahaal , neemarana fort palace"},"parent":["2"],"children":[]},
{"id":"1671785020105","calculatedX":257,"calculatedY":463,"x":257,"y":463,"data":{"name":"pondicherry","desc":"Auroville must be prebooked , bus is there for elders to reach golden globe spot"},"parent":["0"],"children":[]}]}}
'''
ipFile=input('Enter file name').rstrip()
with open(ipFile,'r') as f:
    l=f.readlines()
keyvalue={}
for i in l:
    content=''
    prefix='topic_'
    if i[0:3]=='#?#':
        items=i[2:].split('#')
        if items[1].split('@')[0] in ['topic','section']:
            prefix=items[1].split('@')[0]+'_'
        for j in items:
            temp=j.split('@')
            keys=prefix+temp[0].strip() if len(temp[0]) > 0  else ''
            values=''
            if '@' in j:
                values=temp[1].split(',') if len(temp[1]) > 1 else ''
            if keys!='':
                keyvalue[keys]=values
            if 'section' in keyvalue.keys():
                #print(content)
                content=''
        print(keyvalue)
    else:
        content+=content