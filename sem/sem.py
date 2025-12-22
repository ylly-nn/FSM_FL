from lex.lex import *
from dataclasses import dataclass, field
from typing import Any, ClassVar, Iterable

semantic_err=[]


@dataclass
class AST:
    _counter: ClassVar[int] = 0   # общий счётчик для всех узлов

    kind: str
    value: Any = None
    children: list["AST"] = field(default_factory=list)
    line: int | None = None

    count_kind: int = field(init=False)

    def __post_init__(self):
        self.count_kind = AST._counter
        AST._counter += 1
        


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


def semantic_analysis(ast_program):
    for node in walk_ast(ast_program):

        ## объвление переменных
        if node.kind == "descript":
            ast_type = node.children[-1]

            for child in node.children[:-1]:
                if child.kind == "ident":
                    res = add_dec_var(child.value[1], ast_type.value)

                    ## Объявлена ли 1 раз?
                    if res==-1:
                        name=ident_name_by_id(child.value[1])
                        semantic_err.append("Строка: "+ str(child.line)+". Переменная уже объявлена: "+ str(name))


        if node.kind=="ident" or node.kind=="assigment":
            if not(node.value[1] in dec_var):
                name=ident_name_by_id(node.value[1])
                semantic_err.append("Строка: "+ str(node.line)+" Используется необъявленная переменная: "+ str(name))