from lex.lex import *
from dataclasses import dataclass, field
from typing import Any, ClassVar, Iterable


semantic_err=[]

def require_declared_ident(node):
    if not(node.value[1] in dec_var):
        name=ident_name_by_id(node.value[1])
        semantic_err.append("Строка:"+ str(node.line)+". Используется необъявленная переменная: "+ str(name))
        return -1, node
    else:
        node.ast_type=dec_var[node.value[1]]
        return 0, node

##Красивый вывод дерева

def print_ast(node, prefix="", is_last=True):
    if node is None:
        return

    branch = "└─ " if is_last else "├─ "
    if node.value is not None and node.ast_type is None:
        print(prefix + branch + f"{node.kind}: {node.value}, {node.line}")

    if node.value is not None and node.ast_type is not None:
        print(prefix + branch + f"{node.kind}: {node.value} , {node.ast_type}, {node.line}")


    
    if node.value is None:
        if node.ast_type is not None:
            print(prefix + branch + f"{node.kind}, {node.ast_type}")
        else:
            print(prefix + branch + f"{node.kind}")


    new_prefix = prefix + ("   " if is_last else "│  ")

    for i, child in enumerate(node.children):
        print_ast(child, new_prefix, i == len(node.children) - 1)

@dataclass
class AST:
    _counter: ClassVar[int] = 0   # общий счётчик для всех узлов

    kind: str
    value: Any = None
    children: list["AST"] = field(default_factory=list)
    line: int | None = None
    ast_type: list | None = None

    count_kind: int = field(init=False)

    def __post_init__(self):
        self.count_kind = AST._counter
        AST._counter += 1
        

def str_type_by_code(code):
    if code ==[0,0]:
        return 0, "%"
    elif code ==[0,1]:
        return 0, "!"
    elif code ==[0,2]:
        return 0, "$"
    else:
        return -1, ""
    
dec_var={}

def add_dec_var(var_name: str, var_type: str) -> int:
    if var_name in dec_var:
        return -1

    dec_var[var_name] = var_type
    return 0

def walk_ast(root: AST) -> Iterable[AST]:
    """
    DFS-обход дерева AST (preorder): сначала узел, потом его дети слева направо.
    """
    stack = [root]
    while stack:
        node = stack.pop()
        yield node
        # чтобы дети шли слева направо — пушим в стек в обратном порядке
        for child in reversed(node.children):
            stack.append(child)


def add_mult(type_str):
    global _mult_id
    mult[_mult_id] = type_str
    _mult_id += 1
    return _mult_id - 1

def add_sum(type_str):
    global _sum_id
    sum[_sum_id] = type_str
    _sum_id += 1
    return _sum_id - 1

def add_ratio(type_str):
    global _ratio_id
    ratio[_ratio_id] = type_str
    _ratio_id += 1
    return _ratio_id - 1
def num(node): 
    if node.kind=="num":
            ## Присвоение типа
            str_num=str(number_get(int(node.value[1])))
            if str_num.startswith("0b"):
                node.ast_type="%"
            else:
                node.ast_type="!"
    return node

def logical(node):
    if node.kind == "logical":
        node.ast_type="$"
        return 0, node
    else:
        return -1, -1

def expression(node):
    
    if len(node.children)==1:
       
        node.children[0]=operand(node.children[0])
        node.ast_type=node.children[0].ast_type
    else:
      
        lst_ratio=[]
        global ratio, _ratio_id
       
        ratio={}
        _ratio_id=0
        node.ast_type="$"
        print(ratio)

        for child in node.children:
          
            if child.kind!="ratio":
              
                child=operand(child)
                add_ratio(child.ast_type)
            else:
              
                lst_ratio.append(child.value)
            
        if [1, 1] not in lst_ratio:
            if "$" in ratio.values():
                semantic_err.append("Несовпадение типов для операции группы сравнения(не EQ):$")
    
    return node

def operand(node):
    if len(node.children)==1:
        node.children[0]=addend(node.children[0])
        node.ast_type=node.children[0].ast_type
    else:
        global sum, _sum_id
        sum={}
        _sum_id=0
        for child in node.children:
            if child.kind!="sum":
                child=addend(child)
                if child.ast_type=="$":
                    semantic_err.append("Строка:"+ str(child.line)+". Несовпадение типов для операции группы сложения:$")
                else:
                    add_sum(child.ast_type)
        if "!" in sum.values():
            node.ast_type="!"
        else:
            node.ast_type="%"
        
    return node

def addend(node):
    if len(node.children)==1:
        if node.children[0].kind=="ident":
            err, node.children[0]=require_declared_ident(node.children[0])
        
                
                

        if node.children[0].kind=="num":
            node.children[0]=num(node.children[0])
        

            
        
        if node.children[0].kind=="logical":
            node.children[0].ast_type="$"
            


        if node.children[0].kind=="unary":
            node.children[0].ast_type="$"
           

            ast_unary=node.children[0]
            if len(ast_unary.children) == 1:
                ast_unary.children[0]=addend(ast_unary.children[0])

                if ast_unary.children[0].ast_type!="$":
                    semantic_err.append("Строка:"+ str(node.children[0].line)+". Несовпадение типов: ~"+str(ast_unary.children[0].ast_type))

        if node.children[0].kind=="expression":
            ast_expression=node.children[0]
            node.children[0]=expression(ast_expression)
        node.ast_type=node.children[0].ast_type
    
    else:
        flag=0
        global mult, _mult_id
        mult = {}
        _mult_id = 0
        for child in node.children:
            if child.kind =="mult" and child.value==[1,10]:
                flag=1
            if child.kind != "mult":
                child=multiplicador(child)
                
                if child.ast_type=="$":
                    semantic_err.append("Строка:"+ str(child.line)+". Несовпадение типов для операции группы умножения:$")
                else:
                    add_mult(child.ast_type)
        if flag==1:
            node.ast_type="!"
        elif "!" in mult.values():
            node.ast_type="!"
        else:
            node.ast_type="%"
                
                


                        
    
    return node            

def multiplicador(node):
    if node.kind=="ident":        
        err, node=require_declared_ident(node)
        
    
            
            

    if node.kind=="num":
        node=num(node)

        
    
    if node.kind=="logical":
        node.ast_type="$"
        


    if node.kind=="unary":
        node.ast_type="$"
        

        ast_unary=node
        if len(ast_unary.children) == 1:
            ast_unary=addend(ast_unary)

            if ast_unary.ast_type!="$":
                semantic_err.append("Строка:"+ str(node.line)+". Несовпадение типов: ~"+str(ast_unary.ast_type))

    if node.kind=="expression":
        ast_expression=node
        node=expression(ast_expression)


    return node
    
    




def semantic_analysis(ast_program):
    for node in walk_ast(ast_program):
        
      
        ## объвление переменных
        if node.kind == "descript":
            ast_type = node.children[-1]

            for child in node.children[:-1]:
                if child.kind == "ident":
                    err, my_type=str_type_by_code(ast_type.value)
                    if err !=-1:
                        res = add_dec_var(child.value[1], my_type)

                    ## Объявлена ли 1 раз?
                    if res==-1:
                        name=ident_name_by_id(child.value[1])
                        semantic_err.append("Строка:"+ str(child.line)+". Переменная уже объявлена: "+ str(name))
       
        ## присваивание
        elif node.kind=="assigment":
            err, temp_node=require_declared_ident(node)
            if err!=-1:
                node.ast_type=temp_node.ast_type
    
            ast_expression=node.children[0]
            
            node.children[0]=expression(ast_expression)

            if node.children[0].ast_type!=None and node.children[0].ast_type!=node.ast_type :
                if node.ast_type=="$" or node.ast_type=="%":
                    semantic_err.append("Строка:"+ str(node.line)+". Несовпадение типов: "+ str(node.ast_type)+":="+str(node.children[0].ast_type))
                if node.ast_type=="!" and node.children[0].ast_type=="$":
                    semantic_err.append("Строка:"+ str(node.line)+". Несовпадение типов: "+ str(node.ast_type)+":="+str(node.children[0].ast_type))
        
        

    

    print("AST")
    print_ast(ast_program)
