import re 
import sys
import argparse
import glob
import os, platform
import random
import shutil
import time
from datetime import datetime, timedelta
g_target_device = None
if platform.system() == 'Windows': 
    g_target_device = "windows"
elif os.getcwd().startswith('/storage/emulated/0/'): 
    g_target_device = "phone"
else:
    g_target_device = "linux"

if g_target_device == 'windows': import msvcrt

g_debug_dict={0: 'show_none', 1: 'show_func_names',2: 'show_func_name_and_params'}
g_remember_modified=False

context_precedence = { 
'snowflake': ['sql'] ,
'sf': ['sql'] ,
'python': ['python'] , 
'aws': ['aws', 'network']
}
day_of_week={0:'mon', 1:'tue', 2:'wed', 3:'thu', 4:'fri', 5: 'sat', 6:'sun'}
g_clrs={
    'default': {'white':[]},
    'kubernetes':{'magenta':['service','node','pod','container'],'yellow':['etcd']},
    'general': {'green':
        'sql sql python java c c++ go docker kubernetes'.split(" ") +
        'amazon aws azure cloud'.split(" ") +
        'oracle mongo dynamo redshift cassandra hive iceberg'.split(" ") + 
        'network subnet vpc vpc firewall '.split(" "),
        'red': '?' #for questions
    },
    'python':
    {'yellow': "assert async await break class continue def del elif else except finally global import lambda nonlocal pass raise return try while yield".split(" "),
    'red':"ArithmeticError AssertionError AttributeError BaseException BlockingIOError BrokenPipeError BufferError BytesWarning ChildProcessError ConnectionAbortedError ConnectionError ConnectionRefusedError ConnectionResetError DeprecationWarning EOFError Ellipsis EnvironmentError Exception False FileExistsError FileNotFoundError FloatingPointError FutureWarning GeneratorExit IOError ImportError ImportWarning IndentationError IndexError InterruptedError IsADirectoryError KeyError KeyboardInterrupt LookupError MemoryError ModuleNotFoundError NameError None NotADirectoryError NotImplemented NotImplementedError OSError OverflowError PendingDeprecationWarning PermissionError ProcessLookupError RecursionError ReferenceError ResourceWarning RuntimeError RuntimeWarning StopAsyncIteration StopIteration SyntaxError SyntaxWarning SystemError SystemExit TabError TimeoutError True TypeError UnboundLocalError UnicodeDecodeError UnicodeEncodeError UnicodeError UnicodeTranslateError UnicodeWarning UserWarning ValueError Warning WindowsError ZeroDivisionError abs all any ascii bin bool breakpoint bytearray bytes callable chr classmethod compile complex copyright credits delattr dict dir divmod enumerate eval exec exit filter float format frozenset getattr globals hasattr hash help hex id input int isinstance issubclass iter len license list locals map max memoryview min next object open ord pow print property quit range repr reversed round set setattr slice sorted staticmethod str sum super tuple type vars zip".split(" ")
    },
    'aws':
    {'yellow': "ec2".split(" ")
    },
    'sf':
    {'yellow': "snowpark clone dynamic micropartition temporary transient permanent ".split(" ")
    },
    'sql':
    {'cyan': "database databases materialization table tables view views".split(" ")
    }
    }
g_stop_words=['a', 'about', 'above', 'after', 'again', 'against', 'ain', 'all', 'am', 'an', 'and', 'any', 'are', 'aren', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'couldn', "couldn't", 'd', 'did', 'didn', "didn't", 'do', 'does', 'doesn', "doesn't", 'doing', 'don', 'dont', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn', "hadn't", 'has', 'hasn', "hasn't", 'have', 'haven', "haven't", 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'isn', "isn't", 'it', "it's", 'its', 'itself', 'just', 'll', 'm', 'ma', 'me', 'mightn', "mightn't", 'more', 'most', 'mustn', "mustn't", 'my', 'myself', 'needn', "needn't", 'no', 'nor', 'not', 'now', 'o', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 're', 's', 'same', 'shan', "shan't", 'she', "she's", 'should', "should've", 'shouldn', "shouldn't", 'so', 'some', 'such', 't', 'than', 'that', "that'll", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 've', 'very', 'was', 'wasn', "wasn't", 'we', 'were', 'weren', "weren't", 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'won', "won't", 'wouldn', "wouldn't", 'y', 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']
'''g_priority={
1: {  3  :'GREEN' , 7 : 'YELLOW' , 14 :'BLUE'  , 21: 'MAGENTA', 3000: 'RED'}, # important
2: {  7  :'GREEN' , 10: 'YELLOW' , 14 :'BLUE'  , 21: 'MAGENTA', 3000: 'RED'}, # something like snowflake
3: {  10 :'GREEN' , 14: 'YELLOW' , 21 :'BLUE'  , 30: 'MAGENTA', 3000: 'RED'}, # something like hive
4: {  14 :'GREEN' , 18: 'YELLOW' , 28 :'BLUE'  , 30: 'MAGENTA', 3000: 'RED'}, # something like gk
5: {  20 :'WHITE' , 30: 'WHITE'  , 40 :'WHITE'  , 45: 'WHITE'  , 3000: 'WHITE'} # default 
}'''
g_priority=[ 'RED' , 'BLUE' , 'YELLOW' , 'GREEN' ]


class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        #self.impl = _GetchWindows()
        if g_target_device == 'windows': 
            self.impl = _GetchWindows()
        elif g_target_device == 'linux': 
            self.impl = _GetchUnix()

    def __call__(self): 
        try:
            return self.impl()
        except Exception as e:
            return input('')

class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()
        
class _GetchDefault:
    def __init__(self):
        pass

    def __call__(self):
        return input()


getch = _Getch()

   
def node_gate(func):
    def inner(*arrs,**kwargs): # must have inner function for decorator
        result = func(*arrs, **kwargs)    
        for i in result:
            for key in i:
                if not key.startswith('_') and key not in ['id','calculatedX','calculatedY','children','name','id','parent','x','y','tag','data','date','t_color','d_visibility','type','meta','fileid','priority']:
                    raise Exception ('A node key seen "{}" "{}:{}" which is not existing currently'.format(key,i['_filename'],i['id']))
        return result
    return(inner)

g_debug_gate_context={'last_called_function': None}
def debug_gate(func):
    def inner(*arrs,**kwargs): # must have inner function for decorator
        curr_func = func.__name__
        g_debug_gate_context['func_being_called'] = curr_func
        if g_debug_dict[args.debug]=='show_func_names':
            if g_debug_gate_context['func_being_called'] == g_debug_gate_context['last_called_function']:
                g_debug_gate_context[func.__name__] += 1
            else:
                last_func = g_debug_gate_context['last_called_function']
                if last_func and g_debug_gate_context[ last_func ] > 1 : print("Calling function", last_func, g_debug_gate_context[ last_func ])
                g_debug_gate_context[last_func] = g_debug_gate_context[curr_func] = 0
                print("Calling function",func.__name__)
        g_debug_gate_context['last_called_function'] = func.__name__
        result = func(*arrs, **kwargs)    
        
        return result
    return(inner)

g_color_context=[]
def set_color_context():
    global g_color_context
    g_color_context=[]
    color_search_order_list=[]
    if 'context' in g_context: color_search_order_list += g_context['context']
    for i in color_search_order_list: # check match 
        for k,v in context_precedence.items(): # search each item 
            if i == k: # if context match
                for each in v: # loop each item of context_precedence_value
                    if each not in color_search_order_list:
                        color_search_order_list.append(each)
    #context_resolver=list(set(g_context['context']).intersection(set(g_clrs.keys())))
    color_search_order_list+=['default']
    for i in color_search_order_list:
        if i in g_clrs.keys():
            g_color_context.append(i)
    print('color context order is',g_color_context)
    
#only color functions should call this 
def give_color(color,clear=True):
    clear_value = '' 
    if clear: clear_value = '\033[0m'
    if color.upper() == "WHITE":
        return { 'pre_control' : '' , 'post_control':  '' }
    else:
        return { 'pre_control' : getattr(Fore,color) , 'post_control':  clear_value }

def word_obj_to_letter_obj(word_obj):
    chars=[]
    for letter in word_obj['word']:
        chars.append( { **word_obj , **{'txt': letter}} )
    return chars

class color_word:
    def __init__(self,word,color="WHITE",context=False):
        self.word = word  
        if args.vannangal == "true":
            if context is None: 
                self.context = True 
            else:
                self.context = context
            self.color = color
        else:
            self.context = False
            self.color = "WHITE"
        self.colorify()
    def colorify(self):
        if not self.context:
            self.colored_obj= give_color(self.color)
        else:
            curr_clr=self.color
            for each in g_color_context+['general']:
                found=False
                for clr,value in list(g_clrs[each].items()):
                    if self.word.lower() in  value:
                        curr_clr=clr.upper()
                        found=True
                        break
                if found: break
            self.colored_obj= give_color(curr_clr)
        self.colored_obj['word']=self.word
    def __str__(self):
        return self.colored_obj['pre_control'] + self.colored_obj['word'] + self.colored_obj['post_control']

class color_line:
    def __init__(self,line,color="WHITE",context=False):
        self.line = line  
        self.context = context 
        self.color = color
        self.colorify()
    def colorify(self) -> list:
        words = list(re.split('(\W)', self.line))
        words = [i for i in words if i]
        if len(words) == 0: #its a special case caused by a\n\nb
            words=['']
        self.colored_obj: list = []
        for word in words:
            self.colored_obj.append( color_word( word,  self.color,self.context ) )
    def __str__(self):
        line = ''
        for i in self.colored_obj:
            line += str(i)
        return line


class color_text:
    def __init__(self,text,color="WHITE",context=None):
        self.text = text  
        self.color = color 
        self.context = context
        self.colorify()
    def colorify(self) -> list:
        lines = self.text.split('\n')
        self.colored_obj: list = []
        for line in lines:
            self.colored_obj.append( color_line(line, self.color, self.context))
    def __str__(self):
        text = ''
        for i in self.colored_obj:
            text += str(i) + '\n'
        return text
        
def colored_print(text,context=None,color="WHITE"):
    text = str(color_text(text,color,context))
    lines = [ line for line in text.split('\n')]
    for line in lines:
        for word in line.split(' '):
            print( word , end=' ')
            if args.modeofprint=='word': 
                input()
        if args.modeofprint=='line': 
            input()
        else:
            print()

@debug_gate            
def file_to_list(filename):
    lines=[]
    with open(filename,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines

@debug_gate
def dfs(graph,start_node,child_key='_children',add_level=True):
    visited = []
    stack = []
    output=[]
    stack.append( start_node )
    start_node['_level']=1
    while stack:
        node = stack.pop(0)
        if node['id'] not in visited:
            output.append(node)
            visited.append(node['id'])
            #print(node)
            child_list=node[child_key]
            child_list=node_search_by_id(graph,child_list)
            for i in child_list:
                i['_level']=node['_level']+1
            #child_list.sort(key=lambda d:d['name'].split(':')[0]) # we are not chaning 1:gfdagf prefix to int because i use 1.1 etc as long as we dont cross 9 we wont have problem leave like this for now, sometimes i even miss to add that prefix
            stack = child_list + stack
    return output 

@debug_gate
def showDFSOutput(res):
    #print('---------------------\033[H',end='') # go to home https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
    #print('\033[0J',end='') #clear till end 
    #print('\033[1J',end='')
    #print('',end='',flush=True)
    if res == [] : 
        print('No match.. continue')
        return
    n=-1
    for i in res:
        #print(i['name'],i['_level'])
        n+=1
        if i['_level']<=int(args.level):
            if args.expand=='node':
                print(i)
            elif args.expand=='data':
                print(i['data'])
            else:
                tag=i['tag'] if 'tag' in i else ""
                curr_level=i['_level']-1
                display_tree_level =  '|' + ( '-' * ( curr_level )  ) * 3
                print( '{:<4}{}{}{} {}'.format(n, display_tree_level,'-', i['name'],tag) )
    
    if args.choosenode == "true":
        ip=input('show data for:').rstrip()
        if ip!='':
            ip=int(ip)
            if ip >= 0 and ip < len(res):
                colored_print(res[ip]['data'])
    action=input('q quit o onceMore enter continue..').rstrip()# needed for multiple files to stop and continue else it just goes and not able to see result                  
    #action='o'
    if action=='q':
        sys.exit(0)
    elif action =='o':        
        #print('\0338',flush=True)
        #input()
        #print('\033[0J',end='',flush=True)
        showDFSOutput(res)
    else:
        pass

@debug_gate
def build_partial_tree(tree, filtered_nodes, seed):
    seed['_children'] = [] # this has to be done at first cnt wait for its turn
    for each_item in filtered_nodes:
        v_each_item = each_item
        if each_item['id'] != 'seed':
            each_item['_children'] = []
            #print('processing item ',v_each_item['name'])
            has_upstream = False
            while not has_upstream:
                parent = node_search_by_child(tree, v_each_item['id'] ,  )
                #lets say the current parent is not attached to anything and was not in list of selected items it will cause a problem
                if parent and parent['id'] in [ i['id'] for i in filtered_nodes] :
                    if '_children' in parent :
                        parent['_children'] += [ each_item['id'] ]
                        #print('found parent for ',each_item['name'], ' it is ', parent['name'])
                    else:
                        parent['_children'] = [ each_item['id'] ]
                    has_upstream = True
                elif parent:
                    v_each_item = parent
                    pass # keep going 
                else : # found no parent at all attach to seed 
                    #print('found no parent for ',v_each_item['name'])
                    seed[ '_children' ] += [ each_item['id'] ]
                    has_upstream = True
    #for i in filtered_nodes: print(i['id'],end=' ')
    return filtered_nodes

@debug_gate
def link_calendar_tree_from_all_searched_files(calendar_objs):
    #print('link_calendar_tree_from_all_searched_files')
    search_all()
    for each_file in g_context['chosen_file_list']:
        each_file=os.path.basename(each_file)
        for each_obj in g_context[each_file]['tree']: # this is directly reading from tree not filtered tree dont change immediately see how it goes
            for obj in calendar_objs:
                if 'date' in each_obj:
                    for each_date in each_obj['date']:
                        match = False
                        if re.match("^[0-9][0-9]$",each_date):
                            if each_date[:2].lower()==obj['name'][:2].lower(): match = True
                        elif re.match("^[0-9][0-9][0-9][0-9]$",each_date):
                            if each_date[-4:].lower()==obj['name'][-4:].lower(): match = True
                        elif each_date.lower() in "jan,feb,mar,apr,jun,jul,aug,sep,oct,nov,dec".split(','):
                            if each_date[2:5].lower()==obj['name'][2:5].lower(): match = True
                        elif each_date.lower() in "mon,tue,wed,thu,fri,sat,sun".split(','):
                            if each_date.lower()==day_of_week[obj['_day_obj'].weekday()]: match = True
                        elif re.match("^[0-9][0-9](jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)$",each_date):
                            if each_date[0:5].lower()==obj['name'][0:5].lower(): match = True
                        elif re.match("^[0-9][0-9](jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)[0-9][0-9][0-9][0-9]$",each_date):
                            if each_date.lower()==obj['name'].lower(): match = True
                        else:
                            raise Exception('Incorrect date format',each_file,each_obj)
                        if match: 
                            obj['data'].append({'type': 'link', 'id': each_obj['id'], 'filename': os.path.basename(each_obj['_filename']) })
                            if 'tag' in each_obj: obj['tag'] = each_obj['tag'] #need this for search using tags

@debug_gate
@node_gate
def build_calendar_tree(year, seed, filename):
    #print('build_calendar_tree',year)
    cal_objs=[seed]
    week_count=1
    week=[]
    curr_day=datetime(year,1,1)
    id =  int(time.time())
    if curr_day.weekday() < 6: 
        curr_day = curr_day + timedelta(days=- curr_day.weekday() - 1 ) 
    #print(curr_day)
    curr_day += timedelta(days=-1) # it will increment while starting so just offsetting by 1
    while True:
        curr_day = curr_day + timedelta(days=1)
        curr_day_of_week = curr_day.weekday()
        id += 1 
        str_id = str(id)
        curr_formatted_day=curr_day.strftime('%d%b%Y').lower()
        obj = {'name': curr_formatted_day, 'id': str_id, 'parent': [], 'x': '-1', 'y': '-1', 'tag': [], 'data': [], '_children': [] , '_filename': filename, '_day_obj': curr_day}
        if not week:
            seed['_children'].append( str_id )
        else:
            week[-1]['_children'].append( str_id )
        week.append(obj)#week will have it in tree format
        cal_objs.append(obj)#just all the objs
        if len(week)==7: 
            if curr_day.year == year + 1 or ( curr_day.month == 12 and curr_day.day == 31 ) :
                break
            else:
                week=[]
    link_calendar_tree_from_all_searched_files(cal_objs)
    #print('+++',cal_objs[0])
    return cal_objs

@debug_gate
def build_calendar_tree_from_result(year):
    if len(str(year))!=4: raise Exception('Provide year in 4 digit format yyyy')
    filename='cal'+str(year)
    if filename  not in g_context:
        seed = {'name': 'seed', 'id': 'seed', 'parent': [], 'x': '-1', 'y': '-1', 'data': [], 'children': [] , '_filename': filename, '_children': [] ,'_day_obj': datetime(9999,1,1)}
        tree = build_calendar_tree(year,seed, filename)
    else:
        tree = g_context[filename]['tree']
        seed = g_context[filename]['tree'][0]
    set_g_context(filename=filename,change_current_context=False,tree=tree)
    return filename

@debug_gate
def build_tree_from_result(tree, filtered_nodes,seed, mode='tree') -> None:
    #print('calling display tree')
    res=[]
    #for i in tree: print(i['name'])
     #parent_node = getNoParentNode(tree)
    #parent_node_ids = list ( set(map(lambda d:d['id'],parent_node)).difference({'seed'}) )
    #if seed not in result seed must be added as root 
    #seed['children']=[ i for i in parent_node_ids ] # clear out existing children we are building new graph
    #parent_node = seed
    #the tree generated here is actually disconnected example if a child in 3rd level is selccted and grand parent is selected it is not attached to grand parent so we are going to attach it to closest ancestor
    if 'seed' not in [ i['id'] for i in tree  ]: filtered_nodes.insert(0,seed)
    return build_partial_tree(tree, filtered_nodes,seed)
    #print(g_context[active_file]['filtered_tree'][0])

@debug_gate
def build_tree_from_popup(node):
    global g_ephemeral_tree
    #check if already present 
    is_exist=False
    for i in g_ephemeral_tree:
        if len(i['data'])>1: raise Exception('Ephemeral node can point to only one node {}'.format(i))
        link_data=i['data'][0]
        if link_data['type']=="link": #seed will have default type
            if node['id']+g_context['filename'] == link_data['id']+i['_filename']: #note id is link_data's id filename comes from node because link will have base filename
                is_exist=True 
                input('Node already pinned in ephemeral tree')
                break
    if not is_exist:
        filename=g_context['filename']
        id =  str(int(time.time()))
        data = {'type': 'link', 'id': node['id'], 'filename': os.path.basename(node['_filename']) }
        obj = {'name': node['name'], 'id': id, 'parent': [], 'x': '-1', 'y': '-1', 'tag': [], 'data': [data], 'children':[] ,'_children': [] , '_filename': filename }
        if len(g_ephemeral_tree)>1 and (len(g_ephemeral_tree)-1)%3==0:#>1 accomodates seed
            #g_ephemeral_tree[0]['_ephemeral_children'].append(node['id'])
            g_ephemeral_tree[0]['children'].append(id)
            g_ephemeral_tree[0]['_children'].append(id)
        else:
            #g_ephemeral_tree[-1]['_ephemeral_children'].append(node['id'])
            g_ephemeral_tree[-1]['children'].append(id)
            g_ephemeral_tree[-1]['_children'].append(id)
        g_ephemeral_tree.append(obj)
    #print(g_ephemeral_tree)
    #input()

@debug_gate
def tree_display(tree,seed,mode): #dont use g_context here , it gets into the are of table context, initialize True will do it False wont do it None will check if its already done and not do it if so
    if args.tree == 'false':
        result_dfs=dfs(tree,seed) 
        #showDFSOutput(result_dfs)
        return screen_coordinator('vertical_tree',result_dfs ,{ 'base_data': tree, 'start_node': seed })
    elif args.tree == "true":
        #child_key = "_children" if mode in ["tree","calendar"] else "_ephemeral_children" 
        child_key = "_children"
        for i in tree:
            if "d_visibility" in i.keys() and i["d_visibility"]=="hidden":
                hide_children( i, tree , key=child_key )
        data_table = build_data_table_from_tree(seed,tree,child_key)
        return screen_coordinator(mode,data_table ,{ 'base_data': tree, 'child_key': child_key, 'start_node': seed })

def pick_random_selected_item():
    who_is_on_screen = g_screen_obj['active_obj']
    active_obj = g_screen_obj[who_is_on_screen]
    selected_visible_items = active_obj['state_of_table']['selected_visible_items']
    rand_obj = random.choices(selected_visible_items)
    return rand_obj

@debug_gate
def popup_display(id):
    who_is_on_screen = g_screen_obj['active_obj']
    active_obj = g_screen_obj[who_is_on_screen]
    selected_visible_items = active_obj['state_of_table']['selected_visible_items']
    popup_obj={"name": 'NO ACTIVE ITEM', "_filename": "_popup", "id": "-1", "data": [{ 'type': 'default', 'txt': 'error'}] }
    if id is None:
        rand_obj = pick_random_selected_item() #random.choices(selected_visible_items)
        if rand_obj: popup_obj=rand_obj[0]['obj']
    for i in selected_visible_items:
        if i['obj']['_print_arr_name']==id:
            popup_obj=i['obj']
            break
    '''popup_x = 3 #even though i set column next print will override it , tired of fixig now
    popup_y = 3
    print('\033[{};{}H'.format(popup_y,popup_x),end='')
    print('*'*max_len_of_line)
    for _ in range(0, table_properties['height']-1):
        for line in popup_data :
            line = (line + ' ' * max_len_of_line)[0:max_len_of_line]
            print(''.join( color_line(line,True,'YELLOW') ))
        print(' '*max_len_of_line)
    print('*'*max_len_of_line)'''
    screen_coordinator('popup',[popup_obj] ,{ 'who_is_on_screen' : who_is_on_screen , 'base_data': popup_obj})

@debug_gate
def display_table(clear_screen = True, cursor_pos = None):
    no_of_lines_printed=0
    who_is_on_screen = g_screen_obj['active_obj']
    active_obj = g_screen_obj[who_is_on_screen]
    table_to_be_printed = active_obj['table_to_be_printed']
    command_options = active_obj['command_options']
    color = active_obj['table_properties']['default_color']
    if clear_screen: ansii_screen_controls()
    if cursor_pos: ansii_screen_controls( 'move_cursor_x_y', {'x': cursor_pos['x'], 'y': cursor_pos['y'] })
    lines=''
    for line in table_to_be_printed:
        words = ''
        for word in line:
            if word==' ':
                words += word
            else:
                words += word['pre_control']+word['txt']+word['post_control']
        lines+=words+'\n'
        no_of_lines_printed+=1
    words=''
    for k,v in command_options.items():
        words+=k+":"+v+' '
    if len(words) > os.get_terminal_size().columns:
        pass 
    else:
        words += ' ' * ( os.get_terminal_size().columns - len(words) ) 
    lines+=words+'\n'
    no_of_lines_printed+=1
    if args.screencontrol:
        for _ in range(os.get_terminal_size().lines - no_of_lines_printed - 5): 
            lines+=(' '*os.get_terminal_size().columns)+'\n'
    print(lines)
    command = ''
    if g_target_device == "windows":
        command = getch().decode("utf-8")
    else:
        command = getch()
    return command

@debug_gate
def initiate_params(g_screen_current_obj):
    g_screen_current_obj['cell_properties']={'margin':{'v_char':'|','h_char':'-','units':0},'padding':{'units':0,'char':' '},'border':{'char':' ','units':0}}

@debug_gate
def initialize_tree_params(g_screen_obj):
    '''only initialize params must be here anything that changes should not be here only STATIC'''
    command_options = { 'i j k l': "scroll", 'q' : "quit", "p": "popup" , "s": "random", "h" : "highlight", "m": "minimize", "x" : "hide", "t": "travel"}
    mode=g_screen_obj['active_obj']
    g_screen_obj[mode]=dict()
    initiate_params( g_screen_obj[mode] )
    if mode == "tree" : 
        command_options = { **command_options,  **{ 'n': 'next', "e": "ephemeral", "c": "calendar" , "r": "reload", "v": "visited on", "u": "unhide all"} }
        table_properties={'height':None,'width':None,'w_size':20,'h_size' : 1,'pre_dots' : 1,'post_dots' : 2, 'pre_dot_char': '-', 'post_dot_char': '-', 'pre_fill_name': '-', 'post_fill_name': '-', 'default_color': 'WHITE' }
    elif mode == "ephemeral_tree":
        command_options = { **command_options, **{ 'b': "Go back to normal tree" } }
        table_properties={'height':None,'width':None,'w_size':15,'h_size' : 1,'pre_dots' : 0,'post_dots' : 1, 'pre_dot_char': ' ', 'post_dot_char': ' ', 'pre_fill_name': ' ', 'post_fill_name': ' ', 'default_color': 'GREEN' }
    elif mode == "vertical_tree":
        command_options = { 'q' : "q for quit", "p": "popup" , "r": "rndm",  "h" : "highlight"}
        command_options = { **command_options,  **{ 'n': 'move to next file' } }
        table_properties={'height': None,'width':None,'default_color': 'WHITE', 'w_size':100,'h_size' : 1 }
    elif mode == "calendar":
        command_options = { **command_options, **{ 'b': "Go back to normal tree" } }
        table_properties={'height':None,'width':None,'w_size':15,'h_size' : 10,'pre_dots' : 0,'post_dots' : 1, 'pre_dot_char': ' ', 'post_dot_char': ' ', 'pre_fill_name': ' ', 'post_fill_name': ' ', 'default_color': 'GREEN' }
    g_screen_obj[mode]['table_properties']=table_properties
    g_screen_obj[mode]['command_options']=command_options

@debug_gate
def initialize_vertical_tree_params(g_screen_obj):
    '''only initialize params must be here anything that changes should not be here only STATIC'''
    command_options = { 'q' : "q for quit", "p": "popup" , "s": "some pop",  "h" : "highlight"}
    mode=g_screen_obj['active_obj']
    g_screen_obj[mode]=dict()
    initiate_params( g_screen_obj[mode] )
    height = -1
    width  = -1
    #height = 5
    #width = 30
    command_options = { **command_options,  **{ 'n': 'move to next file', "c": "custom_input" } }
    table_properties={'height':height,'width':width,'default_color': 'YELLOW', 'w_size':100,'h_size' : 1 }
    g_screen_obj[mode]['table_properties']=table_properties
    g_screen_obj[mode]['command_options']=command_options
    
@debug_gate
def initialize_popup_params(g_screen_obj):
    #print("initialize_popup_params")
    mode=g_screen_obj['active_obj']
    g_screen_obj[mode]=dict()
    initiate_params( g_screen_obj[mode] )
    g_screen_obj[mode]['cell_properties']['margin']={'v_char':'|','h_char':'-','units':1}#dont add vertical character difficult to copy
    #g_screen_obj[mode]['cell_properties']['border']= {'units':1,'char': '*'}
    #g_screen_obj[mode]['cell_properties']['padding']={'units':1,'char': '&'}
    command_options= { 'i j k l': "scroll", #not command option keys must be space separated
        'n' : 'next line',
        'w' : 'next word',
        'h' : 'hide answer',
        'c' : 'x popup show tree', 
        'r' : 'remember',
        'q' : "quit"
        }
    table_properties={'height': None,'width': None , 'default_color': 'WHITE', 'popup_width_height': 'default'}
    g_screen_obj[mode]['table_properties']=table_properties
    g_screen_obj[mode]['command_options']=command_options    

g_screen_obj=dict()
g_clear_screen_first_time=True
@debug_gate
def screen_coordinator(mode, data_table=None ,context_properties=None): #except for mode all other params should be used only for initialization
    if mode not in g_context['accepted_mode']: raise Exception("the mode {} is not one of the accepted values {}".format(mode,g_context['accepted_mode']))
    global g_clear_screen_first_time
    if g_clear_screen_first_time and args.screencontrol:
        g_clear_screen_first_time=False
        for _ in range(os.get_terminal_size().lines): print()
    #parts that need to be refreshed each time
    g_screen_obj['active_obj']=None
    command_properties = { 'w_shift': 0, 'h_shift': 0, 'option': '', 'default_shift': 3}
    if mode in [ 'calendar','tree', 'ephemeral_tree', 'vertical_tree' ]:
        g_screen_obj['active_obj']= mode
        if ( mode not in g_screen_obj):
            initialize_tree_params(g_screen_obj)
        g_screen_obj[mode] = {**g_screen_obj[mode],**{  'data_table': data_table,'context_properties': context_properties, 'table_to_be_printed': None }}
        g_screen_obj[mode]['command_properties'] = tree_command_properties = { **command_properties, **{ 'highlight': None } } 
        #print(data_table)
        #print(context_properties.keys())
        #input()
        command_options=g_screen_obj[mode]['command_options']
        command_dict={ 'command': None, 'command_attribute' : None}
        while tree_command_properties['option'] not in  ['n','r']:
            height = os.get_terminal_size().lines - 8
            width  = os.get_terminal_size().columns
            g_screen_obj[mode]['table_properties']['height']=height
            g_screen_obj[mode]['table_properties']['width']=width
            g_screen_obj[mode]['table_to_be_printed'] = refresh_tree_print_table(mode, tree_command_properties, command_dict)
            g_screen_obj[mode]['command_properties'] = tree_command_properties
            g_screen_obj[mode]['command_dict'] = command_dict
            command = display_table()
            #reset per cycle 
            if command_dict['command'] == "h" and '_initiator' in tree_command_properties['highlight'] and tree_command_properties['highlight']['_initiator'] == "t": 
                tree_command_properties['w_shift'] = tree_command_properties['h_shift'] = 0
            command_attribute = None
            if  (command in ['c','p','h','x'] and command in command_options) or ( command in ['i','j','k','l'] and g_target_device == "phone" ): # custom , then revert to normal input 
                if command in ['p']: 
                    if tree_command_properties['highlight'] and '_print_arr_id' in tree_command_properties['highlight']:
                        for temp in g_screen_obj[mode]['state_of_table']['selected_visible_items']:
                            if temp['obj']['id'] == tree_command_properties['highlight']['_print_arr_id']:
                                command_attribute = temp['obj']['_print_arr_name'] 
                                break
                        #command_attribute = tree_command_properties['highlight']['_print_arr_name']
                    else:
                        command_attribute = input('enter id seen in screen <id>:<name> ').rstrip()
                if command in ['x']: command_attribute = input('enter id seen in screen <id>:<name> ').rstrip()
                if command == 'c': command_attribute = input('enter year:').rstrip()
                if command == 'h': command_attribute = input('enter comma separated text').rstrip()
                if command in ['i','j','k','l']  and g_target_device == "phone": 
                    command_attribute = "5"
            command_dict = { 'command': command, 'command_attribute' : command_attribute}
            tree_screen_action_on_command(command_dict,tree_command_properties,command_options)
            #reset per cycle 
            if command_dict['command'] not in ['i','j','k','l','p','h','v']: tree_command_properties['highlight']=None
        #teardown
        if command!="r": del(g_screen_obj[mode]) #do not tear down when it is just a reload
    '''if mode in [ 'vertical_tree' ]:
        g_screen_obj['active_obj']= mode
        if ( mode not in g_screen_obj):
            initialize_vertical_tree_params(g_screen_obj)
        g_screen_obj[mode] = {**g_screen_obj[mode],**{  'data_table': data_table,'context_properties': context_properties, 'table_to_be_printed': None }}
        #print(data_table)
        #print(context_properties.keys())
        #input()
        command_options=g_screen_obj[mode]['command_options']
        while command_properties['option'] != 'n':
            g_screen_obj[mode]['table_to_be_printed'] = refresh_vertical_tree_print_table(command_properties)
            command = display_table()
            command_attribute = None
            if command in ['c','p']: # custom , then revert to normal input 
                if command == 'p': command_attribute = input('enter id of popup seen in screen <id>:<name> ').rstrip()
                if command == 'c': command_attribute = input(' tbd ').rstrip()
            command_dict = { 'command': command, 'command_attribute' : command_attribute}
            vertical_tree_screen_action_on_command(command_dict,command_properties,command_options)
        #teardown
        del(g_screen_obj[mode])'''
    if mode == 'popup':
        g_screen_obj['active_obj']='popup'
        if ( mode not in g_screen_obj):
            initialize_popup_params(g_screen_obj)
        g_screen_obj[mode] = {**g_screen_obj[mode],**{'data_table': data_table,'context_properties': context_properties, 'table_to_be_printed': None }}        
        g_screen_obj[mode]['command_properties'] = popup_command_properties = { **command_properties } 
        #print(context_properties)
        if context_properties['who_is_on_screen'] == 'tree':
            g_screen_obj[mode]['command_options']={**g_screen_obj[mode]['command_options'] , **{'p': "pin"} }
        else:
            if 'p' in g_screen_obj[mode]['command_options']: del( g_screen_obj[mode]['command_options']['p'] )
        command_options=g_screen_obj[mode]['command_options']
        command_dict={ 'command': None, 'command_attribute' : None}
        while popup_command_properties['option'] != 'q':
            if  g_screen_obj[mode]['table_properties']['popup_width_height'] == "text_based":
                height = width = -1
            else:
                height = os.get_terminal_size().lines - 8
                width  = os.get_terminal_size().columns
            g_screen_obj[mode]['table_properties']['height']=height
            g_screen_obj[mode]['table_properties']['width']=width
            g_screen_obj[mode]['table_to_be_printed'] = refresh_popup_print_table(popup_command_properties, command_dict)
            command = display_table(False,{'x':0 , 'y': 3})
            #command = display_table()
            command_attribute = None
            if command in ['i','j','k','l'] and g_target_device == "phone" :
                command_attribute = "2"
            if command in ['r']: 
                next_visit_in = input('enter next_visit_in days - 0:remove enter:retain').rstrip().lstrip()
                if not next_visit_in: next_visit_in = 9999
                next_visit_in = int(next_visit_in)
                command_attribute = { 'id': context_properties['base_data']['id'] , 
                                      'next_visit_in' : next_visit_in, 
                                      'filename' : os.path.basename( context_properties['base_data']['_filename'].split('.')[0] ) 
                                    }
            command_dict = { 'command': command, 'command_attribute' : command_attribute}
            popup_screen_action_on_command(command_dict,popup_command_properties,command_options, context_properties)
        del(g_screen_obj[mode])
    return g_screen_obj

@debug_gate
def popup_screen_action_on_command(command_dict, command_properties,command_options, context_properties):
    command = command_dict['command']
    command_attribute = command_dict['command_attribute']
    valid_command_options = [ i.split(' ') for i in command_options.keys() ]
    valid_command_options = [j for i in valid_command_options for j in i]
    if command not in valid_command_options: return
    command_properties['h_shift'] = 0
    command_properties['w_shift'] = 0
    if command == 'q':
        end_action()
    if command == 'n': #handled in refresh_popup_print_table
        return  
    if command == 'w': #handled in refresh_popup_print_table
        return 
    if command == 'h': #handled in refresh_popup_print_table
        return 
    if command == 'c':
        #g_screen_obj['popup']['state_of_table'] = { 'start_x': 0, 'start_y': 0 } # state must be reset, after trying ways to do it in refresh pop this seems the best way else its challengig
        command_properties['option'] = 'q'
        return
    if command in ['p']:
        obj = context_properties['base_data']
        build_tree_from_popup( obj )
    if command == 'r':
        #g_screen_obj['popup']['state_of_table'] = { 'start_x': 0, 'start_y': 0 } # state must be reset, after trying ways to do it in refresh pop this seems the best way else its challengig
        memory_controller( 'update', **command_attribute )
        return   
    if command in ['v']:
        obj = context_properties['base_data']
        build_tree_from_popup( obj )
    if command in ['i', 'j', 'k', 'l']:
        shift_value = 1
        if command_attribute and str.isnumeric( command_attribute.rstrip().lstrip() ):
            shift_value = int(command_attribute.rstrip().lstrip())
        elif g_target_device == "phone": 
            shift_value = 6
        else:
            shift_value = 1
        if command == 'i': command_properties['h_shift'] = shift_value
        elif command == 'k': command_properties['h_shift'] = - shift_value
        if command == 'j': command_properties['w_shift'] = shift_value
        elif command == 'l': command_properties['w_shift'] = - shift_value

@debug_gate
def vertical_tree_screen_action_on_command(command_dict, command_properties,command_options):
    global g_screen_obj
    command = command_dict['command']
    command_attribute = command_dict['command_attribute']
    valid_command_options = [ i.split(' ') for i in command_options.keys() ]
    valid_command_options = [j for i in valid_command_options for j in i]
    if command not in valid_command_options: return
    command_properties['h_shift'] = 0
    command_properties['w_shift'] = 0
    if command == 'q': sys.exit(0)
    if command == 'b': 
        command_properties['option'] = 'n'
        return
    if command in [ 'p','s']: 
        last_active_obj = g_screen_obj['active_obj']
        #print('==**===',last_active_obj)
        popup_display( command_attribute )
        #print('= set xx====',last_active_obj)
        g_screen_obj['active_obj']=last_active_obj
        return   
    if command == 'n': 
        command_properties['option'] = 'n'
        return 
    if command == 'e': 
        last_active_obj = g_screen_obj['active_obj']
        #print('==** ===',last_active_obj)
        tree_display(g_ephemeral_tree, g_ephemeral_tree[0], 'ephemeral_tree')
        #print('= set yy====',last_active_obj)
        g_screen_obj['active_obj']=last_active_obj
        return

@debug_gate
def tree_screen_action_on_command(command_dict, command_properties,command_options ):
    #print(command_dict, command_properties,command_options )
    global g_screen_obj
    active_obj = g_screen_obj['active_obj']
    g_screen_tree_obj = g_screen_obj[active_obj]
    data_table = g_screen_tree_obj['data_table']
    table_properties = g_screen_tree_obj['table_properties']
    context_properties = g_screen_tree_obj['context_properties']
    cell_properties = g_screen_tree_obj['cell_properties']
    
    command = command_dict['command']
    command_attribute = command_dict['command_attribute']
    valid_command_options = [ i.split(' ') for i in command_options.keys() ]
    valid_command_options = [j for i in valid_command_options for j in i]
    if command not in valid_command_options: return
    command_properties['h_shift'] = 0
    command_properties['w_shift'] = 0
    if command == 'q': end_action()
    if command == 'b': 
        command_properties['option'] = 'n'
        return
    if command == 'r': # its equiavalent to n which quits but main_coordinator will deal with him
        command_properties['option'] = 'r'
        return
    if command == 'h': 
        command_properties['highlight']= { 'mode': 'txt', 'param': command_attribute }
        return
    if command == 'v': #will be handled in generate_cell_tree_text
        command_dict['command']='h'
        command_properties['highlight']= { 'mode': 'date', 'param': None } 
        return
    if command == 's': 
        pop_rand_obj = pick_random_selected_item()[0]['obj']
        command_dict['command']='h'
        command_properties['highlight']= { 'mode': 'id', 'param': pop_rand_obj['id'], '_print_arr_id': pop_rand_obj['id'] } # _print_arr_name is used for subsequent popup
        #print(command_dict,command_properties)
        return
    if command in [ 'm', 'x', 'u' ]: 
        #will be taken care by refresh_tree_print_table
        return
    if command in [ 'p']: 
        last_active_obj = g_screen_obj['active_obj']
        #print('==**===',last_active_obj)
        popup_display( command_attribute )
        #print('= set xx====',last_active_obj)
        g_screen_obj['active_obj']=last_active_obj
        return   
    if command in ['t']:
        travel_obj = random.choice([j for i in data_table for j in i if j ])
        x, y = get_index_of_table ( travel_obj ,  data_table )
        g_screen_tree_obj['state_of_table']['start_x'] = x
        g_screen_tree_obj['state_of_table']['start_y'] = y
        command_properties['h_shift'] = - int(table_properties['height']/2)
        command_properties['w_shift'] = - int(table_properties['width']/2)
        command_dict['command']='h'
        command_properties['highlight']= { 'mode': 'id', 'param': travel_obj['id'], '_print_arr_id': travel_obj['id'], '_initiator' : 't' } # _print_arr_name is used for subsequent popup
    if command in [ 'c']: 
        if command_attribute.rstrip().lstrip() and str.isnumeric( command_attribute.rstrip().lstrip() ) :
            last_active_obj = g_screen_obj['active_obj']
            filename = build_calendar_tree_from_result(int(command_attribute))
            tree=g_context[filename]['tree']
            tree_display(tree, tree[0], 'calendar')
            g_screen_obj['active_obj']=last_active_obj
        return  
    if command == 'n': 
        command_properties['option'] = 'n'
        return 
    if command == 'e': 
        last_active_obj = g_screen_obj['active_obj']
        #print('==** ===',last_active_obj)
        tree_display(g_ephemeral_tree, g_ephemeral_tree[0], 'ephemeral_tree')
        #print('= set yy====',last_active_obj)
        g_screen_obj['active_obj']=last_active_obj
        return
    if command in ['i', 'j', 'k', 'l']:
        shift_value = 1
        if command_attribute and str.isnumeric( command_attribute.rstrip().lstrip() ):
            shift_value = int(command_attribute.rstrip().lstrip())
        elif g_target_device == "phone": 
            shift_value = 6
        else:
            shift_value = 1
        if command == 'i':
            command_properties['h_shift'] = shift_value
        elif command == 'k':
            command_properties['h_shift'] = - shift_value
        if command == 'j':
            command_properties['w_shift'] = shift_value
        elif command == 'l':
            command_properties['w_shift'] = - shift_value

def command_effect():
    pass

@debug_gate
def refresh_popup_print_table(command_properties, command_dict):
    global g_screen_obj
    g_screen_tree_obj = g_screen_obj['popup']
    data_table = g_screen_tree_obj['data_table']
    table_properties = g_screen_tree_obj['table_properties']
    context_properties = g_screen_tree_obj['context_properties']
    cell_properties = g_screen_tree_obj['cell_properties']
    if 'state_of_table' not in  g_screen_tree_obj:
        if args.qamode:
            hide_answer_mode = hide_line_answer = True 
        else:
            hide_answer_mode = hide_line_answer = False
        g_screen_tree_obj['state_of_table'] = { 'init': True, 'start_x': 0, 'start_y': 0 , 'word': 99999, 'line': -2, 'total_word_in_line': -1, 'total_line': -1 ,'hide_answer_mode': hide_answer_mode, 'hide_line_answer': hide_line_answer, 'secret_in_line': False } # line is -2 because when its -1 it will show all x in the generate_cell_box_text function
    if command_dict['command']=='h': 
        g_screen_tree_obj['state_of_table']['hide_answer_mode'] = True
        g_screen_tree_obj['state_of_table']['hide_line_answer'] = True
    if command_dict['command']=='n' or ( g_screen_tree_obj['state_of_table']['init'] and args.qamode ):  
        if ( g_screen_tree_obj['state_of_table']['init'] or command_dict['command']=='h' ):
            #change of state so dont calculate anything 
            pass
        else:
            if g_screen_tree_obj['state_of_table']['hide_answer_mode']: 
                if g_screen_tree_obj['state_of_table']['hide_line_answer']:
                    if g_screen_tree_obj['state_of_table']['secret_in_line']: 
                        g_screen_tree_obj['state_of_table']['line'] -= 1
                        g_screen_tree_obj['state_of_table']['hide_line_answer'] = False
                else:
                    g_screen_tree_obj['state_of_table']['hide_line_answer'] = True
        if g_screen_tree_obj['state_of_table']['word'] < g_screen_tree_obj['state_of_table']['total_word_in_line']:
            g_screen_tree_obj['state_of_table']['word'] = 99999
        else:
            g_screen_tree_obj['state_of_table']['line'] += 1
            if  g_screen_tree_obj['state_of_table']['total_line'] >= 0 and g_screen_tree_obj['state_of_table']['line'] >= g_screen_tree_obj['state_of_table']['total_line']:
                g_screen_tree_obj['state_of_table']['line'] = -1
    if command_dict['command']=='w':  
        g_screen_tree_obj['state_of_table']['hide_answer_mode'] = False #hiding secrets wont work in word mode KEEP IT SIMPLE DONT OVER DO, deactivate if needed press h again
        g_screen_tree_obj['state_of_table']['hide_line_answer'] = False
        if g_screen_tree_obj['state_of_table']['word'] >= g_screen_tree_obj['state_of_table']['total_word_in_line']:
            g_screen_tree_obj['state_of_table']['word'] = 0
            g_screen_tree_obj['state_of_table']['line'] += 1
        else:
            g_screen_tree_obj['state_of_table']['word'] += 1
    state_of_table = g_screen_tree_obj['state_of_table']
    print_table, new_state_of_table = build_popup_array_table(state_of_table, data_table,table_properties,command_properties,cell_properties)
    #print_table=[''.join(line) for line in print_table]
    g_screen_tree_obj['state_of_table'] = { **state_of_table, **new_state_of_table}
    #print(g_screen_tree_obj['state_of_table'])
    g_screen_tree_obj['state_of_table']['init'] = False
    return print_table

@debug_gate
def hide_all_children():
    if g_screen_obj['active_obj'] != "tree": raise Exception('only tree mode can invoke hide_all_children')
    child_key = g_screen_obj['tree']['context_properties']['child_key']
    if '_node_with_hidden_children' in g_screen_obj['tree']:
        for i in g_screen_obj['tree']['_node_with_hidden_children']:
            hide_children(i,g_screen_obj['tree']['context_properties']['base_data'],key=child_key)
        del(g_screen_obj['tree']['_node_with_hidden_children'])
    else:
        g_screen_obj['tree']['_node_with_hidden_children'] = []
        for i in g_screen_obj['tree']['context_properties']['base_data']:
            if child_key + '_hidden' in i:
                g_screen_obj['tree']['_node_with_hidden_children'].append( i )
                hide_children(i,g_screen_obj['tree']['context_properties']['base_data'],key=child_key)
    
@debug_gate
def hide_children(obj,tree,key='children'):
    all_children=get_all_children(tree,[obj['id']],key)
    hidden_child_name = key + '_hidden' # need to separate hidden children for normal and ephemeral
    if hidden_child_name in obj:
        obj[key]=obj[hidden_child_name]
        obj['name']=obj['_hidden_name']
        del(obj[hidden_child_name])
    else:
        obj[hidden_child_name]=obj[key]
        obj['_hidden_name']=obj['name']
        obj['name']='x|'+obj['name']
        obj[key]=[]
    #print(obj)

@debug_gate
def refresh_tree_print_table(mode, *args):
    if mode == "vertical_tree":
        return refresh_vertical_tree_print_table(mode, *args)
    else:
        return refresh_graph_tree_print_table(mode, *args)

@debug_gate
def refresh_graph_tree_print_table(mode, command_properties, command_dict):
    global g_screen_obj
    g_screen_tree_obj = g_screen_obj[mode]
    data_table = g_screen_tree_obj['data_table']
    table_properties = g_screen_tree_obj['table_properties']
    context_properties = g_screen_tree_obj['context_properties']
    cell_properties = g_screen_tree_obj['cell_properties']
    if 'state_of_table' not in g_screen_tree_obj:
        start_x, start_y = get_index_of_table( context_properties['start_node'], data_table )
        g_screen_tree_obj['state_of_table'] = { 'start_x': start_x, 'start_y': start_y, 'first_w_block_in_scope': table_properties['w_size'], 'first_h_block_in_scope': table_properties['h_size'] }
    if command_dict['command']=='m':
        if '_h_size' in table_properties:
            table_properties['h_size']=table_properties['_h_size']
            g_screen_tree_obj['state_of_table']['first_h_block_in_scope']=g_screen_tree_obj['state_of_table']['_first_h_block_in_scope']
            del(g_screen_tree_obj['state_of_table']['_first_h_block_in_scope'])
            del(table_properties['_h_size'])
        else:
            table_properties['_h_size']=table_properties['h_size']
            table_properties['h_size']=1
            g_screen_tree_obj['state_of_table']['_first_h_block_in_scope'] = g_screen_tree_obj['state_of_table']['first_h_block_in_scope']
            g_screen_tree_obj['state_of_table']['first_h_block_in_scope'] = 1
    if command_dict['command'] in ['x','u']:
        if command_dict['command'] == 'x':
            for i in g_screen_tree_obj['state_of_table']['selected_visible_items']:
                if i['obj']['_print_arr_name']==command_dict['command_attribute'].lstrip().rstrip():
                    hide_children(i['obj'], g_screen_tree_obj['context_properties']['base_data'],g_screen_tree_obj['context_properties']['child_key'])
        if command_dict['command'] == 'u':
            hide_all_children()
        g_screen_tree_obj['data_table'] = build_data_table_from_tree(
            parent_node=g_screen_tree_obj['context_properties']['start_node'],
            tree=g_screen_tree_obj['context_properties']['base_data'],
            child_key=g_screen_tree_obj['context_properties']['child_key'])
        data_table = g_screen_tree_obj['data_table']
    state_of_table = g_screen_tree_obj['state_of_table']
    print_table, new_state_of_table = build_tree_array_table(state_of_table, data_table,table_properties, command_properties, context_properties, cell_properties)
    fill_vertical_dots(context_properties['base_data'],new_state_of_table['selected_visible_items'], print_table,table_properties['width'],table_properties['height'],table_properties['h_size'],table_properties['w_size'],table_properties['default_color'], [],context_properties['child_key'])
    #since this table is a list of list make it a list of line 
    #print_table=[''.join(line) for line in print_table]
    g_screen_tree_obj['state_of_table'] = { **state_of_table, **new_state_of_table}
    return print_table

@debug_gate
def refresh_vertical_tree_print_table(mode, command_properties, command_dict):
    global g_screen_obj
    #print(command_properties,command_dict)
    g_screen_tree_obj = g_screen_obj['vertical_tree']
    data_table = g_screen_tree_obj['data_table']
    table_properties = g_screen_tree_obj['table_properties']
    context_properties = g_screen_tree_obj['context_properties']
    cell_properties = g_screen_tree_obj['cell_properties']
    if 'state_of_table' not in  g_screen_tree_obj:
        g_screen_tree_obj['state_of_table'] = { 'start_x': 0, 'start_y': 0 }
    state_of_table = g_screen_tree_obj['state_of_table']
    print_table, new_state_of_table  = build_vertical_tree_array_table(state_of_table, data_table,table_properties,command_properties,context_properties,cell_properties)
    #print_table=[''.join(line) for line in print_table]
    g_screen_tree_obj['state_of_table'] = { **state_of_table, **new_state_of_table}
    #print(print_table)
    return print_table

@debug_gate
def get_index_of_table(item,lst: []):
    for n,i in enumerate(lst):
        for m,j in enumerate(i):
            if j and 'id' in j and j['id'] == item['id']:
                return [n,m]
    print('could not get index of item')
    sys.exit(1)

@debug_gate
def build_data_table_from_tree(parent_node,tree,child_key='_children'):
    table=[[parent_node]]
    items=[parent_node]
    root_row = None
    for i in items:
        #print('llll',i['name'])
        childrens = node_search_by_id(tree, i[child_key] )
        l = len( childrens )
        m = l // 2 
        middle = l % 2
        if l > 0: 
            x,y = get_index_of_table( i, table )
            if not root_row: root_row = x 
            #print(x,y)
            table[x].append(None)
            item_no_after_middle = 1
            for n_child, e_child in enumerate(childrens):
                #print('child is',e_child['name'])
                e_child = [ e_child ]
                items+=e_child
                if middle == 1 and n_child == m :
                    #print('...appending ', e_child)
                    table[x][-1] = e_child[0] # not a list since we said its a None and already assigned a palce
                elif n_child < m :
                    #print('...inserting before',table[x],'...', [ None for i in range(len(table[x])-1) ]   +  e_child )
                    table.insert(x, [ None for i in range(len(table[x])-1) ]   +  e_child   )
                    x+=1
                else:
                    #print('...inserting after','...',[ None for i in range(len(table[x])-1) ]   +  e_child )
                    table.insert(x+item_no_after_middle, [ None for i in range(len(table[x])-1) ] +  e_child  )
                    item_no_after_middle += 1
                '''for temp in table: 
                    for j in temp: 
                        if j:
                            print(j['name'],end='')
                        else:
                            print('--------',end='')
                    print()'''
            #input()
    #normalize table to have all rows and cols of same lenth
    max_cols = -1 
    for i in table:
        max_cols = max ( max_cols, len(i) )
    for i in table:
            i += [None] * ( max_cols - len(i) )
    '''for n,i in enumerate(table):
        for m,j in enumerate(i):
            name=None if not j else j['name']
            print('###',n,m,name,end='')
        print()'''
    return table

@debug_gate
def calculate_table_block_size( curr_arr_pos, first_block_in_scope , block_size, shift_value, total_size ):
    #print({'curr_arr_pos': curr_arr_pos, 'first_block_in_scope': first_block_in_scope, 'block_size': block_size, 'shift_value': shift_value, 'total_size': total_size})
    values = []
    if shift_value > 0 : 
        how_much_can_curr_arr_give =  first_block_in_scope
        #print('how_much_can_curr_arr_give', how_much_can_curr_arr_give)
        how_much_more_is_needed = how_much_can_curr_arr_give - shift_value
        #print('how_much_more_is_needed', how_much_more_is_needed)
        if how_much_more_is_needed > 0 :
            #print('----- no right shift -----')
            first_block_in_scope = how_much_more_is_needed
            curr_arr_pos = curr_arr_pos
        elif abs(how_much_more_is_needed) % block_size >= 0 :
            #print('!!!!! trigger right shift !!!!!')
            first_block_in_scope = block_size - ( abs(how_much_more_is_needed) % block_size )
            curr_arr_pos +=  abs(how_much_more_is_needed) // block_size + 1
    elif shift_value < 0 :
        how_much_can_curr_arr_give =  block_size -  first_block_in_scope
        #print('how_much_can_curr_arr_give', how_much_can_curr_arr_give)
        how_much_more_is_needed = how_much_can_curr_arr_give - abs(shift_value)
        #print('how_much_more_is_needed', how_much_more_is_needed)
        if how_much_more_is_needed >= 0:
            #print('----- no left shift -----')
            first_block_in_scope += abs(shift_value)
            curr_arr_pos = curr_arr_pos
        elif abs(how_much_more_is_needed) % block_size >= 0 :
            #print('!!!!! trigger left shift !!!!!')
            first_block_in_scope = ( abs(how_much_more_is_needed) % block_size )
            first_block_in_scope = block_size if first_block_in_scope == 0 else first_block_in_scope
            #handle special case if the value is say 5 and block size is 5 do not increment by 1 as it will push it further add -1 
            curr_arr_pos -=  ( abs(how_much_more_is_needed) - 1 ) // block_size + 1
        
    values.append( { 'p' : curr_arr_pos, 'b' : first_block_in_scope } )
    
    running_total_size = first_block_in_scope
    running_arr_pos = curr_arr_pos + 1
    while ( total_size - running_total_size ) > 0:
        #print( total_size - running_total_size )
        if block_size > ( total_size - running_total_size ):
            block_size = ( total_size - running_total_size )
        values.append( { 'p' : running_arr_pos, 'b' : block_size } )
        running_arr_pos += 1
        running_total_size += block_size
        #print(values)
    return curr_arr_pos, values, first_block_in_scope

generated_node_ids = { 'ids': [i+j for i in list('abcdefghijklmnopqrstuvwxyz0123456789') for j in list('abcdefghijklmnopqrstuvwxyz0123456789') ], 'curr_id': 0 }
@debug_gate
def generate_node_id():
    global generate_node_ids
    id_list = generated_node_ids['ids']
    generate_value = id_list [ generated_node_ids['curr_id'] ]
    if generated_node_ids['curr_id'] + 1  >= len( id_list ):
        generated_node_ids['curr_id'] = 0
    else:
        generated_node_ids['curr_id'] += 1
    return generate_value

@debug_gate
def fill_surround_block(mode,table,cell_properties):
    cp=cell_properties
    units=cp[mode]['units']
    start_x = cp['start_x']
    end_x = cp['end_x']
    start_y = cp['start_y']
    end_y = cp['end_y']
    if mode=='margin':
        h_char = cp[mode]['h_char']
        v_char = cp[mode]['v_char']
    if mode in ['padding','border']:
        h_char = cp[mode]['char']
        v_char = cp[mode]['char']
    for _ in range(units):
        for i in range(start_y, end_y+1): 
            make_table_entry( table,i,start_x, word_obj_to_letter_obj(color_word(v_char,"YELLOW",False).colored_obj)[0] )
            make_table_entry( table,i, end_x, word_obj_to_letter_obj(color_word(v_char,"YELLOW",False).colored_obj)[0] )
        for i in range(start_x, end_x+1): 
            #make_table_entry( table, start_y, i, {'txt': h_char, 'pre_control': '\x1b[33m', 'post_control': '\x1b[0m' } )
            make_table_entry( table, start_y, i, word_obj_to_letter_obj(color_word(h_char,"YELLOW",False).colored_obj)[0])
            make_table_entry( table, end_y, i, word_obj_to_letter_obj(color_word(h_char,"YELLOW",False).colored_obj)[0] )


@debug_gate
def fetch_links(filename,id):
    #print('fetch_links',filename,id)
    #print(filename,g_context[filename].keys())
    for item in g_context[filename]['tree']:
        if item['id']==id:
            return item 

@debug_gate
def nested_links_to_dfs_flat_array(node,output,level=-1,seeing_for_first_time=True,is_root=True): #is top node means when a node is seen for first time it will be true when after travel graph comes back to it we will set it to false
    for each_data in node['_resolved_data']:
        if each_data['type'] == 'default':
            output.append({'level': level,'is_root': is_root, 'seeing_for_first_time': seeing_for_first_time, 'data': each_data['txt'], '_filename': os.path.basename(node['_filename']), 'name': node['name']})
        elif each_data['type'] == 'link':
            nested_links_to_dfs_flat_array(each_data,output,level+1,True,False)
        else:
            raise Exception('Unknown type of data in nested_links_to_dfs_flat_array, its neither default not link {}'.format(each_data))
        seeing_for_first_time = False
    if not is_root:
        output.append({'level': level, 'is_root': is_root, 'seeing_for_first_time': seeing_for_first_time, 'data': '<eol>\n', '_filename': os.path.basename(node['_filename']), 'name': node['name']})
    return output

@debug_gate
def find_cycle_and_update_data(leaf,status,assumed_status,track_stack=[]):
    #print('processing node', leaf)
    status[ os.path.basename(leaf['_filename']) + leaf['id'] ] = True 
    assumed_status[ os.path.basename(leaf['_filename']) + leaf['id'] ] = True 
    #if '_resolved_data' not in leaf: leaf['_resolved_data']=[] this causes addition to data each time it is referenced
    leaf['_resolved_data']=[]
    for each_data in leaf['data']:
        #print("processing each data",each_data)
        if each_data['type'] == 'default':
            #print('appending data',each_data)
            leaf['_resolved_data'].append(each_data)
        elif each_data['type'] == 'link':
            node = fetch_links(each_data['filename'],each_data['id'])
            track_stack.append({'filename': os.path.basename(node['_filename']),'id': node['id']})
            #print('identified link',node)
            if each_data['filename']+each_data['id'] not in status:
                res_obj = find_cycle_and_update_data(node,status,assumed_status,track_stack)
                #print('res_obj is ',res_obj)
                leaf['_resolved_data'].append({**each_data,**res_obj})
            elif each_data['filename']+each_data['id'] in assumed_status:
                if  assumed_status[each_data['filename']+each_data['id']]:
                    raise Exception('cycle when connecting the following path:{}'.format(track_stack))
                else:
                    res_obj = fetch_links(each_data['filename'],each_data['id'])
                    leaf['_resolved_data'].append({**each_data,**res_obj})
                #input('found data already visited but not cycle curr node {} now has {}'.format(link['filename'], [i['_filename']+i['name'] for i in node['_temp_link_data']] ))
            assumed_status[  each_data['filename']+each_data['id'] ] = False 
            #print(status,assumed_status)
    #print('final',leaf)
    #print(track_stack)
    return leaf
    
def temp_dfs_print(node):
    #print( '===', node['_filename'],node['id'] )
    if '_temp_link_data' in node:
        for i in node['_temp_link_data']:
            temp_dfs_print(i)

@debug_gate
def resolve_links_and_data(node):
    #print("resolving node",node)
    #print(node)
    # if you resolved already dont resolve again because then the resolved text keep on appending 
    if '_resolved_data' in node: return node
    status = dict()
    assumed_status = dict()
    data = find_cycle_and_update_data(node,status,assumed_status)
    #input()
    return data

@debug_gate
def generate_cell_box_text(cell_obj, cell_properties):
    text = ''
    root_link_node = resolve_links_and_data(cell_obj)
    title = root_link_node['name'] + "\n" + '---------------\n'
    #temp_dfs_print(i)
    for n,i in enumerate(nested_links_to_dfs_flat_array(root_link_node,[])):
        #print([i], i['data'].split('\n'))
        level_adjusted_text = ''
        #.join([ ' '*i['level']+temp+'\n' if temp != '' else '\n'   ])
        if i['data'] == '':
            level_adjusted_text += ' '*i['level']
        else:
            each_line = i['data'].split('\n')
            for n,each_word in enumerate(each_line):
                if n+1 == len(each_line) and each_word == '' : # a\n will give ['a',''] dont want to add \n for 2 index so it becomes a\n\n
                    pass#dont do anything 
                else:
                    level_adjusted_text += ( ' '*i['level'] + each_word + '\n' )
        #print([level_adjusted_text])
        if i['is_root']:
            text+='{}'.format(level_adjusted_text)
        elif i['seeing_for_first_time']: # first loop is actual parent subsequent are link data
            text+=' '*i['level']+'<lnk>:{}:{}\n{}'.format(i['_filename'],i['name'],level_adjusted_text)
        else:
            text+='{}'.format(level_adjusted_text)
        #print([text])
    #print([text])
    all_lines = text.split('\n')
    #print(all_lines)
    cell_properties['total_line'] = len(all_lines)
    if cell_properties['line']>=-1:
        show_hide_text=''
        for n,line in enumerate(all_lines):
            #show_hide_text += ( ' '.join([ re.sub('.','-',i)  if random.randint(1,10) in [1,2,3] and i not in g_stop_words else i for i in list(re.split('\W', line)) ])  ) + '\n'
            if n <= cell_properties['line']:
                if  cell_properties['line'] == n : #do only for last line
                    words_list = list(re.split(' ', line))
                    cell_properties['total_word_in_line'] = len(words_list) - 1 #array type calculation
                    for m,word in enumerate(words_list):
                        if m <= cell_properties['word']:
                            show_hide_text += word
                        else:
                            show_hide_text += re.sub('[^\s]','x',word )
                        if len(words_list)-1 == m: 
                            show_hide_text += '\n'
                        else:
                            show_hide_text += ' '
                else:       
                    show_hide_text += line + '\n'
            else:
                show_hide_text += re.sub('[^\s]','x',line) + '\n'
    else:
        show_hide_text = text
    if cell_properties['hide_line_answer'] :
        lines = show_hide_text.split('\n')
        #print(lines,cell_properties['line'])
        if cell_properties['line']>=0 and cell_properties['line'] < len(lines):
            secret_in_focus = lines[ cell_properties['line'] ]
            #print(secret_in_focus)
            if bool( re.search ( '~\*.*?~\*', secret_in_focus ) ):
                secret_in_focus = lines[ cell_properties['line'] ]
                #lines[ cell_properties['line'] ] = re.sub('~\*.*?\*~','?',secret_in_focus)
                lines[ cell_properties['line'] ] = ''.join([j[:2]+re.sub('[^\s]','?',j[2:-2])+j[-2:] if j.startswith('~*') else j for j in  [ ''.join(i) for i in re.findall('(~\*.*?~\*)?|(\w+)|(\s+)|(\W+?)',secret_in_focus) ] ])
                if len(secret_in_focus) != len(lines[ cell_properties['line'] ]): raise Exception("possible bug when doing regex to hide answer")
                #print(lines[ cell_properties['line'] ],secret_in_focus)
                #input()
                cell_properties['secret_in_line'] = True
        else:
            cell_properties['secret_in_line'] = False
        show_hide_text = '\n'.join(lines)
    return title + show_hide_text

@debug_gate
def generate_cell_vertical_tree_text(cell_obj, cell_properties):
    cell_text_obj = cell_obj
    return (cell_text_obj['_print_arr_name'].ljust(3))+'  '*cell_text_obj['_level']+cell_text_obj['name']

@debug_gate
def generate_cell_default_text(cell_obj, cell_properties):
    cell_text_obj = cell_obj
    return cell_text_obj['name']

@debug_gate
def gather_cell_tree_text(cell_obj, cell_properties):
    #print('...',cell_obj,cell_properties)
    base_file_name = os.path.basename( cell_obj['_filename'] )
    if cell_properties['highlight'] and cell_properties['highlight']['mode']=="date":
            for i in g_context['remember_list']:
                if i['filename'] == base_file_name.split('.')[0] and i['id'] == cell_obj['id']:
                    #return datetime.strftime(i['last_visited_date'],'%d%b%Y')
                    cell_properties['_next_visit_in'] = i['next_visit_in']
                    cell_properties['_date_lag'] = (datetime.now() - i['last_visited_date'] ).days # +1 to include the day getting subracted
                    return str( cell_properties['_date_lag'] ) + ',' + str( cell_properties['_next_visit_in'] )
            cell_properties['_date_lag'] = 9999
            return '9999'
    else:
        return cell_obj['name']

@debug_gate
def generate_cell_tree_text(cell_obj, cell_properties):
    cell_text_obj = cell_obj
    active_obj = g_screen_obj['active_obj']
    table_properties=g_screen_obj[active_obj]['table_properties']
    context_properties=g_screen_obj[active_obj]['context_properties']
    pre_dots = table_properties['pre_dots']
    post_dots = table_properties['post_dots']
    pre_dot_char = table_properties['pre_dot_char']
    post_dot_char= table_properties['post_dot_char']
    pre_fill_name = table_properties['pre_fill_name']
    post_fill_name= table_properties['post_fill_name']
    child_key= context_properties['child_key']
    obj = cell_properties['obj']
    w_size = cell_properties['end_x'] - cell_properties['start_x'] + 1
    #print(name,w_size)
    post_dot_char = post_dot_char if obj[child_key] else ' ' 
    size_for_name = w_size - ( pre_dots + post_dots )
    if '_print_arr_name' not in obj: #note there is a possible bug that the ids assigned may get exhausted but 36 * 36 = 1000 nodes i am never going to have that much
        obj['_print_arr_name'] = generate_node_id()
    name = obj['_print_arr_name'] + ':' + gather_cell_tree_text(cell_obj, cell_properties) #give_color(name,'YELLOW')
    name = name[0:size_for_name]
    #name = '{:-^{size}s}'.format(name,size=size_for_name)
    # custom center justify 
    if len(name) >= size_for_name:
        pass 
    else :
        available_string_size = ( size_for_name - len(name ) ) // 2 
        available_string_odd_even = ( size_for_name - len(name ) ) % 2 
        #fill_before
        name = pre_fill_name * available_string_size + name 
        name += ( post_fill_name if obj[child_key] else ' ' ) * (available_string_size + available_string_odd_even)
    name = pre_dot_char * pre_dots + name +  post_dot_char*post_dots
    return name

@debug_gate
def generate_cell_calendar_text(cell_obj, cell_properties):
    #print(cell_obj)
    #input()
    cell_text_obj = cell_obj
    name = cell_text_obj['name']
    active_obj = g_screen_obj['active_obj']
    table_properties=g_screen_obj[active_obj]['table_properties']
    context_properties=g_screen_obj[active_obj]['context_properties']
    pre_dots = table_properties['pre_dots']
    post_dots = table_properties['post_dots']
    pre_dot_char = table_properties['pre_dot_char']
    post_dot_char= table_properties['post_dot_char']
    pre_fill_name = table_properties['pre_fill_name']
    post_fill_name= table_properties['post_fill_name']
    child_key= context_properties['child_key']
    obj = cell_properties['obj']
    w_size = cell_properties['end_x'] - cell_properties['start_x'] + 1
    #print(name,w_size)
    post_dot_char = post_dot_char if obj[child_key] else ' ' 
    size_for_name = w_size - ( pre_dots + post_dots )
    if '_print_arr_name' not in obj: #note there is a possible bug that the ids assigned may get exhausted but 36 * 36 = 1000 nodes i am never going to have that much
        obj['_print_arr_name'] = generate_node_id()
    name = obj['_print_arr_name'] + ':' + name #give_color(name,'YELLOW')
    name = name[0:size_for_name]
    #name = '{:-^{size}s}'.format(name,size=size_for_name)
    # custom center justify 
    if len(name) >= size_for_name:
        pass 
    else :
        available_string_size = ( size_for_name - len(name ) ) // 2 
        available_string_odd_even = ( size_for_name - len(name ) ) % 2 
        #fill_before
        name = pre_fill_name * available_string_size + name 
        name += ( post_fill_name if obj[child_key] else ' ' ) * (available_string_size + available_string_odd_even)
    name = pre_dot_char * pre_dots + name +  post_dot_char*post_dots
    text = ''
    unique_names = []
    root_link_node = resolve_links_and_data(cell_obj)
    '''for n,i in enumerate(nested_links_to_dfs_flat_array(root_link_node,[])):
        if n!=0: # first loop is actual parent subsequent are link data
            text+='{} '.format(i['name'])
        else:
            pass # when a linked array returns it always contains the root data, so since we already use root data as the main showing name no need to show again'''
    for n,i in enumerate(nested_links_to_dfs_flat_array(root_link_node,[])):
        #print(i)
        if not i['is_root']: # first loop is actual parent subsequent are link data
            #text+='{} '.format(i['name'])
            if ( i['name'], i['_filename'] ) not in unique_names:
                unique_names.append( ( i['name'], i['_filename'] ) )
        else:
            pass
    #print('======',name+text)
    text = ' '.join([i[0] for i in unique_names])
    return name + text

@debug_gate
def priority_color( cell_properties): #not even naming it cell because this access g_context which no cell block does
    date_lag = cell_properties['_date_lag']
    '''if date_lag == 9999 or priority == 5:
        return 'WHITE'''
    if date_lag == 9999:  return 'WHITE'
    next_visit_in = cell_properties['_next_visit_in']
    bands =  [ round(i/ ( len(g_priority) - 1 ),2) for i in range( len(g_priority) ) ] #[1.0, 0.67, 0.33, 0.0]
    bands.reverse()
    #print(bands, date_lag)
    for n,i in enumerate(bands):
        if round( date_lag / next_visit_in , 2 ) >= i : 
            break
    return g_priority[n]
    '''date_toleration = sorted(g_priority[priority])
    for n, curr_date_toleration in enumerate(date_toleration):
        curr_date_toleration_adjusted_for_confidence = curr_date_toleration +  ( date_toleration[ min ( n + confidence , len(date_toleration) - 1 ) ]  if confidence > 0  else 0 )
        if date_lag <= curr_date_toleration_adjusted_for_confidence:
            return g_priority[priority][curr_date_toleration]'''
    
@debug_gate
def highlight_cell_tree_text(colored_text,cell_properties,cell_obj):
    #print('<><><><>',cell_properties)
    highlight_properties=cell_properties['highlight']
    text=''
    root_link_node = resolve_links_and_data(cell_obj)
    tag=cell_obj['tag'] if 'tag' in cell_obj  else [] 
    for n,i in enumerate(nested_links_to_dfs_flat_array(root_link_node,[])):
        text+='{} '.format(i['name'])
        text+='{} '.format(i['data'])
    #print(text)
    #input()
    found=False
    highlight_color = 'RED'
    if highlight_properties:
        if highlight_properties['mode'] == 'txt':
            for each_highlighted_word in highlight_properties['param'].split(','):
                #input(each_highlighted_word)
                #input(text)
                if each_highlighted_word.lower() in text.lower() or any([each_highlighted_word.lower() in temp.lower() for temp in tag]):
                    found=True
        if highlight_properties['mode'] == 'id' and cell_obj['id'] == highlight_properties['param']:
            found=True
        if highlight_properties['mode'] == 'date':
            found=True
            highlight_color = priority_color( cell_properties )
        if found:
            for line in colored_text:
                for n,word in enumerate(line.colored_obj):
                    line.colored_obj[n] = color_word(word.colored_obj['word'],highlight_color)
            return True
    return False

@debug_gate
def highlight_cell_calendar_text(colored_text,cell_properties):
    #print('////////',cell_properties)
    '''for each_nested_item in nested_links_to_dfs_flat_array(cell_properties['obj'],[]):
        print(each_nested_item)
        input('+++')
        if highlight_cell_tree_text(colored_text,cell_properties,each_nested_item): break'''
    highlighted_word=cell_properties['highlight']
    if highlighted_word:
        if highlighted_word['mode'] == 'id' and cell_properties['obj']['id'] == highlighted_word['param']:
            for line in colored_text:
                for n,word in enumerate(line.colored_obj):
                    line.colored_obj[n] = color_word(word.colored_obj['word'],'RED')
        else:
            highlight_cell_tree_text(colored_text,cell_properties,cell_properties['obj'])

@debug_gate
def color_cell_tree_text(text,cell_properties):
    colored_text = color_text(text,cell_properties['default_color'],False).colored_obj
    highlight_cell_tree_text(colored_text,cell_properties,cell_properties['obj'])
    return colored_text

@debug_gate
def color_cell_popup_text(text,cell_properties):
    colored_text = color_text(text,'WHITE',True).colored_obj
    return colored_text

@debug_gate
def color_cell_calendar_text(text,cell_properties):
    colored_text = color_text(text,'WHITE',False).colored_obj
    highlight_cell_calendar_text(colored_text,cell_properties)
    return colored_text

@debug_gate
def color_cell_default_text(text,cell_properties):
    colored_text = color_text(text,'WHITE',True).colored_obj
    #print(cell_properties)
    highlight_cell_tree_text(colored_text,cell_properties,cell_properties['obj'])
    return colored_text

@debug_gate
def generate_cell_text(cell_properties):
    context=g_screen_obj['active_obj']
    text=''
    #print(context,cell_properties)
    if context in ['tree', 'ephemeral_tree']:
        text =  generate_cell_tree_text(cell_properties['obj'],cell_properties)
        text =  color_cell_tree_text(text,cell_properties)
    elif context in ['calendar']:
        text =  generate_cell_calendar_text(cell_properties['obj'],cell_properties)
        text =  color_cell_calendar_text(text,cell_properties)
    elif context == 'popup':
        text = generate_cell_box_text(cell_properties['obj'],cell_properties)
        text = color_cell_popup_text(text,cell_properties)
    elif context == 'vertical_tree':
        text = generate_cell_vertical_tree_text(cell_properties['obj'],cell_properties)
        text = color_cell_default_text(text,cell_properties)
    else:
        text = generate_cell_default_text(cell_properties['obj'],cell_properties)
        text = color_cell_default_text(text,cell_properties)
        '''no default impl'''
    return text
    #print('----------')
    return format_cell_text(text,cell_properties['end_x']-cell_properties['start_x']+1,True)
    #return format_cell_text(text,4,True)

#format_cell_text(text="hello",width=3,wrap=True)
#format_cell_text(text="hello hi how ar you\n\nmm",width=3,wrap=True)
@debug_gate
def format_cell_text(text,width=100,wrap=True):
    #print('========',text,width)
    if width < 1: raise Exception('width size cannot be less than one')
    formatted_text = ''
    formatted_line = []
    formatted_text_obj = []
    carry_over = ''
    lines = [line.colored_obj for line in text ]
    curr_line = lines.pop(0) if lines else None
    running_width = 0
    while curr_line is not None: #dont do empty some line is empty and it stops at that example hello\n\nhi will stop at hello
        words = curr_line
        carry_over = ''
        add_new_line=True
        for n,each_word_obj in enumerate(words):
            each_word = each_word_obj.word
            #print('###each_word:'+each_word)
            if len(each_word) + running_width <= width:  
                #print('words added',each_word,running_width,width)
                formatted_text += each_word
                formatted_line.append(each_word_obj.colored_obj)
                #print('...',[i for i in formatted_line])
                running_width += len(each_word)
            elif len(each_word) + running_width > width:  
                #print("###crossingwidth###",width,running_width)
                if len(each_word) > width : # keep looping this till it becomes empty 
                    #print("###bigwordfound###")
                    each_big_word = each_word
                    while each_big_word:
                        #print("###eachbigword###:",each_big_word,width,running_width)
                        #input()
                        if each_big_word:
                            #print("###eachpartbigword###:",each_big_word[0: width - running_width])
                            each_big_curr_word = each_big_word[0: width - running_width]
                            each_big_word = each_big_word[len(each_big_curr_word):]
                            formatted_line.append({ **each_word_obj.colored_obj, **{'word': each_big_curr_word} })
                            #print('...',[i for i in formatted_line])
                            running_width += len(each_big_curr_word)
                            if running_width + len(each_big_curr_word) >= width: 
                                formatted_text_obj.append(formatted_line)
                                formatted_line = []
                                running_width = 0
                            
                else:
                    #print('words insert',words[n:])
                    if words[n:]:
                        lines.insert(0,words[n:])
                    break
        running_width = 0
        formatted_text += '\n'
        if formatted_line: formatted_text_obj.append(formatted_line)
        #print(formatted_text_obj)
        formatted_line=[]
        #print('popping line')
        curr_line = lines.pop(0) if lines else None
        #print('popped line',curr_line)
    original_words=''.join([ word.colored_obj['word'] for line in text for word in line.colored_obj])
    validation_words=''.join([word['word'] for line in formatted_text_obj for word in line])
    if original_words != validation_words:
        raise Exception('formatting text error does not match',original_words,validation_words)
    return formatted_text_obj

@debug_gate
def build_cell_text(table,text,cell_properties):
    cp=cell_properties
    if 'w_shift' not in cp: cp['w_shift']=0
    if 'h_shift' not in cp: cp['h_shift']=0
    #print(cell_properties)
    #input()
    chars=[]
    for line in text:
        letters=[]
        for word in line :
            '''for letter in word['word']:
                letters.append( {**word, **{'txt': letter}}  )'''
            letters+=word_obj_to_letter_obj( word )
        chars.append(letters)
    #mx = max([ len(i) for i in chars ])
    #normalised_chars = [ (i+(['*']*mx))[0:mx] for i in chars ]
    for i in range(cp['start_y']+cp['h_shift'], cp['end_y'] + 1):
        for j in range(cp['start_x']+cp['w_shift'], cp['end_x'] + 1):
            char_y = i - ( cp['start_y'] + cp['h_shift'] )
            char_x = j - ( cp['start_x'] + cp['w_shift'] )
            if check_if_range_in_table(chars,char_y,char_x) and j >= cp['start_x'] and i >= cp['start_y']:
                make_table_entry(table, i, j, chars[char_y][char_x])
    '''for i in table:
        for j in i:
            if j==' ':
                print(j,end='')
            else:
                print(j['txt'],end='')
        print()'''


def make_table_entry(table,y,x,obj):
    if check_if_range_in_table(table,y,x):
        table[y][x]=obj

def check_if_range_in_table(table,y=0,x=0):
    return len(table)>0 and y < len(table) and y >= 0 and x < len(table[y]) and x >=0 

@debug_gate
def build_cell_block(cell_properties):
    ''' the height and width should be specific to this cell block not whole table '''
    #print('======',cell_properties)
    margin_padding_border = ( cell_properties['margin']['units']+cell_properties['padding']['units']+cell_properties['border']['units'] )
    cell_properties['start_x'] = cell_properties['start_y'] = margin_padding_border
    margin_padding_border = margin_padding_border * 2
    cell_properties['end_x'] = cell_properties['start_x'] + cell_properties['width'] - margin_padding_border - 1 
    cell_properties['end_y'] = cell_properties['start_y'] + cell_properties['height'] - margin_padding_border - 1
    if cell_properties['height'] == -1 or cell_properties['width'] == -1:
        cell_properties['start_x'] = cell_properties['start_y'] = margin_padding_border = 0 #this mode is mainly for copying text so no border as copying becomes difficult
        text = generate_cell_text(cell_properties)
        cell_properties['height'] = len(text)
        '''for i in text:
            print(i)'''
        cell_properties['width'] =  max( [ sum([len(word.colored_obj['word']) for word in line.colored_obj])  for line in text] )
        #print(cell_properties['height'],cell_properties['width'] ,margin_padding_border)
        cell_properties['end_x'] = cell_properties['start_x'] + cell_properties['width'] - 1 
        cell_properties['end_y'] = cell_properties['start_y'] + cell_properties['height'] - 1
    else:
        text = generate_cell_text(cell_properties)
    formatted_text_obj = format_cell_text(text,cell_properties['end_x']-cell_properties['start_x']+1,True)
    print_arr = [ [ ' ' for i in range(cell_properties['width']) ] for j in range(cell_properties['height']) ] 
    build_cell_text(print_arr,formatted_text_obj,cell_properties)
    if margin_padding_border > 0:
        #border
        if cell_properties['border']['units'] > 0:
            cell_properties['start_x'] -= cell_properties['border']['units']
            cell_properties['start_y'] -=cell_properties['border']['units']
            cell_properties['end_x'] += cell_properties['border']['units']
            cell_properties['end_y'] += cell_properties['border']['units']
            fill_surround_block('border',print_arr,cell_properties)
        #margin
        if cell_properties['margin']['units'] > 0:
            cell_properties['start_x'] -= cell_properties['margin']['units']
            cell_properties['start_y'] -= cell_properties['margin']['units']
            cell_properties['end_x'] += cell_properties['margin']['units']
            cell_properties['end_y'] += cell_properties['margin']['units']
            fill_surround_block('margin',print_arr,cell_properties)
        #padding
        if cell_properties['padding']['units'] > 0:
            cell_properties['start_x'] -= cell_properties['padding']['units']
            cell_properties['start_y'] -=cell_properties['padding']['units']
            cell_properties['end_x'] += cell_properties['padding']['units']
            cell_properties['end_y'] += cell_properties['padding']['units']
            fill_surround_block('padding',print_arr,cell_properties)
    '''for i in print_arr:
        print(''.join(i))
    #input()'''
    return { **cell_properties, **{'print_arr': print_arr } }

@debug_gate
def build_popup_array_table(state_of_table, table,table_properties,command_properties,cell_properties):
    height = table_properties['height']
    width = table_properties['width']
    init_x = state_of_table['start_x'] + command_properties['w_shift']
    init_y = state_of_table['start_y'] + command_properties['h_shift']
    line = state_of_table['line']
    word = state_of_table['word']
    total_word_in_line = state_of_table['total_word_in_line']
    total_line = state_of_table['total_line']
    hide_answer = command_properties['h_shift']
    hide_line_answer = state_of_table['hide_line_answer']
    cell_block_res = build_cell_block({ **cell_properties, **{'obj':table[0], 'width': width , 'height': height, 'w_shift': init_x, 'h_shift': init_y, 'line': line, 'word' : word, 'total_word_in_line': total_word_in_line, 'total_line': total_line, 'hide_line_answer': hide_line_answer, 'secret_in_line': False}} )
    cell_block = cell_block_res['print_arr']
    '''for y in range(height):
        for x in range(width):
            if check_if_range_in_table(cell_block,y-init_y,x-init_x):
                #print(init_y,y,y-init_y,init_x,x,x-init_x)
                #print(cell_block[y-init_y][x-init_x])
                print_arr[y][x]=cell_block[y-init_y][x-init_x]'''
    return cell_block, { 'start_x': init_x, 'start_y': init_y, 'total_word_in_line': cell_block_res['total_word_in_line'], 'hide_line_answer': cell_block_res['hide_line_answer'], 'secret_in_line': cell_block_res['secret_in_line'], 'total_line': cell_block_res['total_line'] } 

@debug_gate
def build_vertical_tree_array_table(state_of_table, table, table_properties, command_properties, context_properties, cell_properties):
    print_arr=[]
    height = table_properties['height']
    width = table_properties['width']
    w_size = table_properties['w_size']
    h_size = table_properties['h_size']
    highlight=command_properties['highlight']
    selected_visible_items=[]
    for n,i in enumerate(table):
        #print(i['name'],i['_level'])
        if i['_level'] <= int(args.level):
            selected_visible_items.append( { 'obj': i } )
            i['_print_arr_name']=str(n)
            cell_block_res = build_cell_block({ **cell_properties, **{'obj': i, 'width': w_size , 'height': h_size, 'highlight': highlight   }} )
            cell_block = cell_block_res['print_arr']
            print_arr+=(cell_block)
    return print_arr, { 'selected_visible_items': selected_visible_items}

@debug_gate
def build_tree_array_table(state_of_table, table, table_properties, command_properties, context_properties, cell_properties):
    #print(table_properties)
    height=table_properties['height']
    width=table_properties['width']
    if width == -1 or height == -1 :raise Exception("width and height cannot be -1 in tree mode")
    w_size=table_properties['w_size']
    h_size=table_properties['h_size']
    default_color=table_properties['default_color']
    w_shift=command_properties['w_shift']
    h_shift=command_properties['h_shift']
    highlight=command_properties['highlight']
    start_x=state_of_table['start_x']
    start_y=state_of_table['start_y']
    first_w_block_in_scope=state_of_table['first_w_block_in_scope']
    first_h_block_in_scope=state_of_table['first_h_block_in_scope']
    start_y, cols, first_w_block_in_scope = calculate_table_block_size( start_y, first_w_block_in_scope, w_size, w_shift, width)
    start_x, rows, first_h_block_in_scope = calculate_table_block_size( start_x, first_h_block_in_scope, h_size, h_shift, height)
    #print(start_x, first_h_block_in_scope, h_size, h_shift, height)
    #print(start_x, rows, first_h_block_in_scope)
    sum = 0
    #print(start_y, cols, first_w_block_in_scope,start_x, rows, first_h_block_in_scope )
    for i in rows: sum += i['b']
    if sum != height: raise Exception('sorry the rows size did not match')
    sum = 0
    for i in cols: sum += i['b']
    if sum != width:   raise Exception('sorry the cols size did not match')
    print_arr = [ [' ' for i in range(width)] for i in range(height) ]
    selected_visible_items = []
    s_x = s_y = 0
    running_height = 0
    first_row = True
    for n_row,row in enumerate(rows):
        s_x=0
        end_y = min(s_y + row['b'],height) - 1
        first_col = True
        for n_col,col in enumerate(cols):
            end_x = min(s_x + col['b'],width) - 1
            if row['p'] >= 0 and row['p'] < len(table) and col['p'] >=0 and col['p'] < len(table[0]) and table [ row['p'] ] [ col['p'] ]:
                #print(s_x,end_x)
                obj = table [ row['p'] ] [ col['p'] ]
                cell_block_res = build_cell_block({ **cell_properties, **{'obj': obj, 'width': w_size , 'height': h_size, 'highlight': highlight, 'default_color': default_color  }} )
                cell_block = cell_block_res['print_arr']
                curr_cell_block_y = cell_block_s_y = h_size - row['b'] if first_row else 0 
                curr_cell_block_x = cell_block_s_x = w_size - col['b'] if first_col else 0 
                #print(curr_cell_block_x,curr_cell_block_y)
                for y in range(s_y, end_y + 1 ):
                    curr_cell_block_x = cell_block_s_x
                    for x in range(s_x, end_x + 1 ):
                        #print(len(print_arr),len(print_arr[0]),y,x,curr_cell_block_y,curr_cell_block_x)
                        if check_if_range_in_table(cell_block,curr_cell_block_y,curr_cell_block_x):
                            print_arr[y][x]=cell_block[curr_cell_block_y][curr_cell_block_x]
                            curr_cell_block_x += 1
                    curr_cell_block_y += 1
                selected_visible_items.append( { 'obj': obj , 'curr_row_in_table': n_row , 'curr_col_in_table': n_col,  'print_arr_row': s_y , 'print_arr_start': s_x, 'print_arr_end': end_x + 1  } )
            first_col = False
            s_x += col['b']
            '''for temp in print_arr:
                print(''.join(temp),end='')
            print()'''
        first_row = False
        s_y += row['b']
    return print_arr, { 'start_x': start_x, 'start_y': start_y, 'first_w_block_in_scope': first_w_block_in_scope, 'first_h_block_in_scope': first_h_block_in_scope , 'selected_visible_items': selected_visible_items}

@debug_gate
def ansii_screen_controls(mode="clear_screen_for_print" , context_properties = None):
    if not args.screencontrol:
        return
    if mode=="clear_screen_for_print":
        print('\033[{hgt}A'.format(hgt=os.get_terminal_size().lines+1),end='',flush=True)
    elif mode=='move_cursor_x_y':
        print('\033[{};{}H'.format(context_properties['y'], context_properties['x']),end='')

@debug_gate
def fill_vertical_dots(tree,selected_visible_items, print_arr,width, height,h_size,w_size, color, parent_non_visible_items=[],child_key = "_children",mode="children"): 
    #first it should add vertical bars for all items in visible area, then we ll collect all the items for which parents are not visible and do one mroe round. it might lead to recursive so using mode and just calling once
    #print("mode is ", mode )
    if mode == "children" :
        item_to_loop = selected_visible_items
    else:
        item_to_loop = parent_non_visible_items
    #for i in selected_visible_items: print('selected_visible_items', i )
    #if mode == "parent":
        #for i in parent_non_visible_items: print('parent_items', i['obj']['id'],  i['obj']['name'] )
    selected_ids = [ i['obj']['id'] for i in selected_visible_items]
    parent_not_visible_but_child_visible = []
    visited_parent_ids = []
    for n_item,i in enumerate(item_to_loop):
        #print('******************',i['obj']['name'])
        if mode == "children":
            parent_of_visible_item =  node_search_by_child ( tree, i['obj']['id'] , child_key )
            # if parent existis and  parent already identified ( many child can have same parent and add it multiple times ) and  parent is not already in visible
            # and if the current col(not the parent) is first column then the vertical bar wont be visible anyway
            #if parent_of_visible_item : print(i['obj']['name'] , parent_of_visible_item['id'], parent_of_visible_item , parent_of_visible_item['id'] not in visited_parent_ids , parent_of_visible_item['id'] not in selected_ids , i['curr_col_in_table'] ) 
            if parent_of_visible_item and parent_of_visible_item['id'] not in visited_parent_ids and parent_of_visible_item['id'] not in selected_ids and i['curr_col_in_table'] > 0: 
                parent_not_visible_but_child_visible .append ( { 'obj':  parent_of_visible_item } )
                visited_parent_ids.append( parent_of_visible_item['id'] )
            
        #give me childrens of this node 
        given_item_child = i['obj'][ child_key ]
        #for each children what is the position in table 
        min_row = 0 
        max_row = 0 
        min_row_found = False 
        max_row_found = False 
        #print(i['obj']['name'])
        arr_start = None
        if not arr_start and mode == 'parent':
            # used in parent mode since parent is not visible and wont have any column info so getting from children, all children have same column so just getting the last item, dont put this inside the above block where temp_obj is found . some times the first and last child are out of bounds so it dont go into the loop
            for temp in selected_visible_items:
                if temp['obj']['id'] in given_item_child: #note : not all childs will be in selected itesms but atleast one will be there since that is the one called the parent
                    arr_start = temp['print_arr_start']  
                    break
        #if mode == "children" :
            #print( '######', i['obj']['name'], given_item_child, len(given_item_child)  , not any(set(given_item_child).intersection(set(selected_ids))) , i['print_arr_row'] , width )
        if mode == "children" and len(given_item_child) > 0 and not any(set(given_item_child).intersection(set(selected_ids))) and i['print_arr_end'] >= width : 
            #print("&&&&&&&&& enter special calc for ", i['obj']['name'])
            #if it does not have full width of the column then dont print ther vertical bar as it is not going to be visible anyway 
            if i['print_arr_end'] - i['print_arr_start'] < w_size:
                min_row = max_row = 0 
            else:
                #how many child the parent has 
                n_of_child_on_each_side = len(i['obj'][child_key])//2 # supposte its 3 ans is 1 1 one each side
                size_of_child_for_each_Side = n_of_child_on_each_side * h_size
                size_on_upper_side = size_of_child_for_each_Side
                size_on_lower_side = size_of_child_for_each_Side + h_size - ( h_size - 1 )
                min_row = max ( 0, i['print_arr_row'] - size_on_upper_side )
                max_row = min ( height, i['print_arr_row'] + size_on_lower_side )
            #print('--------',min_row, max_row)
        else:
            for n,each_child_id in enumerate(given_item_child):
                '''if not arr_start and mode == 'parent':
                    # used in parent mode since parent is not visible and wont have any column info so getting from children, all children have same column so just getting the last item, dont put this inside the above block where temp_obj is found . some times the first and last child are out of bounds so it dont go into the loop
                    temp_obj = [ temp  for temp in selected_visible_items if temp['obj']['id']==each_child_id ] #note : not all childs will be in selected itesms so it may retrun empty
                    if temp_obj: 
                        arr_start = temp_obj[0]['print_arr_start'] '''
                if n == 0 : # if top most child is found 
                    min_row = 0
                    if each_child_id in selected_ids :
                        temp_obj = [ temp  for temp in selected_visible_items if temp['obj']['id']==each_child_id ][0]
                        min_row = temp_obj['print_arr_row']
                        min_row_found = True 
                        #print("found min row ",temp_obj)
                if n == len( given_item_child ) - 1 :
                    max_row = min_row if len( given_item_child ) == 1 else height # if there only one child max row will be same as minrow which is zero
                    if each_child_id in  selected_ids   :
                        temp_obj = [ temp  for temp in selected_visible_items if temp['obj']['id']==each_child_id ][0]
                        max_row = temp_obj['print_arr_row'] + 1
                        max_row_found = True 
                        #print("found max row ",temp_obj)
                #print('#######',each_child_id,min_row,max_row)
            
        if mode == "parent":
            col_of_vertical_dots = arr_start - 1
        else:
            col_of_vertical_dots = i ['print_arr_end'] - 1 
        #print(min_row, max_row , col_of_vertical_dots , len(print_arr) , len(print_arr[0]) )
        for each_row_for_dot in range(min_row, max_row ):
            #print(each_row_for_dot , col_of_vertical_dots)
            if min_row_found and max_row - min_row > 1 and each_row_for_dot == min_row:
                print_arr[ each_row_for_dot ][ col_of_vertical_dots] = word_obj_to_letter_obj(color_word('/',color,False).colored_obj)[0]
                min_row_found = False 
            elif max_row_found and max_row - min_row > 1 and each_row_for_dot == max_row - 1:
                print_arr[ each_row_for_dot ][ col_of_vertical_dots] = word_obj_to_letter_obj(color_word('\\',color,False).colored_obj)[0]
                max_row_found = False 
            else:    
                print_arr[ each_row_for_dot ][ col_of_vertical_dots]= word_obj_to_letter_obj(color_word('.',color,False).colored_obj)[0]
    #one more call for parents 
    if mode == "children":
        fill_vertical_dots(tree,selected_visible_items, print_arr,width, height,h_size,w_size,color,parent_not_visible_but_child_visible,child_key,mode="parent")

@debug_gate
def getNoParentNode(tree):
    nodes = list(map(lambda d:d['id'],tree))
    links = list(map(lambda d:d['children'],tree))
    links = [item for sublist in links for item in sublist]
    topNodeIds=list(filter(lambda d:d not in links,nodes))
    topNodes=list(filter(lambda d:d['id'] in topNodeIds,tree))
    return topNodes

@debug_gate
def check_node_uniqueness(tree):
    unique_id = list(map(lambda d:d['id'],tree))
    return len(unique_id) == len(set(unique_id))

@debug_gate
def node_search_by_id(tree,node_id_list=[]):
    selectedNodes=[]
    for i in tree:
        for j in node_id_list:
            if i['id']==j:
                selectedNodes.append(i)
                break
    return selectedNodes 


def node_search_by_child(tree,node_id, child_key='children'):
    #print('node_search_by_child: searching for ',node_id)
    selectedNodes=[]
    for i in tree:
        if child_key not in i: print(i)
        #for j in node_id:
        if node_id in i[child_key]:
            selectedNodes.append( i )
    if len(selectedNodes) > 1:
        raise Exception( 'found more than 1 parent for ' , node_id, selectedNodes)
    elif selectedNodes:
        return selectedNodes[0]
    else:
        return None

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

def get_all_children(tree,node_id_list=[],key='children'):
    selectedNodes=[]
    selected_id=[]
    selected_id+=node_id_list
    for i in selected_id:
        res = get_children(tree, [i], key)
        for j in res :
            if j['id'] not in selected_id:
                selectedNodes.append(j)
                selected_id.append(j['id'])
    return selectedNodes

def get_children(tree,node_id_list=[],key="children"):
    selectedNodes=[]
    nodes = node_search_by_id(tree,node_id_list)
    for i in nodes:
        if len(i[key]) > 0 : 
            selectedNodes+=node_search_by_id( tree, i[key] )
    return selectedNodes    
 
def get_parent(tree,node_id):
    return node_search_by_child(tree,node_id)
    
def is_item_in_list(item,item_list,partial=False):
    item=item.lower()
    item_list=[i.lower() for i in item_list]
    if not partial:
        return item in item_list
    else:
        for i in item_list:
            if item in i:
                return True
    
def match_node_property(node_list,values=[],property_name=['tag','name'],include_context_as_tag=True):
    if not values : return node_list
    selectedNodes=[]
    for j in node_list:
        match=[]
        for i in values:
            match_found=False
            for k in property_name:
                if k in j:
                    property_name_list=j[k] if isinstance(j[k],list)  else [j[k]] #some property like tag is a list but name is not a list so making common
                    if include_context_as_tag and not args.filename : property_name_list += g_context['context'] #when specific file is chosen then no need to add a tag
                    if is_item_in_list(i,property_name_list,True):
                        match_found=True
                        break #found stop searching properties as for one property match is found
            match.append(match_found)
        if all(match):
            selectedNodes.append(j)
    return selectedNodes

@debug_gate    
def parse_command(tree,command):
    cmd = list(command.split(','))
    selectedNodes=[]
    selectedIds=[]
    prev_node = None
    for i in cmd:
        curr_selected_node=[]
        cmd_parts=i.split('?')
        node_name=cmd_parts[0].split(',') if cmd_parts[0]!='' else None
        node_tag = None if len(cmd_parts)<2 else [] if cmd_parts[1]=='' else cmd_parts[1].split(',')
        if node_name is not None: curr_selected_node = match_node_property(tree,node_name,['name'])
        if node_tag is not None: 
            search_tree = curr_selected_node if node_name is not None else tree
            #print('........',curr_selected_node,node_name)
            curr_selected_node =  match_node_property(search_tree,node_tag,['tag'])
        #print(node_name, node_tag)
        #print([i['name'] for i in curr_selected_node])
        for curr_item in curr_selected_node:
            if curr_item['id'] not in selectedIds:
                selectedIds.append(curr_item['id'])
                selectedNodes.append(curr_item)
    return(selectedNodes)

@debug_gate
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
        prevNode = get_parent(tree,selectedNodes[0]['id']) 
        if len(childNodes) == 0:
            start=input( color_text( 'end of road e: to end b: to go back', 'RED' )  ).rstrip()
            if start not in ['e','b'] or start == 'e':
                print('bye..')
                break
            else:
                print()
        else:
            for n,i in enumerate(childNodes):
                print(str(n)+'('+i['name']+')',end=' ')
            print()
            if prevNode:
                print('Backward Node:(',prevNode['name'],')')
            
            start=input(color_text ( 'choose starting point: b for prev' , "GREEN" )  )
        if start=='b':
            if not prevNode: #this has no parent so we cannot go back 
                selectedNodes = selectedNodes
            else:
                selectedNodes = [ prevNode ]
        else:
            selectedNodes= [childNodes[int(start)]]

@node_gate
def to_node(content,filename,reload):
    '''filename wont change in current context so we cannot get it from g_context
    called_from_current_search need to know how is calling to_node if its a link search calling it or a true search calling it . this is needed to avoid infinite loop when searching for link data
    '''
    curr_block=''
    start=False
    identified_box_hash=False
    seen_link_atleast_once=False
    total_items=[]
    dict_items=dict()
    global g_prevent_infinite_link_search
    for i in content:
        if i.startswith('#?#box'):
            i = i.rstrip()
            identified_box_hash=True
            seen_link_atleast_once=False
            if start:
                if curr_block:
                    dict_items['data'].append({ 'type': 'default', 'txt': curr_block })
                    curr_block=''
                total_items.append(dict_items)
            else:
                start=True 
            items=i.split('#')
            dict_items={'_filename':filename}
            for j in items:
                if '@' in j:
                    key=j.split('@')[0]
                    value=j.split('@')[1]
                    if key.lower() in ['parent','children','tag','date']:
                        value=value.split(',') if value.strip()!='' else []
                    dict_items[key]=value
            dict_items['data']=[]
            #dict_items = dict([ ( a.split('@')[0],a.split('@')[1].split(',') if ',' in a.split('@')[1] else a.split('@')[1])  for a in i.split('#') if '@' in a ])
        elif i.startswith('#?#link') and identified_box_hash:
            seen_link_atleast_once=True
            lnk = dict([ ( a.split('@')[0],a.split('@')[1].split(',') if ',' in a.split('@')[1] else a.split('@')[1])  for a in i.split('#') if '@' in a ])
            lnk_nodeid = lnk['id'].rstrip()
            lnk_basefilename = lnk['fn'].rstrip()
            if lnk_basefilename in g_context['all_file_dict']:
                lnk_filename = g_context['all_file_dict'][lnk_basefilename] 
            else:
                raise Exception("link error for node id:"+lnk_nodeid+" and temp_filename:"+lnk_basefilename)
            set_g_context(lnk_filename,False,reload)
            if curr_block:
                dict_items['data'].append({ 'type': 'default', 'txt': curr_block })
                curr_block=''
            dict_items['data'].append({ 'type': 'link', 'id':lnk_nodeid, 'filename':lnk_basefilename })
        elif identified_box_hash:
            if i.startswith('#?#hint'):
                hint_items=i.rstrip().split('#')
                for hint_j in hint_items:
                    if '@' in hint_j:
                        key=hint_j.split('@')[0]
                        value=hint_j.split('@')[1]
                        if key.lower() in ['tag','date','type']:
                            value=value.split(',') if value.strip()!='' else []
                        else:
                            raise Exception("hint has an unapproved key {}".format(key))
                        if key in dict_items:
                            dict_items[key] += value
                        else:
                            dict_items[key] = value
            curr_block+=i
    if curr_block: dict_items['data'].append({ 'type': 'default', 'txt': curr_block })
    curr_block=''
    total_items.append(dict_items)
    return(total_items)

@debug_gate
def file_to_tree(filename,reload=False):
    content=file_to_list(filename)
    return to_node(content,filename,reload)

g_context=dict()
g_context['tree']=[]
g_context['accepted_mode']=['tree','ephemeral_tree','calendar','popup', 'vertical_tree']
g_ephemeral_tree: list= [{'calculatedX': '0', 'calculatedY': '0', 'children': [] , '_children': [], 'name': 'seed' , 'id': 'seed', 'parent': [], 'x': '0', 'y': '0', 'data': [{'type': 'default', 'txt': 'seed'}], '_filename':'dummy', }]
@debug_gate
def set_g_context(filename=None,change_current_context=False,tree=None,reload=False):
    base_file_name=os.path.basename(filename)
    if reload or base_file_name not in g_context: 
        g_context[base_file_name]=dict()
        g_context[base_file_name]['filename']=filename # these two lines must be above tree calculation its an indicator that this is currently being processed,if this indicator is not there program will think its not processed and leads to recursion
        g_context[base_file_name]['basefilename']=base_file_name
        if not tree: tree=file_to_tree(filename,reload)
        context=[ j.rstrip() for i in tree if i['id']=='seed' and 'tag' in i for j in i['tag']]
        context=[i.rstrip() for i in context]
        #priority= [ int(i['priority'].rstrip()) if 'priority' in i else 5 for i in tree if i['id']=='seed' ][0]
        #if priority > 5 : raise Exception('Max allowed value for priority is 5')
        g_context[base_file_name]['tree']=tree
        g_context[base_file_name]['context']=context
        #g_context[base_file_name]['priority']=priority
    if change_current_context: set_g_current_context(filename)
    #print('set_g_context finished for file {}: {}'.format(base_file_name,g_context[base_file_name].keys()))
   # maintain history also in g_context under key nodeid

@debug_gate
def set_g_current_context(filename):
        base_file_name=os.path.basename(filename)
        if base_file_name not in g_context: raise Exception('cannot set current context as it is not not loaded in g_context')
        g_context['filename']=filename
        g_context['basefilename']=base_file_name
        g_context['tree']=g_context[base_file_name]['tree']
        g_context['context']=g_context[base_file_name]['context']
        #g_context['priority']=g_context[base_file_name]['priority']
        print("context is:",g_context['context'])
        set_color_context()

@debug_gate
def search_all():
    for i in g_context['chosen_file_list']:
        base_file_name = os.path.basename(i)
        search( i , set_curr_context=False,prompt_each_match=False)
    print('All files searched')

@debug_gate
def search(filename,set_curr_context=True,prompt_each_match=True,reload=False) -> None:
    base_file_name=os.path.basename(filename)
    filtered_nodes=[]
    print('searching {}'.format(base_file_name))
    set_g_context(filename=filename,change_current_context=set_curr_context,tree=None,reload=reload)
    if reload or ( 'searched' not in g_context[base_file_name] or not g_context[base_file_name]['searched'] ): 
        print('search was not completed earlier for  {} initiating search'.format(base_file_name))
        g_context[base_file_name]['searched']=True
        g_context[base_file_name]['filtered_nodes']=filtered_nodes
        if args.search!='' and args.search is not None:
            #args_property = args.property.split(',') if args.property != '' else ['name','tag']
            args_level = args.level
            filtered_nodes = parse_command(g_context[base_file_name]['tree'],args.search)
            if filtered_nodes:
                g_context[base_file_name]['filtered_nodes']=filtered_nodes
                if not reload: print('Match found in:'+filename)
                if prompt_each_match: input()
    '''if args.dive=='true' and args.dive is not None:
        dive_mode(g_context['tree']) this should not be in search it should be outside disabling for now'''
    
@debug_gate
def identify_files(key='all',filename=None):
    files=file_list=[]
    base_dir=g_context['base_dir']
    if base_dir.startswith('C:\\Users\\mithu'):
        file_list = {'reference' : [
                    base_dir+r'\Desktop\projects\d3\map\core\data\*[0-9].txt', # non recursive
                    base_dir+r'\Desktop\projects\*\quickref.txt',# ** means recursive
                    #r'G:\My Drive\Downloads\jarvis\tech\**\py*.txt' not all files are converted now
                    ],
                    'spark' : [base_dir+r'\Desktop\projects\d3\map\core\data\sp*.txt'],
                    'secret' : [base_dir+r'\Downloads\track\projects\d3\privateData\secrets_1.txt'],
                    'private' : [base_dir+r'\Downloads\track\projects\d3\privateData\*.txt'],
                    'quickref' : [
                    #base_dir+r'\Downloads\track\**\*quickref*.txt', 
                    #base_dir+r'\Desktop\projects\**\*quickref*.txt'
                    ],
                }
    elif base_dir.startswith('/storage/emulated/0/Download'):
        file_list = {'reference' : [ base_dir+r'/*[0-9].txt', 
                    ],
                }       
    file_path_list=dict()
    for k,v in file_list.items():
        files_per_key=[]
        for i in v:
            files_per_key+=glob.glob(i,recursive=True)
        file_path_list[k]=files_per_key
    all_files=[]
    for v in file_path_list.values(): all_files+=v
    all_file_dict=dict()
    for i in all_files:
        if os.path.basename(i) in all_file_dict and all_file_dict[os.path.basename(i)]!=i:  # second and condition sometimes multiple key may point to same file which is valid
            raise Exception("\n"+i+" is already present in dict as "+all_file_dict[os.path.basename(i)]+"\nkeep file names unique even across folders \n this saves a lot of madness \n alternative was fileid but it requires opening file and looking into it \n having unique filename is painful but its pretty easy to look up for links")
        all_file_dict[os.path.basename(i)]=i
    g_context['all_file_dict']=all_file_dict
    if key and key in ('all'):
        chosen_file_list = all_files
    elif key is not None and key != '':
        chosen_file_list = file_path_list[key.lower()]
    elif filename:
        if filename[0] == '*' and filename[-1] == '*':
            chosen_file_list = [ all_file_dict[temp] for temp in all_file_dict.keys() if filename[1:-1].lower() in temp.lower() ]
        else:
            chosen_file_list=[filename]
    else:
        raise Exception("No matching files")
    g_context['chosen_file_list']=list(set(chosen_file_list))
    return g_context['chosen_file_list'] #each time the search order will be different so dont introduce shuffle

def reload_coordinator(filename):
    search(filename,set_curr_context=True,prompt_each_match=False,reload=True)  
    
def main_coordinator(filename, command=None):
    search(filename)
    while command != 'n':
        tree = g_context[g_context['basefilename']]['tree']
        seed = node_search_by_id(tree,['seed'])[0]
        filtered_nodes = g_context[g_context['basefilename']]['filtered_nodes']
        if filtered_nodes and not ( len(filtered_nodes) == 1 and filtered_nodes[0]['id'] == 'seed' ) :
            g_context[g_context['basefilename']]['filtered_tree'] = build_tree_from_result(tree, filtered_nodes, seed)
            res = tree_display(g_context[g_context['basefilename']]['filtered_tree'] , seed , mode='tree')
            last_active_obj=res['active_obj']
            if last_active_obj in res:
                command = res[last_active_obj]['command_properties']['option']
                if command=='r':
                    reload_coordinator(filename)
            else:
                command='n'
        else:
            command='n'


@debug_gate
def memory_controller(mode='read',**kwargs):
    #print(kwargs)
    global g_remember_modified
    base_dir=g_context['base_dir']
    file_name = "remember.csv"
    if base_dir.startswith('C:\\Users\\mithu'): file_name=os.path.join(base_dir, r'Desktop\projects\d3\map\core\data\meta', file_name )
    if base_dir.startswith('/storage/emulated/0/Download'): file_name=os.path.join(base_dir, file_name )
    headers="filename|id|last_visited_date|next_visit_in".split('|')
    file_name=os.path.join(base_dir,file_name)
    if mode == "read":
        read_memory_file(file_name,headers)
    elif mode=='write':
        write_memory_file(file_name,headers, g_context['remember_list'])
    elif mode == 'update':
        #print(kwargs)
        if kwargs['next_visit_in'] == 99:
            #print('no action')
            return
        n = -1
        g_remember_modified = True
        match_found = False
        time_now = datetime.now()
        for n,i in enumerate(g_context['remember_list']):
            if i['filename'] == kwargs['filename'] and i['id'] == kwargs['id']:
                match_Found = True
                if kwargs['next_visit_in'] == 0: #if exists then break out and deal with it there
                    #print('found match zero next_visit_in')
                    break
                else:
                    i['next_visit_in'] = kwargs['next_visit_in']
                    i['last_visited_date'] = time_now
                    #print('found match and updating',i)
                    return
        if kwargs['next_visit_in'] == 0 and match_Found: #could have been in loop but dont feel comfortable doing while looping
            #print('removing',g_context['remember_list'][n])
            g_context['remember_list'].pop( n )
        else:
            #print('adding',  dict(zip(headers,[ kwargs['filename'], kwargs['id'] ,time_now , kwargs['confidence'] ]))  )
            g_context['remember_list'].append(  dict(zip(headers,[ kwargs['filename'], kwargs['id'] ,time_now , kwargs['next_visit_in'] ]))  )
        
@debug_gate
def read_memory_file(file_name, headers):
    remember_list=[]
    start=True
    with open(file_name,'r') as f:
        for line in f:
            line = line.rstrip()
            curr_list = line.split('|')
            if start:
                if headers != curr_list: raise Exception("{} does not match with header detected in file".format(headers))
                start=False
            else:
                curr_dict = dict(zip(headers,curr_list))
                curr_dict['next_visit_in']=int( curr_dict['next_visit_in'] )
                #if curr_dict['next_visit_in'] not in ( 1, 2, 3 ) : raise Exception("Allowed confidence values are 0 1 2 and 3 ,default high medium low")
                curr_dict['last_visited_date'] = datetime.strptime( curr_dict['last_visited_date'].lower() ,'%d%b%Y')
                if curr_dict['last_visited_date'] > datetime.now(): raise Exception("Last visited date cannot be in future: {} {}".format(curr_list[0],curr_list[1]))
                remember_list.append( curr_dict )
    g_context['remember_list'] = remember_list
    #print(';;;;;;;;', g_context['remember_list'] ) 
    
@debug_gate
def write_memory_file(file_name, headers, contents):
    #print(file_name, headers, contents)
     #copy2 preserves metadata
    if g_remember_modified:
        shutil.copy2( file_name, os.path.join( os.path.dirname(file_name) , os.path.basename(file_name).split('.')[0]+'_'+ datetime.strftime(datetime.now(),'%Y%m%d%H%M%S')+'.csv' ) )
        with open(file_name,'w') as f:
            f.write('|'.join(headers) + '\n' )
            for d in contents:
                text = []
                for col in headers:
                    if col == 'next_visit_in': text.append( str( d['next_visit_in'] ) )
                    elif col == 'last_visited_date': text.append( datetime.strftime(d['last_visited_date'],'%d%b%Y') )
                    else: text.append( str( d[col] ) )
                f.write('|'.join(text) + '\n' )

@debug_gate
def end_action():
    if args.remember: memory_controller('write')
    sys.exit(0)
    
@debug_gate
def main(args):
    if os.getcwd().startswith('C:\\Users\\mithu'): g_context['base_dir']='C:\\Users\\mithu'
    elif os.getcwd().startswith('/storage/emulated/0/Download'): g_context['base_dir']='/storage/emulated/0/Download'
    if args.remember: memory_controller('read')
    files=identify_files(args.key,args.filename)
    #print(files)
    #dont make it complicated search each file individually
    for filename in files:
        if args.filename is not None:
            if input('do you want to process this file:\n'+filename+'?\nenter y').rstrip() in ['y']:
                pass 
            else:
                continue
        print( color_text( 'processing file:'+ filename, 'YELLOW') )
        main_coordinator(filename)
    end_action()

parser = argparse.ArgumentParser()
parser.add_argument("-k","--key", help="search by key reference,nifi instead of file")
parser.add_argument("-f","--filename", help="increase output verbosity")
parser.add_argument("-s","--search", help="increase output verbosity")
#parser.add_argument("-d","--dive", help="dive into tree ",nargs="?",default='false',const="true")
parser.add_argument("-d","--debug", help="dive into tree ",nargs="?",default=0,const=1,type=int)
#parser.add_argument("-p","--property", help="increase output verbosity", default="name,tag")
parser.add_argument("-l","--level", help="level of depth applies only to vertical_tree", default=100)
#parser.add_argument("-e","--expand", help="node data", default=100) makes it look too complilcated not practical to use
parser.add_argument("-c","--choosenode", help="choosenode",nargs="?",default='false',const='true') #if just -c value 1 if nothing value false
#parser.add_argument("-m","--modeofprint", help="modeofprint",nargs="?",default='read',const='line')
parser.add_argument("-t","--tree", help="tree",nargs="?",default='false',const='true')
parser.add_argument("-v","--vannangal", help="painttext with colors",nargs="?",default='false',const='true')
parser.add_argument("-sc","--screencontrol", help="ansii screencontrol",nargs="?",default=False,const=True,type=bool)
parser.add_argument("-r","--remember", help="load memory file",nargs="?",default=False,const=True,type=bool)
parser.add_argument("-q","--qamode", help="show xxx on popup",nargs="?",default=False,const=True,type=bool)

args = parser.parse_args()    
print(args)

g_program_start_time = time.time()
if __name__=="__main__":
    if args.vannangal == "true":
        from colorama import Fore,init
        init(autoreset=True)
    main(args)   