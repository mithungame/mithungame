import re 
import argparse
from colorama import Fore,init
import glob

init(autoreset=True)

g_clrs={
    'kubernetes':{'magenta':['service','node','pod','container'],'yellow':['etcd','go','kubernetes','docker']},
    'python':{'yellow':['for','if','elif','['],'red':['etcd','go','kubernetes','docker']}
    }

def colored_print(text):
    if g_context==[] or g_context[0] not in g_clrs.keys():
        print(text,end='')
    else:
        context_resolver=list(set(g_context).intersection(set(g_clrs.keys())))[0]
        line_parts = text.split('\n')
        for i in line_parts:
            for j in [word for word in list(re.split('(\W)', i)) if word != '' ]:
                curr_clr='WHITE'
                for clr,value in g_clrs[context_resolver].items():
                    if j=="for":print(j,clr,j.lower() in value,value)
                    if j.lower() in  value:
                        curr_clr=clr.upper()
                        break
                print( getattr(Fore,curr_clr) + j,end='')
            print()
    
def file_to_list(filename):
    lines=[]
    with open(filename,'r') as f:
        lines=f.readlines()
    return lines
    
def dfs(graph,start_node):
    visited = []
    stack = []
    output=[]
    stack.append( start_node )
    start_node['level']=1
    while stack:
        node = stack.pop(0)
        if node['id'] not in visited:
            output.append(node)
            visited.append(node['id'])
            child_list=node['children']
            child_list=node_search_by_id(graph,child_list)
            for i in child_list:
                i['level']=node['level']+1
            child_list.sort(key=lambda d:d['name'].split(':')[0]) # we are not chaning 1:gfdagf prefix to int because i use 1.1 etc as long as we dont cross 9 we wont have problem leave like this for now, sometimes i even miss to add that prefix
            stack = child_list + stack
    return output 
    
def showDFSOutput(res):
    if res == [] : 
        print('No match.. continue')
        return
    n=-1
    for nodes in res:
        for i in nodes:
            n+=1
            if i['level']<=int(args.level):
                if args.expand=='node':
                    print(i)
                elif args.expand=='data':
                    print(i['data'])
                else:
                    tag=i['tag'] if 'tag' in i else ""
                    print( '{:<4}{}{}{} {}'.format(n, '|'*(i['level']-1),'-', i['name'],tag) )
    
    if args.choosenode == "true":
        ip=input('show data for:').rstrip()
        if ip!='':
            ip=int(ip)
            for nodes in res:
                l = len(nodes)
                if ip >= 0 and ip < l:
                    colored_print(nodes[ip]['data'])
                    break
                ip = ip - l
    input('\ncontinue..') # needed for multiple files to stop and continue else it just goes and not able to see result                  

def displayTree(tree):
    print('displayTree')
    res=[]
    root = {'children': [], 'name': '1:display', 'id': '1680960041999', 'parent': [], 'x': '0', 'y': '0', 'data': 'columns\n\n', 'level': 0}#tying them all under a root just for the sake of display
    parent_node = getNoParentNode(tree)
    parent_node_ids = list(map(lambda d:d['id'],parent_node))
    root['children'] = parent_node_ids
    for i in parent_node:
        res.append( dfs(tree,i) )
    showDFSOutput(res)


def to_node(content):
    curr_block=''
    start=False
    identified_hashquestionhash=False
    total_items=[]
    dict_items=dict()
    for i in content:
        if i[0:3]=='#?#':
            identified_hashquestionhash=True
            if start:
                dict_items['data']=curr_block
                curr_block=''
                total_items.append(dict_items)
            else:
                start=True 
            items=i.split('#')
            dict_items=dict()
            for j in items:
                if '@' in j:
                    key=j.split('@')[0]
                    value=j.split('@')[1]
                    if key.lower() in ['parent','children','tag']:
                        value=value.split(',') if value.strip()!='' else []
                    dict_items[key]=value
        elif identified_hashquestionhash:
            curr_block+=i
    dict_items['data']=curr_block
    curr_block=''
    total_items.append(dict_items)
    return(total_items)

def getNoParentNode(tree):
    nodes = list(map(lambda d:d['id'],tree))
    links = list(map(lambda d:d['children'],tree))
    links = [item for sublist in links for item in sublist]
    topNodeIds=list(filter(lambda d:d not in links,nodes))
    topNodes=list(filter(lambda d:d['id'] in topNodeIds,tree))
    return topNodes

def check_node_uniqueness(tree):
    unique_id = list(map(lambda d:d['id'],tree))
    return len(unique_id) == len(set(unique_id))
    
def node_search_by_id(tree,node_id_list=[]):
    selectedNodes=[]
    for i in tree:
        for j in node_id_list:
            if i['id']==j:
                selectedNodes.append(i)
                break
    return selectedNodes 

def node_search_by_child(tree,node_id_list=[]):
    selectedNodes=[]
    for i in tree:
        for j in node_id_list:
            if j in i['children']:
                selectedNodes.append(i)
                break
    return selectedNodes     

def node_search_by_name(tree,node_name_list=[],ignoreCase=False,partialmatch=False):
    selectedNodes=[]
    for i in tree:
        for j in node_name_list:
            if ':' in i['name'] :
                name = i['name'].split(':')[1] 
            else :
                name = i['name']
            if ignoreCase:
                name=name.lower()
            if partialmatch and j in name:
                selectedNodes.append(i)
            elif j==name:
                selectedNodes.append(i)
    return selectedNodes 

def get_all_children(tree,node_id_list=[]):
    selectedNodes=[]
    selected_id=[]
    selected_id+=node_id_list
    for i in selected_id:
        res = get_children(tree, [i])
        for j in res :
            if j['id'] not in selected_id:
                selectedNodes.append(j)
                selected_id.append(j['id'])
    return selectedNodes
    
def get_children(tree,node_id_list=[]):
    selectedNodes=[]
    nodes = node_search_by_id(tree,node_id_list)
    for i in nodes:
        if len(i['children']) > 0 : 
            selectedNodes+=node_search_by_id( tree, i['children'] )
    return selectedNodes    
 
def get_parent(tree,node_id_list=[])->str:
    selectedNodes=[]
    selectedNodes+=node_search_by_child(tree,node_id_list)
    return selectedNodes
    
def is_item_in_list(item,item_list,partial=False):
    item=item.lower()
    item_list=[i.lower() for i in item_list]
    if not partial:
        return item in item_list
    else:
        for i in item_list:
            if item in i:
                return True
    
def match_node_property(node_list,value=[''],property_name=['tag','name']):
    selectedNodes=[]
    for j in node_list:
        match=[]
        for i in value:
            match_found=False
            for k in property_name:
                if k in j:
                    property_name_list=j[k] if isinstance(j[k],list)  else [j[k]] #some property like tag is a list but name is not a list so making common
                    if is_item_in_list(i,property_name_list,True):
                        match_found=True
                        break #found stop searching properties as for one property match is found
            match.append(match_found)
        if all(match):
            selectedNodes.append(j)
                
    return selectedNodes
    
def parse_command(tree,command,args_property):
    #cmd = list(re.split('([\>\&])',command))
    cmd = list(command.split('>'))
    selectedNodes=tree
    prev_node = None
    for i in cmd:
        cmd_parts=i.split(':')
        node=cmd_parts[0].split(',') if cmd_parts[0]!='' else []
        tag =cmd_parts[1].split(',') if len(cmd_parts)>1 and cmd_parts[1]!='' else []
        if node!=[]:
            curr_node_list  = node_search_by_name(selectedNodes,node,ignoreCase=True)
            curr_node_ids = list(map(lambda d:d['id'],curr_node_list))
            selectedNodes = get_all_children(selectedNodes,curr_node_ids)
        if tag!=[]:
            selectedNodes = match_node_property(selectedNodes,tag,args_property)
    return(selectedNodes)
        

def dive_mode(tree):
    cmd =  input('enter name - This will be the starting location:')
    curr_node_list  = node_search_by_name(tree,[cmd.rstrip()],ignoreCase=True,partialmatch=True)
    for n,i in enumerate(curr_node_list):
        print(n,i['name'])
    start=int(input('choose diving point:'))
    selectedNodes=[curr_node_list[start]]
    
    
    while True:
        childNodes = get_children(tree, list(map(lambda d:d['id'],selectedNodes)))
        colored_print ( "===\n"+selectedNodes[0]['name'] + '\n'+ selectedNodes[0]['data'] +'===\n\n')
        prevNode = get_parent(tree, list(map(lambda d:d['id'],selectedNodes)) ) 
        if len(childNodes) == 0:
            start=input(getattr(Fore,'RED') + 'end of road e: to end b: to go back'+ Fore.RESET  ).rstrip()
            if start not in ['e','b'] or start == 'e':
                print('bye..')
                break
            else:
                print()
        else:
            for n,i in enumerate(childNodes):
                print(str(n)+'('+i['name']+')',end=' ')
            print()
            if len(prevNode)>0:
                print('Backward Node:(',prevNode[0]['name'],')')
            
            start=input(getattr(Fore,'GREEN') + 'choose starting point: b for prev'+ Fore.RESET  )
        if start=='b':
            if len(prevNode)<1: #this has no parent so we cannot go back 
                selectedNodes = selectedNodes
            else:
                selectedNodes = [ prevNode[0] ]
        else:
            selectedNodes= [childNodes[int(start)]]
        

g_context=[]    
def search(args,filename):
    content=file_to_list(filename)
    tree=to_node(content)
    global g_context
    context=[ j.rstrip() for i in tree if i['id']=='seed' and 'tag' in i for j in i['tag']]
    g_context=[i.rstrip() for i in context]
    print("context is:",context)
    if args.search!='' and args.search is not None:
        args_property = args.property.split(',') if args.property != '' else ['name','tag']
        args_level = args.level
        filtered_nodes = parse_command(tree,args.search,args_property)
        displayTree(filtered_nodes)
    if args.dive=='true' and args.dive is not None:
        dive_mode(tree)
        
def main(args):
    files=[]
    file_list = {'reference' : [r'C:\Users\mithu\Downloads\track\projects\d3\core\data\*[0-9].txt', # non recursive
                    r'C:\Users\mithu\Downloads\track\projects\**\quickref.txt',# ** means recursive
                    #r'G:\My Drive\Downloads\jarvis\tech\**\py*.txt' not all files are converted now
                    ],
                'spark' : [r'C:\Users\mithu\Downloads\track\projects\d3\core\data\sp*.txt'],
                'secret' : [r'C:\Users\mithu\Downloads\track\projects\d3\privateData\secret*.txt']
                }
    if args.key=='all':
        chosen_file_list = list({x for v in file_list.values() for x in v})
    elif args.key is not None:
        chosen_file_list = file_list[args.key.lower()]
    else:
        chosen_file_list=[args.filename]
    for i in chosen_file_list:
        files+=glob.glob(i,recursive=True) 

    #dont make it complicated search each file individually
    for filename in files:
        print(Fore.YELLOW+ 'processing file:'+ filename)
        search(args,filename)


parser = argparse.ArgumentParser()
parser.add_argument("-k","--key", help="search by key reference,nifi instead of file")
parser.add_argument("-f","--filename", help="increase output verbosity")
parser.add_argument("-s","--search", help="increase output verbosity")
parser.add_argument("-d","--dive", help="dive into tree ",nargs="?",default='false',const="true")
parser.add_argument("-p","--property", help="increase output verbosity", default="name,tag")
parser.add_argument("-l","--level", help="increase output verbosity", default=100)
parser.add_argument("-e","--expand", help="node data", default=100)
parser.add_argument("-c","--choosenode", help="choosenode",nargs="?",default='false',const='true') #if just -c value 1 if nothing value false
args = parser.parse_args()    
print(args)
if __name__=="__main__":
    main(args)
    
    

