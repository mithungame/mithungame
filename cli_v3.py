import re 
import sys
import argparse
import glob
import os, platform
import random
import time
if platform.system() == 'Windows': import msvcrt

context_precedence = { 
'snowflake': ['database'] ,
'python': ['python']
}
g_clrs={
    'default': {'white':[]},
    'kubernetes':{'magenta':['service','node','pod','container'],'yellow':['etcd']},
    'general': {'magenta':
        'sql sql python java c c++ go docker kubernetes'.split(" ") +
        'aws azure cloud'.split(" ") +
        'oracle mongo dynamo redshift cassandra hive '.split(" ")
    },
    'python':
    {'yellow': "and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield".split(" "),
    'red':"ArithmeticError AssertionError AttributeError BaseException BlockingIOError BrokenPipeError BufferError BytesWarning ChildProcessError ConnectionAbortedError ConnectionError ConnectionRefusedError ConnectionResetError DeprecationWarning EOFError Ellipsis EnvironmentError Exception False FileExistsError FileNotFoundError FloatingPointError FutureWarning GeneratorExit IOError ImportError ImportWarning IndentationError IndexError InterruptedError IsADirectoryError KeyError KeyboardInterrupt LookupError MemoryError ModuleNotFoundError NameError None NotADirectoryError NotImplemented NotImplementedError OSError OverflowError PendingDeprecationWarning PermissionError ProcessLookupError RecursionError ReferenceError ResourceWarning RuntimeError RuntimeWarning StopAsyncIteration StopIteration SyntaxError SyntaxWarning SystemError SystemExit TabError TimeoutError True TypeError UnboundLocalError UnicodeDecodeError UnicodeEncodeError UnicodeError UnicodeTranslateError UnicodeWarning UserWarning ValueError Warning WindowsError ZeroDivisionError abs all any ascii bin bool breakpoint bytearray bytes callable chr classmethod compile complex copyright credits delattr dict dir divmod enumerate eval exec exit filter float format frozenset getattr globals hasattr hash help hex id input int isinstance issubclass iter len license list locals map max memoryview min next object oct open ord pow print property quit range repr reversed round set setattr slice sorted staticmethod str sum super tuple type vars zip".split(" ")}
    }

def color_gate(func):
    def inner(*arrs,**kwargs): # must have inner function for decorator
        if args.vannangal == "false":
            return arrs[0]
        return func(*arrs, **kwargs)    
    return(inner)

g_color_context='default'
def set_color_context():
    global g_color_context
    context_resolver=list(set(g_context['context']).intersection(set(g_clrs.keys())))
    g_color_context= context_resolver[0] if context_resolver else 'default'

    
#only color functions should call this 
def give_color(color,clear=True):
    clear_value = '' 
    if clear: clear_value = '\033[0m'
    if color.upper() == "WHITE": 
        return { 'pre_control' : '' , 'post_control':  '' }
    else:
        return { 'pre_control' : getattr(Fore,color) , 'post_control':  clear_value }

class color_word:
    def __init__(self,word,color="WHITE",context=False):
        self.word = word  
        self.context = context 
        self.color = color
        self.colorify()
    @color_gate
    def colorify(self):
        if not self.context:
            self.colored_obj= give_color(self.color)
        else:
            curr_clr=self.color
            for clr,value in list({**g_clrs[g_color_context],**g_clrs['general']}.items()):
                if self.word.lower() in  value:
                    curr_clr=clr.upper()
                    break
            self.colored_obj= give_color(curr_clr)
        self.colored_obj['word']=self.word
    def __str__(self):
        return self.colored_obj['pre_control'] + self.colored_obj['word'] + self.colored_obj['post_control']

@color_gate
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
    def __init__(self,text,color="WHITE",context=False):
        self.text = text  
        self.context = context 
        self.color = color
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
    if context is None:
        if args.vannangal == "true":
            context = True 
        else:
            context = False
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
            
def file_to_list(filename):
    lines=[]
    with open(filename,'r',encoding='utf-8') as f:
        lines=f.readlines()
    return lines
    
def dfs(graph,start_node,child_key='_children'):
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
        #print(i)
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

def build_partial_tree(tree,seed):
    seed['_children'] = [] # this has to be done at first cnt wait for its turn
    for each_item in tree:
        v_each_item = each_item
        if each_item['id'] != 'seed':
            each_item['_children'] = []
            #print('processing item ',v_each_item['name'])
            has_upstream = False
            while not has_upstream:
                parent = node_search_by_child(g_context['tree'], v_each_item['id'] ,  )
                #lets say the current parent is not attached to anything and was not in list of selected items it will cause a problem
                if parent and parent['id'] in [ i['id'] for i in tree] :
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
    return tree
      
def build_tree_from_result(tree):
    #print('calling display tree')
    global g_context
    res=[]
    #for i in tree: print(i['name'])
    seed = node_search_by_id(g_context['tree'],['seed'])[0]
    #parent_node = getNoParentNode(tree)
    #parent_node_ids = list ( set(map(lambda d:d['id'],parent_node)).difference({'seed'}) )
    #if seed not in result seed must be added as root 
    #seed['children']=[ i for i in parent_node_ids ] # clear out existing children we are building new graph
    #parent_node = seed
    #the tree generated here is actually disconnected example if a child in 3rd level is selccted and grand parent is selected it is not attached to grand parent so we are going to attach it to closest ancestor
    if 'seed' not in [ i['id'] for i in tree  ]: tree.insert(0,seed)
    g_context['filtered_tree'] = build_partial_tree(tree,seed)
    tree_display(g_context['filtered_tree'], seed)

def build_tree_from_popup(node):
    global g_ephemeral_tree
    if node['id']+g_context['filename'] not in [ i['id']+i['_filename'] for i in g_ephemeral_tree]: 
        node['_filename']=g_context['filename']
        g_ephemeral_tree.append(node)
        node['_ephemeral_children']=[]
        g_ephemeral_tree[0]['_ephemeral_children'].append(node['id'])

def tree_display(tree,seed,mode='tree'): #dont use g_context here , it gets into the are of table context, initialize True will do it False wont do it None will check if its already done and not do it if so
    if args.tree == 'false':
        result_dfs=dfs(tree,seed) 
        #showDFSOutput(result_dfs)
        screen_coordinator('vertical_tree',result_dfs ,{ 'base_data': tree, 'start_node': seed })
    elif args.tree == "true":
        child_key = "_children" if mode == "tree" else "_ephemeral_children" 
        data_table = build_data_table_from_tree(seed,tree,child_key)
        screen_coordinator(mode,data_table ,{ 'base_data': tree, 'child_key': child_key, 'start_node': seed })

def popup_display(id):
    who_is_on_screen = g_screen_obj['active_obj']
    active_obj = g_screen_obj[who_is_on_screen]
    selected_visible_items = active_obj['state_of_table']['selected_visible_items']
    popup_obj={"name": 'NO ACTIVE ITEM', "data": 'error'}
    if id is None:
        rand_obj = random.choices(selected_visible_items)
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
        words+=k+": "+v+' '
    lines+=words+'\n'
    no_of_lines_printed+=1
    for _ in range(os.get_terminal_size().lines - no_of_lines_printed - 5): lines+=(' '*os.get_terminal_size().columns)+'\n'
    print(lines)
    command = ''
    if platform.system() == 'Windows':
        command = msvcrt.getch().decode("utf-8")
    else:
        command = input('')
    return command

def initiate_params(g_screen_current_obj):
    g_screen_current_obj['cell_properties']={'margin':{'v_char':'|','h_char':'-','units':0},'padding':{'units':0,'char':' '},'border':{'char':' ','units':0}}

def initialize_tree_params(g_screen_obj):
    '''only initialize params must be here anything that changes should not be here only STATIC'''
    command_options = { 'i j k l': "scroll", 'q' : "q for quit", "p": "popup" , "r": "rndm"}
    mode=g_screen_obj['active_obj']
    g_screen_obj[mode]=dict()
    initiate_params( g_screen_obj[mode] )
    height = os.get_terminal_size().lines - 8
    width  = os.get_terminal_size().columns
    #height = 5
    #width = 30
    if mode == "tree" : 
        command_options = { **command_options,  **{ 'n': 'move to next file', "c": "custom_input", "e": "show ephemeral tree" } }
        table_properties={'height':height,'width':width,'w_size':20,'h_size' : 1,'pre_dots' : 1,'post_dots' : 2, 'pre_dot_char': '-', 'post_dot_char': '-', 'pre_fill_name': '-', 'post_fill_name': '-', 'default_color': 'YELLOW' }
    elif mode == "ephemeral_tree":
        command_options = { **command_options, **{ 'b': "Go back to normal tree" } }
        table_properties={'height':height,'width':width,'w_size':15,'h_size' : 1,'pre_dots' : 0,'post_dots' : 1, 'pre_dot_char': ' ', 'post_dot_char': ' ', 'pre_fill_name': ' ', 'post_fill_name': ' ', 'default_color': 'GREEN' }
    g_screen_obj[mode]['table_properties']=table_properties
    g_screen_obj[mode]['command_options']=command_options

def initialize_vertical_tree_params(g_screen_obj):
    '''only initialize params must be here anything that changes should not be here only STATIC'''
    command_options = { 'q' : "q for quit", "p": "popup" , "r": "rndm"}
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
    
def initialize_popup_params(g_screen_obj):
    #print("initialize_popup_params")
    mode=g_screen_obj['active_obj']
    g_screen_obj[mode]=dict()
    initiate_params( g_screen_obj[mode] )
    g_screen_obj[mode]['cell_properties']['margin']={'v_char':'|','h_char':'-','units':1}
    command_options= { 'i j k l': "scroll", #not command option keys must be space separated
        'c': 'close popup and show tree', 
        'q' : "q for quit"
        } 
    height = os.get_terminal_size().lines 
    width  = os.get_terminal_size().columns
    table_properties={'height': height - int( height * .20 ),'width': width - int(width * .5) , 'default_color': 'WHITE'}
    #table_properties={'height': -1,'width': -1 , 'default_color': 'WHITE'}
    g_screen_obj[mode]['table_properties']=table_properties
    g_screen_obj[mode]['command_options']=command_options    

g_screen_obj=dict()
g_clear_screen_first_time=True
def screen_coordinator(mode, data_table=None ,context_properties=None): #except for mode all other params should be used only for initialization
    global g_clear_screen_first_time
    if g_clear_screen_first_time and args.screencontrol=="true":
        g_clear_screen_first_time=False
        for _ in range(os.get_terminal_size().lines): print()
    #parts that need to be refreshed each time
    g_screen_obj['active_obj']=None
    command_properties = { 'w_shift': 0, 'h_shift': 0, 'option': '', 'default_shift': 3}
    if mode in [ 'tree', 'ephemeral_tree' ]:
        g_screen_obj['active_obj']= mode
        if ( mode not in g_screen_obj):
            initialize_tree_params(g_screen_obj)
        g_screen_obj[mode] = {**g_screen_obj[mode],**{  'data_table': data_table,'context_properties': context_properties, 'table_to_be_printed': None }}
        #print(data_table)
        #print(context_properties.keys())
        #input()
        command_options=g_screen_obj[mode]['command_options']
        while command_properties['option'] != 'n':
            g_screen_obj[mode]['table_to_be_printed'] = refresh_tree_print_table(mode, command_properties)
            command = display_table()
            command_attribute = None
            if command in ['c','p']: # custom , then revert to normal input 
                if command == 'p': command_attribute = input('enter id of popup seen in screen <id>:<name> ').rstrip()
                if command == 'c': command_attribute = input(' tbd ').rstrip()
            command_dict = { 'command': command, 'command_attribute' : command_attribute}
            tree_screen_action_on_command(command_dict,command_properties,command_options)
        #teardown
        del(g_screen_obj[mode])
    if mode in [ 'vertical_tree' ]:
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
        del(g_screen_obj[mode])
    if mode == 'popup':
        g_screen_obj['active_obj']='popup'
        if ( mode not in g_screen_obj):
            initialize_popup_params(g_screen_obj)
        g_screen_obj[mode] = {**g_screen_obj[mode],**{'data_table': data_table,'context_properties': context_properties, 'table_to_be_printed': None }}        
        #print(context_properties)
        if context_properties['who_is_on_screen'] == 'tree':
            g_screen_obj[mode]['command_options']={**g_screen_obj[mode]['command_options'] , **{'p': "pin"} }
        else:
            if 'p' in g_screen_obj[mode]['command_options']: del( g_screen_obj[mode]['command_options']['p'] )
        command_options=g_screen_obj[mode]['command_options']
        while command_properties['option'] != 'q':
            g_screen_obj[mode]['table_to_be_printed'] = refresh_popup_print_table(command_properties)
            command = display_table(False,{'x':0 , 'y': 3})
            #command = display_table()
            command_attribute = None
            command_dict = { 'command': command, 'command_attribute' : command_attribute}
            popup_screen_action_on_command(command_dict,command_properties,command_options, context_properties)

def popup_screen_action_on_command(command_dict, command_properties,command_options, context_properties):
    command = command_dict['command']
    command_attribute = command_dict['command_attribute']
    command_properties['h_shift'] = 0
    command_properties['w_shift'] = 0
    valid_command_options = [ i.split(' ') for i in command_options.keys() ]
    valid_command_options = [j for i in valid_command_options for j in i]
    if command not in valid_command_options: return
    if command == 'q':
        sys.exit(0)
    if command == 'c':
        g_screen_obj['popup']['state_of_table'] = { 'start_x': 0, 'start_y': 0 } # state must be reset, after trying ways to do it in refresh pop this seems the best way else its challengig
        command_properties['option'] = 'q'
        return
    if command in ['p']:
        obj = context_properties['base_data']
        build_tree_from_popup( obj )
    if command in ['i', 'j', 'k', 'l']:
        shift_value = 1
        if command == 'i': command_properties['h_shift'] = shift_value
        elif command == 'k': command_properties['h_shift'] = - shift_value
        if command == 'j': command_properties['w_shift'] = shift_value
        elif command == 'l': command_properties['w_shift'] = - shift_value

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
    if command in [ 'p','r']: 
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

def tree_screen_action_on_command(command_dict, command_properties,command_options ):
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
    if command in [ 'p','r']: 
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
    if command in ['i', 'j', 'k', 'l']:
        shift_value = 3
        if command_attribute:
            shift_value = int(command_attribute)
        if command == 'i':
            command_properties['h_shift'] = shift_value
        elif command == 'k':
            command_properties['h_shift'] = - shift_value
            
        if command == 'j':
            command_properties['w_shift'] = shift_value
        elif command == 'l':
            command_properties['w_shift'] = - shift_value

def refresh_popup_print_table(command_properties):
    global g_screen_obj
    g_screen_tree_obj = g_screen_obj['popup']
    data_table = g_screen_tree_obj['data_table']
    table_properties = g_screen_tree_obj['table_properties']
    context_properties = g_screen_tree_obj['context_properties']
    cell_properties = g_screen_tree_obj['cell_properties']
    if 'state_of_table' not in  g_screen_tree_obj:
        g_screen_tree_obj['state_of_table'] = { 'start_x': 0, 'start_y': 0 }
    state_of_table = g_screen_tree_obj['state_of_table']
    print_table, new_state_of_table = build_popup_array_table(state_of_table, data_table,table_properties,command_properties,cell_properties)
    #print_table=[''.join(line) for line in print_table]
    g_screen_tree_obj['state_of_table'] = { **state_of_table, **new_state_of_table}
    return print_table
    
def refresh_tree_print_table(mode, command_properties):
    global g_screen_obj
    g_screen_tree_obj = g_screen_obj[mode]
    data_table = g_screen_tree_obj['data_table']
    table_properties = g_screen_tree_obj['table_properties']
    context_properties = g_screen_tree_obj['context_properties']
    cell_properties = g_screen_tree_obj['cell_properties']
    if 'state_of_table' not in g_screen_tree_obj:
        start_x, start_y = get_index_of_table( context_properties['start_node'], data_table )
        g_screen_tree_obj['state_of_table'] = { 'start_x': start_x, 'start_y': start_y, 'first_w_block_in_scope': table_properties['w_size'], 'first_h_block_in_scope': table_properties['h_size'] }
    state_of_table = g_screen_tree_obj['state_of_table']
    print_table, new_state_of_table = build_tree_array_table(state_of_table, data_table,table_properties, command_properties, context_properties, cell_properties)
    fill_vertical_dots(context_properties['base_data'],new_state_of_table['selected_visible_items'], print_table,table_properties['width'],table_properties['height'],table_properties['h_size'],table_properties['w_size'],[],context_properties['child_key'])
    #since this table is a list of list make it a list of line 
    #print_table=[''.join(line) for line in print_table]
    g_screen_tree_obj['state_of_table'] = { **state_of_table, **new_state_of_table}
    return print_table

def refresh_vertical_tree_print_table(command_properties):
    global g_screen_obj
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

def get_index_of_table(item,lst: []):
    for n,i in enumerate(lst):
        for m,j in enumerate(i):
            if j and 'id' in j and j['id'] == item['id']:
                return [n,m]
    print('could not get index of item')
    sys.exit(1)

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
def generate_node_id():
    global generate_node_ids
    id_list = generated_node_ids['ids']
    generate_value = id_list [ generated_node_ids['curr_id'] ]
    if generated_node_ids['curr_id'] + 1  >= len( id_list ):
        generated_node_ids['curr_id'] = 0
    else:
        generated_node_ids['curr_id'] += 1
    return generate_value

def fill_surround_block(mode,table,cell_properties):
    cp=cell_properties
    units=cp[mode]['units']
    if mode=='margin':
        h_char = cp[mode]['h_char']
        v_char = cp[mode]['v_char']
    if mode in ['padding','border']:
        h_char = cp[mode]['char']
        v_char = cp[mode]['char']
    for _ in range(units):
        for i in range(cp['start_x'], cp['end_x']+1): 
            make_table_entry( table, cp['start_y'], i, {'txt': h_char, 'pre_control': '\x1b[33m', 'post_control': '\x1b[0m' } )
            make_table_entry( table, cp['end_y'], i, {'txt': h_char, 'pre_control': '\x1b[33m', 'post_control': '\x1b[0m'} )
        cp['start_y'] += 1
        cp['end_y'] -= 1
        for i in range(cp['start_y'], cp['end_y']+1): 
            make_table_entry( table,i,cp['start_x'], {'txt': v_char, 'pre_control': '\x1b[33m', 'post_control': '\x1b[0m' } )
            make_table_entry( table,i, cp['end_x'], {'txt': v_char, 'pre_control': '\x1b[33m', 'post_control': '\x1b[0m' } )
        cp['start_x'] += 1 
        cp['end_x'] -= 1

def generate_cell_box_text(cell_obj, cell_properties):
    cell_text_obj = cell_obj
    text = ''
    text += cell_text_obj['name'] + "\n====\n"
    text += cell_text_obj['data'] + "\n"
    link_objs = cell_text_obj['links']
    while link_objs:
        i = link_objs.pop(0)
        text += '<l:'+os.path.basename(i['_filename'])+'>'+':'+i['name']+':\n'
        text += i['data']
        if i['links']: link_objs =i['links'] + link_objs
    return text

def generate_cell_vertical_tree_text(cell_obj, cell_properties):
    cell_text_obj = cell_obj
    return cell_text_obj['_print_arr_name']+' '*cell_text_obj['_level']+cell_text_obj['name']
    
def generate_cell_default_text(cell_obj, cell_properties):
    cell_text_obj = cell_obj
    return cell_text_obj['name']
    
def generate_cell_tree_text(cell_obj, cell_properties):
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
    return name

def color_cell_tree_text(text,cell_properties):
    colored_text = color_text(text,'YELLOW',False).colored_obj
    return colored_text

def color_cell_popup_text(text,cell_properties):
    colored_text = color_text(text,'WHITE',True).colored_obj
    return colored_text

def color_cell_default_text(text,cell_properties):
    colored_text = color_text(text,'WHITE',True).colored_obj
    return colored_text

def generate_cell_text(cell_properties):
    context=g_screen_obj['active_obj']
    text=''
    #print(context,cell_properties)
    if context in ['tree', 'ephemeral_tree']:
        text =  generate_cell_tree_text(cell_properties['obj'],cell_properties)
        text =  color_cell_tree_text(text,cell_properties)
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
def format_cell_text(text,width=100,wrap=True):
    #print('========',text)
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
        #   print('###currline:',[i.word for i in words])
        #input()
        carry_over = ''
        add_new_line=True
        for n,each_word_obj in enumerate(words):
            each_word = each_word_obj.word
            #print('###each_word:'+each_word)
            if len(each_word) + running_width <= width:  
                #print('words added',each_word)
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
            for letter in word['word']:
                letters.append( {**word, **{'txt': letter}}  )
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

def build_cell_block(cell_properties):
    ''' the height and width should be specific to this cell block not whole table '''
    #print('======',cell_properties)
    cell_properties['start_x'] = cell_properties['start_y'] = 0 
    if cell_properties['height'] == -1 or cell_properties['width'] == -1:
        text = generate_cell_text(cell_properties)
        cell_properties['height'] = len(text)
        '''for i in text:
            print(i)'''
        cell_properties['width'] =  max( [ sum([len(word.colored_obj['word']) for word in line.colored_obj])  for line in text] )
        margin_padding_border = ( cell_properties['margin']['units']+cell_properties['padding']['units']+cell_properties['border']['units'] ) * 2
        cell_properties['height'] += margin_padding_border
        cell_properties['width'] += margin_padding_border
        #print(cell_properties['height'],cell_properties['width'] ,margin_padding_border)
        cell_properties['end_x'] = cell_properties['width'] - 1 
        cell_properties['end_y'] = cell_properties['height'] - 1
    else:
        cell_properties['end_x'] = cell_properties['width'] - 1 
        cell_properties['end_y'] = cell_properties['height'] - 1 
        text = generate_cell_text(cell_properties)
    formatted_text_obj = format_cell_text(text,cell_properties['end_x']-cell_properties['start_x']+1,True)
    print_arr = [ [ ' ' for i in range(cell_properties['width']) ] for j in range(cell_properties['height']) ] 
    #border 
    fill_surround_block('border',print_arr,cell_properties)
    #margin
    fill_surround_block('margin',print_arr,cell_properties)
    #padding
    fill_surround_block('padding',print_arr,cell_properties)
    build_cell_text(print_arr,formatted_text_obj,cell_properties)
    '''for i in print_arr:
        print(''.join(i))
    #input()'''
    return print_arr

def build_popup_array_table(state_of_table, table,table_properties,command_properties,cell_properties):
    height = table_properties['height']
    width = table_properties['width']
    init_x = state_of_table['start_x'] + command_properties['w_shift']
    init_y = state_of_table['start_y'] + command_properties['h_shift']
    cell_block = build_cell_block({ **cell_properties, **{'obj':table[0], 'width': width , 'height': height, 'w_shift': init_x, 'h_shift': init_y }} )
    '''for y in range(height):
        for x in range(width):
            if check_if_range_in_table(cell_block,y-init_y,x-init_x):
                #print(init_y,y,y-init_y,init_x,x,x-init_x)
                #print(cell_block[y-init_y][x-init_x])
                print_arr[y][x]=cell_block[y-init_y][x-init_x]'''
    return cell_block, { 'start_x': init_x, 'start_y': init_y } 

def build_vertical_tree_array_table(state_of_table, table, table_properties, command_properties, context_properties, cell_properties):
    print_arr=[]
    height = table_properties['height']
    width = table_properties['width']
    w_size = table_properties['w_size']
    h_size = table_properties['h_size']
    selected_visible_items=[]
    for n,i in enumerate(table):
        #print(i['name'],i)
        selected_visible_items.append( { 'obj': i } )
        i['_print_arr_name']=str(n)
        print_arr+=(build_cell_block({ **cell_properties, **{'obj': i, 'width': w_size , 'height': h_size  }} ))
    return print_arr, { 'selected_visible_items': selected_visible_items}

def build_tree_array_table(state_of_table, table, table_properties, command_properties, context_properties, cell_properties):
    #print(table_properties)
    height=table_properties['height']
    width=table_properties['width']
    if width == -1 or height == -1 :raise Exception("width and height cannot be -1 in tree mode")
    w_size=table_properties['w_size']
    h_size=table_properties['h_size']
    w_shift=command_properties['w_shift']
    h_shift=command_properties['h_shift']
    start_x=state_of_table['start_x']
    start_y=state_of_table['start_y']
    first_w_block_in_scope=state_of_table['first_w_block_in_scope']
    first_h_block_in_scope=state_of_table['first_h_block_in_scope']
    start_y, cols, first_w_block_in_scope = calculate_table_block_size( start_y, first_w_block_in_scope, w_size, w_shift, width)
    start_x, rows, first_h_block_in_scope = calculate_table_block_size( start_x, first_h_block_in_scope, h_size, h_shift, height)
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
                cell_block = build_cell_block({ **cell_properties, **{'obj': obj, 'width': w_size , 'height': h_size  }} )
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
    
def build_tree_array_table_old(state_of_table, table, table_properties, command_properties, context_properties):
    height=table_properties['height']
    width=table_properties['width']
    w_size=table_properties['w_size']
    h_size=table_properties['h_size']
    pre_dots=table_properties['pre_dots']
    post_dots=table_properties['post_dots']
    w_shift=command_properties['w_shift']
    h_shift=command_properties['h_shift']
    start_x=state_of_table['start_x']
    start_y=state_of_table['start_y']
    pre_dot_char = table_properties['pre_dot_char']
    post_dot_char = table_properties['pre_dot_char']
    pre_fill_name = table_properties['pre_fill_name']
    post_fill_name = table_properties['post_fill_name']
    first_w_block_in_scope=state_of_table['first_w_block_in_scope']
    first_h_block_in_scope=state_of_table['first_h_block_in_scope']
    child_key=context_properties['child_key']
    start_y, cols, first_w_block_in_scope = calculate_table_block_size( start_y, first_w_block_in_scope, w_size, w_shift, width)
    start_x, rows, first_h_block_in_scope = calculate_table_block_size( start_x, first_h_block_in_scope, h_size, h_shift, height)
    sum = 0
    for i in rows: sum += i['b']
    if sum != height: raise Exception('sorry the rows size did not match')
    sum = 0
    for i in cols: sum += i['b']
    if sum != width:   raise Exception('sorry the cols size did not match')
    #print(rows)
    #print(cols)
    # fit the table to result 
    first_row = True
    first_col = True
    print_arr = []
    selected_visible_items = []
    running_height = 0
    for n_row,row in enumerate(rows):
        #print('==',row,end='   ')
        given_block_height = row['b']
        for each_row in range(  0  , given_block_height  ):
            running_width = 0 
            print_row = []
            #print('=====',each_row,running_width)
            if ( each_row ==0 and first_row and given_block_height != h_size ) or ( each_row != 0 ):#print if hgt index is0 for given block except for first block which must be height size
                if first_row: first_row = False
                #print_row+=([' ']*width)
                print_row += [ ' ' for i in range(width) ]
                running_width+=width
            else:
                for n_col,col in enumerate(cols):
                    #print(row,col)
                    if row['p'] >= 0 and row['p'] < len(table) and col['p'] >=0 and col['p'] < len(table[0]) and table [ row['p'] ] [ col['p'] ]:
                        obj = table [ row['p'] ] [ col['p'] ]
                        name =  obj['name']
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
                        if n_col == 0 :
                            name = name[-col['b']:]
                        else:
                            name = name[0:col['b']]
                        #print_row+=name
                        print_row += [ each_letter for each_letter in name ]
                        selected_visible_items.append( { 'obj': obj , 'curr_row_in_table': n_row , 'curr_col_in_table': n_col,  'print_arr_row': running_height , 'print_arr_start': running_width, 'print_arr_end': running_width + len(name)  } )
                        running_width+=len(name)
                        #print(name,len(name),col ['b'])
                    else:
                        name=([' '] * col ['b'] )
                        #print(name,len(name),col ['b'])
                        #print_row+=name
                        print_row += [each_letter for each_letter in name ]
                        running_width+=len(name)
            print_arr.append(print_row)
            #print(print_row)
            #print(len(print_row))
            #input()
            #print(print_row)
            #print(''.join(print_row) )
            running_height += 1
    return print_arr, { 'start_x': start_x, 'start_y': start_y, 'first_w_block_in_scope': first_w_block_in_scope, 'first_h_block_in_scope': first_h_block_in_scope , 'selected_visible_items': selected_visible_items} 

def ansii_screen_controls(mode="clear_screen_for_print" , context_properties = None):
    if args.screencontrol=="false":
        return
    if mode=="clear_screen_for_print":
        print('\033[{hgt}A'.format(hgt=os.get_terminal_size().lines+1),end='',flush=True)
    elif mode=='move_cursor_x_y':
        print('\033[{};{}H'.format(context_properties['y'], context_properties['x']),end='')
    
def fill_vertical_dots(tree,selected_visible_items, print_arr,width, height,h_size,w_size, parent_non_visible_items=[],child_key = "_children",mode="children"): 
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
            if min_row_found and max_row > 1:
                print_arr[ each_row_for_dot ][ col_of_vertical_dots] = {'pre_control': '\x1b[33m', 'post_control': '\x1b[0m', 'txt': '/'}
                min_row_found = False 
            elif max_row_found and max_row > 1 and each_row_for_dot == max_row - 1:
                print_arr[ each_row_for_dot ][ col_of_vertical_dots] = {'pre_control': '\x1b[33m', 'post_control': '\x1b[0m', 'txt': '\\'}
                max_row_found = False 
            else:    
                print_arr[ each_row_for_dot ][ col_of_vertical_dots]= {'pre_control': '\x1b[33m', 'post_control': '\x1b[0m', 'txt': '.'}
    #one more call for parents 
    if mode == "children":
        fill_vertical_dots(tree,selected_visible_items, print_arr,width, height,h_size,w_size,parent_not_visible_but_child_visible,child_key,mode="parent")

g_prevent_infinite_link_search=[]
def to_node(content,filename,called_from_current_search=False):
    '''filename wont change in current context so we cannot get it from g_context
    called_from_current_search need to know how is calling to_node if its a link search calling it or a true search calling it . this is needed to avoid infinite loop when searching for link data
    '''
    curr_block=''
    start=False
    identified_box_hash=False
    total_items=[]
    dict_items=dict()
    global g_prevent_infinite_link_search
    for i in content:
        if i.startswith('#?#link') and identified_box_hash:
            i = i.rstrip()
            identified_box_hash=False
            lnk = dict([ ( a.split('@')[0],a.split('@')[1].split(',') if ',' in a.split('@')[1] else a.split('@')[1])  for a in i.split('#') if '@' in a ])
            lnk_nodeid = lnk['id'].rstrip()
            lnk_basefilename = lnk['fn'].rstrip()
            if lnk_basefilename not in g_prevent_infinite_link_search:
                g_prevent_infinite_link_search.append(lnk_basefilename)
            else:
                raise Exception("call to filename:{} and nodeid:{} results in infinite link search loop".format(lnk_basefilename, lnk_nodeid))
            lnk_filename=None
            if lnk_basefilename in g_context['all_file_dict']:
                lnk_filename = g_context['all_file_dict'][lnk_basefilename] 
            else:
                raise Exception("link error for node id:"+lnk_nodeid+" and temp_filename:"+lnk_basefilename)
            if lnk_basefilename not in g_context: set_g_context(lnk_filename,False)
            found=False
            for each_node in g_context[lnk_basefilename]['tree']:
                #print( each_node['id'] ,  temp_nodeid , type(each_node['id']), type(temp_nodeid))
                if each_node['id'] == lnk_nodeid:
                    #curr_block += each_node['data']
                    dict_items['links'].append(each_node)
                    found=True
                    break
            if not found: raise Exception("link referenced node not found filename and nodeid are:",lnk_filename,lnk_nodeid)
        if i.startswith('#?#box'):
            if called_from_current_search: g_prevent_infinite_link_search=[]#reset for each box only for current search file
            i = i.rstrip()
            identified_box_hash=True
            if start:
                dict_items['data']=curr_block
                curr_block=''
                total_items.append(dict_items)
            else:
                start=True 
            items=i.split('#')
            dict_items={'links':[],'_filename':filename}
            for j in items:
                if '@' in j:
                    key=j.split('@')[0]
                    value=j.split('@')[1]
                    if key.lower() in ['parent','children','tag']:
                        value=value.split(',') if value.strip()!='' else []
                    dict_items[key]=value
            #dict_items = dict([ ( a.split('@')[0],a.split('@')[1].split(',') if ',' in a.split('@')[1] else a.split('@')[1])  for a in i.split('#') if '@' in a ])
        elif identified_box_hash:
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

def node_search_by_child(tree,node_id, child_key='children'):
    #print('node_search_by_child: searching for ',node_id)
    selectedNodes=[]
    for i in tree:
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
    
def match_node_property(node_list,value=[''],property_name=['tag','name'],include_context_as_tag=True):
    selectedNodes=[]
    for j in node_list:
        match=[]
        for i in value:
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
    
def parse_command(tree,command,args_property):
    #cmd = list(re.split('([\>\&])',command))
    cmd = list(command.split('>'))
    selectedNodes=tree
    prev_node = None
    for i in cmd:
        cmd_parts=i.split('?')
        node=cmd_parts[0].split(',') if cmd_parts[0]!='' else []
        tag =cmd_parts[1].split(',') if len(cmd_parts)>1 and cmd_parts[1]!='' else []
        if '*' in tag:
            return tree
        #print(node,tag)
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
        prevNode = get_parent(tree,selectedNodes[0]['id']) 
        if len(childNodes) == 0:
            start=input( color_word( 'end of road e: to end b: to go back', 'RED' )  ).rstrip()
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
            
            start=input(color_word ( 'choose starting point: b for prev' , "GREEN" )  )
        if start=='b':
            if not prevNode: #this has no parent so we cannot go back 
                selectedNodes = selectedNodes
            else:
                selectedNodes = [ prevNode ]
        else:
            selectedNodes= [childNodes[int(start)]]

def file_to_tree(filename,called_from_current_search=False):
    content=file_to_list(filename)
    return to_node(content,filename,called_from_current_search)

g_context=dict()
g_context['tree']=[]
g_ephemeral_tree: list= [{'calculatedX': '0', 'calculatedY': '0', '_ephemeral_children': [], 'children': [] , 'name': 'seed' , 'id': 'seed', 'parent': [], 'x': '0', 'y': '0', 'data': 'seed', '_filename':'dummy', }]
def set_g_context(filename,change_current_context=False,called_from_current_search=False):
    #print('===',args,filename)
    global g_context
    base_file_name=os.path.basename(filename)
    tree=file_to_tree(filename,called_from_current_search)
    context=[ j.rstrip() for i in tree if i['id']=='seed' and 'tag' in i for j in i['tag']]
    context=[i.rstrip() for i in context]
    if change_current_context:
        g_context['filename']=filename
        g_context['basefilename']=base_file_name
        g_context['tree']=tree
        g_context['context']=context
        set_color_context()
    # maintain history also in g_context under key nodeid
    g_context[base_file_name]={'filename': filename,'basefilename': base_file_name,'tree': tree,'context': context }
    
def search(filename):
    set_g_context(filename,True,True)
    print("context is:",g_context['context'])
    if args.search!='' and args.search is not None:
        args_property = args.property.split(',') if args.property != '' else ['name','tag']
        args_level = args.level
        filtered_nodes = parse_command(g_context['tree'],args.search,args_property)
        if filtered_nodes:
            input('Match found in:'+filename)
            build_tree_from_result(filtered_nodes)
    if args.dive=='true' and args.dive is not None:
        dive_mode(g_context['tree'])

def identify_files(key='all',filename=None):
    files=file_list=[]
    if os.getcwd().startswith('C:\\Users\\mithu'):
        base_dir='C:\\Users\\mithu'
        file_list = {'reference' : [base_dir+r'\Downloads\track\projects\d3\core\data\*[0-9].txt', # non recursive
                    base_dir+r'\Downloads\track\projects\**\quickref.txt',# ** means recursive
                    #r'G:\My Drive\Downloads\jarvis\tech\**\py*.txt' not all files are converted now
                    ],
                'spark' : [base_dir+r'\Downloads\track\projects\d3\core\data\sp*.txt'],
                'secret' : [base_dir+r'\Downloads\track\projects\d3\privateData\*[0-9].txt'],
                'quickref' : [base_dir+r'\Downloads\track\**\*quickref*.txt'],
                }
    elif os.getcwd().startswith('/storage/emulated/0/download'):
        file_list = {'reference' : [r'/storage/emulated/0/download*[0-9].txt', 
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
        chosen_file_list=[filename]
    else:
        raise Exception("No matching files")
    return chosen_file_list

def main(args):
    files=identify_files(args.key,args.filename)
    #print(files)
    #dont make it complicated search each file individually
    for filename in files:
        if args.filename is not None:
            if input('do you want to process this file:\n'+filename+'?\nenter y').rstrip() in ['y']:
                pass 
            else:
                continue
        print( color_word( 'processing file:'+ filename, 'YELLOW') )
        search(filename)


parser = argparse.ArgumentParser()
parser.add_argument("-k","--key", help="search by key reference,nifi instead of file")
parser.add_argument("-f","--filename", help="increase output verbosity")
parser.add_argument("-s","--search", help="increase output verbosity")
parser.add_argument("-d","--dive", help="dive into tree ",nargs="?",default='false',const="true")
parser.add_argument("-p","--property", help="increase output verbosity", default="name,tag")
parser.add_argument("-l","--level", help="increase output verbosity", default=100)
parser.add_argument("-e","--expand", help="node data", default=100)
parser.add_argument("-c","--choosenode", help="choosenode",nargs="?",default='false',const='true') #if just -c value 1 if nothing value false
parser.add_argument("-m","--modeofprint", help="modeofprint",nargs="?",default='read',const='line')
parser.add_argument("-t","--tree", help="tree",nargs="?",default='false',const='true')
parser.add_argument("-v","--vannangal", help="painttext with colors",nargs="?",default='false',const='true')
parser.add_argument("-sc","--screencontrol", help="ansii screencontrol",nargs="?",default='false',const='true')
args = parser.parse_args()    
print(args)
if __name__=="__main__":
    if args.vannangal == "true":
        from colorama import Fore,init
        init(autoreset=True)
    main(args)