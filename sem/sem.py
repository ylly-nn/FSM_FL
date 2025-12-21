from lex.lex import *
from dataclasses import dataclass, field
from typing import Any, ClassVar, List, Optional
##объявленные переменные


@dataclass
class AST:
    _counter: ClassVar[int] = 0   # общий счётчик для всех узлов

    kind: str
    value: Any = None
    children: list["AST"] = field(default_factory=list)

    count_kind: int = field(init=False)

    def __post_init__(self):
        self.count_kind = AST._counter
        AST._counter += 1
        

def swap_ratio_with_next(ast_node):
    """
    Меняет местами каждого ребёнка с kind == "ratio" со следующим ребёнком.
    Пример: [operand, ratio, operand] -> [operand, operand, ratio]
    """
    if ast_node is None or not hasattr(ast_node, "children"):
        return ast_node

    i = 0
    while i < len(ast_node.children) - 1:
        child = ast_node.children[i]

        # kind может отсутствовать у некоторых объектов
        if hasattr(child, "kind") and child.kind == "ratio":
            ast_node.children[i], ast_node.children[i + 1] = (
                ast_node.children[i + 1],
                ast_node.children[i],
            )
            i += 2  # пропускаем следующий, чтобы не менять обратно
        else:
            i += 1

    return ast_node


a = AST("ident", [1,2])
b = AST("num", 1)
c = AST("binop", "+", [a, b])

