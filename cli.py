import re 
import sys
import argparse
import glob
import os, platform
if platform.system() == 'Windows': import msvcrt

g_clrs={
    'default': {'white':[]},
    'kubernetes':{'magenta':['service','node','pod','container'],'yellow':['etcd','go','kubernetes','docker']},
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
    context_resolver=list(set(g_context).intersection(set(g_clrs.keys())))
    g_color_context= context_resolver[0] if context_resolver else 'default'

@color_gate
def color_block( word, color):
    """ just give color dont care of context or word or line or nothing , just color the block """
    each_color = give_color(color,True)
    return each_color['pre_control'] + word + each_color['post_control']
    
#only color functions should call this 
def give_color(color,clear=False):
    clear_value = '' 
    if clear: clear_value = '\033[0m'
    if color.upper() == "WHITE": 
        return { 'pre_control' : '' , 'post_control':  '' }
    else:
        return { 'pre_control' : getattr(Fore,color) , 'post_control':  clear_value }

@color_gate
def color_word(word,context=False,color="WHITE"):
    if not context:
        each_color = give_color(color,True)
        return each_color['pre_control'] + word + each_color['post_control']
    else:
        curr_clr='WHITE' 
        for clr,value in g_clrs[g_color_context].items():
            if word.lower() in  value:
                curr_clr=clr.upper()
                break
        each_color = give_color(curr_clr,True)
        return each_color['pre_control'] + word + each_color['post_control']

@color_gate
def color_line(line,context=False,color="WHITE") -> list:
    words = list(re.split('(\W)', line))
    colored_line = []
    for word in words:
        colored_line .append( color_word( word, context, color ) )
    return colored_line

def colored_print(text):
    lines = text.split('\n')
    colored_line = ''
    for line in lines:
        colored_line = color_line(line, True)
        if args.modeofprint=='word': 
            for word in colored_line: 
                print( word , end='')
                input()
        else:
            print( ''.join(colored_line) )
            if args.modeofprint=='line': 
                input()   
    
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
    start_node['level']=1
    while stack:
        node = stack.pop(0)
        if node['id'] not in visited:
            output.append(node)
            visited.append(node['id'])
            #print(node)
            child_list=node[child_key]
            child_list=node_search_by_id(graph,child_list)
            for i in child_list:
                i['level']=node['level']+1
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
        if i['level']<=int(args.level):
            if args.expand=='node':
                print(i)
            elif args.expand=='data':
                print(i['data'])
            else:
                tag=i['tag'] if 'tag' in i else ""
                curr_level=i['level']-1
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
                parent = node_search_by_child(g_global_tree, v_each_item['id'] ,  )
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

def displayTree(tree):
    #print('calling display tree')
    res=[]
    #for i in tree: print(i['name'])
    seed = node_search_by_id(g_global_tree,['seed'])[0]
    #parent_node = getNoParentNode(tree)
    #parent_node_ids = list ( set(map(lambda d:d['id'],parent_node)).difference({'seed'}) )
    #if seed not in result seed must be added as root 
    #seed['children']=[ i for i in parent_node_ids ] # clear out existing children we are building new graph
    #parent_node = seed
    #the tree generated here is actually disconnected example if a child in 3rd level is selccted and grand parent is selected it is not attached to grand parent so we are going to attach it to closest ancestor
    if 'seed' not in [ i['id'] for i in tree  ]: tree.insert(0,seed)
    tree = build_partial_tree(tree,seed)
    #print(tree)
    #input()
    res=dfs(tree,seed) 
    #print('dfs result is \n',res)
    #input()
    if args.tree == 'false':
        showDFSOutput(res)
    else:
        build_table(seed,tree)

def get_index_of_table(item,lst: []):
    for n,i in enumerate(lst):
        for m,j in enumerate(i):
            if j and 'id' in j and j['id'] == item['id']:
                return [n,m]
    print('could not get index of item')
    sys.exit(1)

def build_table(parent_node,tree,child_key='_children'):
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
    print_table(tree,table,parent_node)

def solve_it( curr_arr_pos, first_block_in_scope , block_size, shift_value, total_size ):
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

generated_node_ids = { 'ids': [ [ i+j, 2 ] for i in list('abcdefghijklmnopqrstuvwxyz0123456789') for j in list('abcdefghijklmnopqrstuvwxyz0123456789') ], 'curr_id': 0 }
def generate_node_id():
    global generate_node_ids
    id_list = generated_node_ids['ids']
    generate_value = id_list [ generated_node_ids['curr_id'] ][0]
    if generated_node_ids['curr_id'] + 1  >= len( id_list ):
        generated_node_ids['curr_id'] = 0
    else:
        generated_node_ids['curr_id'] += 1
    return generate_value
        


def build_array_table(tree,table,start_node,height=30,width=150,w_size = 15  ,w_shift=0, h_shift=0, h_size = 1   , pre_dots = 1 , post_dots = 2 , child_key = '_children'):
    #print('===============',len(table),len(table[0]))
    #for i in table: print(len(i))
    start_x, start_y = get_index_of_table( start_node , table )
    print("starting is ",start_x,start_y)
    first_w_block_in_scope = w_size
    first_h_block_in_scope = h_size
    option = ''
    print("starting is ",start_x,start_y,first_w_block_in_scope,first_h_block_in_scope)
    while option != 'q':
        start_y, cols, first_w_block_in_scope = solve_it( start_y, first_w_block_in_scope, w_size, w_shift, width)
        start_x, rows, first_h_block_in_scope = solve_it( start_x, first_h_block_in_scope, h_size, h_shift, height)
        sum = 0
        for i in rows: sum += i['b']
        if sum != height: raise Exception('sorry the rows size did not match')
        sum = 0
        for i in cols: sum += i['b']
        if sum != width:   raise Exception('sorry the cols size did not match')
        print(rows)
        print(cols)
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
                    print_row += [ {'data':' '} for i in range(width) ]
                    running_width+=width
                else:
                    for n_col,col in enumerate(cols):
                        if row['p'] >= 0 and row['p'] < len(table) and col['p'] >=0 and col['p'] < len(table[0]) and table [ row['p'] ] [ col['p'] ]:
                            obj = table [ row['p'] ] [ col['p'] ]
                            name =  obj['name']
                            pre_dot_char = '-'
                            post_dot_char = '-' if obj['_children'] else ' ' 
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
                                name = '-' * available_string_size + name 
                                name += ( '-' if obj['_children'] else ' ' ) * (available_string_size + available_string_odd_even)
                            name = '-'*pre_dots + name +  post_dot_char*post_dots
                            if n_col == 0 :
                                name = name[-col['b']:]
                            else:
                                name = name[0:col['b']]
                            #print_row+=name
                            print_row+= [{ 'data': each_letter } for each_letter in name ]
                            selected_visible_items.append( { 'obj': obj , 'curr_row_in_table': n_row , 'curr_col_in_table': n_col,  'print_arr_row': running_height , 'print_arr_start': running_width, 'print_arr_end': running_width + len(name)  } )
                            running_width+=len(name)
                            #print(name,len(name),col ['b'])
                        else:
                            name=([' '] * col ['b'] )
                            #print(name,len(name),col ['b'])
                            #print_row+=name
                            print_row+= [{ 'data': each_letter } for each_letter in name ]
                            running_width+=len(name)
                print_arr.append(print_row)
                #print(print_row)
                #print(len(print_row))
                #input()
                #print(print_row)
                #print(''.join(print_row) )
                running_height += 1
        fill_vertical_dots(tree,selected_visible_items, print_arr,width,height,h_size,w_size)
        #clear_screen_for_print()
        #print(h_shift,w_shift)
        for line in print_arr:
            each_line=''
            for letter in line:
                if 'pre_color' in letter: line += letter['pre_color']
                each_line += letter['data']
                if 'post_color' in letter: line += letter['post_color']
            print(each_line)
        
        '''i_h_shift = input('enter h_shift').rstrip()
        h_shift = int(i_h_shift) if i_h_shift else 0
        i_w_shift = input('enter w_shift').rstrip()
        w_shift = int(i_w_shift) if i_w_shift else 0'''
        h_shift = w_shift = 0
        default_shift = 3
        pop_item = None
        print(" i j k l for navigation, c for custom input , q for quit[press q without enter]")
        if platform.system() == 'Windows':
            i_ip_value = msvcrt.getch().decode("utf-8")
            shift_by_how_much = default_shift
        if i_ip_value == 'c' or platform.system() != 'Windows' : # custom , then revert to normal input 
            i_ip_value = input('enter [ijkl][N] for moving, id for viewing, q for quit ').rstrip()
            if i_ip_value[0] in ['i','j','k','l']:
                shift_by_how_much = int(i_ip_value[1:]) if i_ip_value[1:] else default_shift
                i_ip_value=i_ip_value[0]
        if i_ip_value == 'q':
            option = 'q'
        if i_ip_value == 'i':
            h_shift = shift_by_how_much
        if i_ip_value == 'k':
            h_shift = - shift_by_how_much
        if i_ip_value == 'j':
            w_shift = shift_by_how_much
        if i_ip_value == 'l':
            w_shift = - shift_by_how_much
        if len(i_ip_value) == 2 :
            for i in selected_visible_items:
                if i['obj']['_print_arr_name']==i_ip_value:
                    colored_print( i['obj']['data'] )
                    break
            input()
                    
def clear_screen_for_print():
    for i in range(os.get_terminal_size().lines): print()
    #pass
    print('\033[{hgt}A'.format(hgt=os.get_terminal_size().lines+1),end='',flush=True)
    
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
            parent_of_visible_item =  node_search_by_child ( tree, i['obj']['id'] )
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
            #print(min_row, max_row)
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
                #print(each_child_id,min_row,max_row)
            
        if mode == "parent":
            col_of_vertical_dots = arr_start - 1
        else:
            col_of_vertical_dots = i ['print_arr_end'] - 1 
        #print(min_row, max_row , col_of_vertical_dots , len(print_arr) , len(print_arr[0]) )
        for each_row_for_dot in range(min_row, max_row ):
            #print(each_row_for_dot , col_of_vertical_dots)
            if min_row_found and max_row > 1:
                print_arr[ each_row_for_dot ][ col_of_vertical_dots]['data'] = '/'
                min_row_found = False 
            elif max_row_found and max_row > 1 and each_row_for_dot == max_row - 1:
                print_arr[ each_row_for_dot ][ col_of_vertical_dots]['data'] = '\\'
                max_row_found = False 
            else:    
                print_arr[ each_row_for_dot ][ col_of_vertical_dots]['data'] = '.'
    #one more call for parents 
    if mode == "children":
        fill_vertical_dots(tree,selected_visible_items, print_arr,width, height,h_size,w_size,parent_not_visible_but_child_visible,child_key = "_children",mode="parent")

def print_table(tree,table,parent_node):
    #print(table)
    '''for i in table:
        for j in i:
            if j:
                print('{:<10}'.format(j['name'][:10]),end=' ')
                #print( j )
            else:
                print('{:<10}'.format(' '*10),end=' ')
                #print( j )
        print()'''
    build_array_table(tree,table,parent_node)
    
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

def node_search_by_child(tree,node_id):
    #print('node_search_by_child: searching for ',node_id)
    selectedNodes=[]
    for i in tree:
        #for j in node_id:
        if node_id in i['children']:
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
                    if include_context_as_tag and not args.filename : property_name_list += g_context #when specific file is chosen then no need to add a tag
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
            start=input( color_block( 'end of road e: to end b: to go back', 'RED' )  ).rstrip()
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
            
            start=input(color_block ( 'choose starting point: b for prev' , "GREEN" )  )
        if start=='b':
            if not prevNode: #this has no parent so we cannot go back 
                selectedNodes = selectedNodes
            else:
                selectedNodes = [ prevNode ]
        else:
            selectedNodes= [childNodes[int(start)]]
        

g_context=[]
g_global_tree=None    
def search(args,filename):
    global g_global_tree
    content=file_to_list(filename)
    g_global_tree=to_node(content)
    global g_context
    context=[ j.rstrip() for i in g_global_tree if i['id']=='seed' and 'tag' in i for j in i['tag']]
    g_context=[i.rstrip() for i in context]
    set_color_context()
    print("context is:",g_context)
    if args.search!='' and args.search is not None:
        args_property = args.property.split(',') if args.property != '' else ['name','tag']
        args_level = args.level
        filtered_nodes = parse_command(g_global_tree,args.search,args_property)
        input('Match found in:'+filename)
        displayTree(filtered_nodes)
    if args.dive=='true' and args.dive is not None:
        dive_mode(g_global_tree)
        
def main(args):
    files=[]
    file_list=[]
    if os.getcwd().startswith('C:\\Users\\mithu'):
        file_list = {'reference' : [r'C:\Users\mithu\Downloads\track\projects\d3\core\data\*[0-9].txt', # non recursive
                    r'C:\Users\mithu\Downloads\track\projects\**\quickref.txt',# ** means recursive
                    #r'G:\My Drive\Downloads\jarvis\tech\**\py*.txt' not all files are converted now
                    ],
                'spark' : [r'C:\Users\mithu\Downloads\track\projects\d3\core\data\sp*.txt'],
                'secret' : [r'C:\Users\mithu\Downloads\track\projects\d3\privateData\*[0-9].txt'],
                'quickref' : [r'C:\Users\mithu\Downloads\track\**\*quickref*.txt'],
                }
    elif os.getcwd().startswith('/storage/emulated/0/download'):
        file_list = {'reference' : [r'/storage/emulated/0/download*[0-9].txt', 
                    ],
                }       
    if args.key and args.key in ('all'):
        chosen_file_list = list({x for v in file_list.values() for x in v})
    elif args.key is not None and args.key != '':
        chosen_file_list = file_list[args.key.lower()]
    else:
        chosen_file_list=[args.filename]
    for i in chosen_file_list:
        files+=glob.glob(i,recursive=True) 
    #print(files)
    #dont make it complicated search each file individually
    
    files=list(set(files))
    if args.key=='all' and args.filename is not None:
        files = [ i for i in files if args.filename in os.path.basename(i) ]
    for filename in files:
        if args.filename is not None:
            if input('do you want to process this file:\n'+filename+'?\nenter y').rstrip() in ['y']:
                pass 
            else:
                continue
        print( color_block( 'processing file:'+ filename, 'YELLOW') )
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
parser.add_argument("-m","--modeofprint", help="modeofprint",nargs="?",default='read',const='line')
parser.add_argument("-t","--tree", help="tree",nargs="?",default='false',const='true')
parser.add_argument("-v","--vannangal", help="painttext with colors",nargs="?",default='false',const='true')
args = parser.parse_args()    
print(args)
if __name__=="__main__":
    if args.vannangal == "true":
        from colorama import Fore,init
        init(autoreset=True)
    main(args)