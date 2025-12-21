from __future__ import annotations

from lex.lex import *
from sem.sem import *

import os
import logging
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple


BASE_DIR = os.path.dirname(__file__)
LOG_PATH = os.path.join(BASE_DIR, "logs")

open(LOG_PATH, "w").close()

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(funcName)s(): %(message)s",
)

syntax_errors: list[str] = []


# ===================== AST =====================

@dataclass
class AST:
    kind: str
    value: Any = None
    children: List["AST"] = field(default_factory=list)
    line: Optional[int] = None
    inferred_type: Optional[str] = None


def line_of(count: int) -> Optional[int]:
    if count is None or count < 0 or count >= len(lst_lines):
        return None
    return lst_lines[count]


def _tok_str(tok: Any) -> str:
    # tok обычно вида [table, id]
    try:
        if isinstance(tok, list) and len(tok) == 2:
            return f"[{tok[0]},{tok[1]}]"
    except Exception:
        pass
    return str(tok)


def print_ast(node: Optional[AST], indent: str = "", is_last: bool = True) -> None:
    if node is None:
        return
    branch = "└─ " if is_last else "├─ "
    head = f"{node.kind}"
    if node.value is not None:
        head += f":{_tok_str(node.value)}"
    if node.line is not None:
        head += f" (line {node.line})"
    print(indent + branch + head)

    new_indent = indent + ("   " if is_last else "│  ")
    for i, ch in enumerate(node.children):
        print_ast(ch, new_indent, i == len(node.children) - 1)


# ===================== Grammar helpers =====================

'''1. <операции_группы_отношения>::= NE | EQ | LT| LE | GT | GE 
# [1,0] | [1,1] | [1,2] | [1,3] | [1,4] | [1,5]'''


def ratio(count):
    logging.info("Проверка <операции_группы_отношения>")
    if (
        lst_tokens[count] == [1, 0]
        or lst_tokens[count] == [1, 1]
        or lst_tokens[count] == [1, 2]
        or lst_tokens[count] == [1, 3]
        or lst_tokens[count] == [1, 4]
        or lst_tokens[count] == [1, 5]
    ):
        return 0
    else:
        return -1


'''2. <операции_группы_сложения>:: = plus | min | or 
# [1,6] | [1,7] | [1,8]'''


def summ(count):
    logging.info("Проверка <операции_группы_сложения>")
    if lst_tokens[count] == [1, 6] or lst_tokens[count] == [1, 7] or lst_tokens[count] == [1, 8]:
        return 0
    else:
        return -1


'''3. <операции_группы_умножения>::= mult | div | and 
# [1,9] | [1,10] | [1,11]'''


def mult(count):
    logging.info("Проверка <операции_группы_умножения>")
    if lst_tokens[count] == [1, 9] or lst_tokens[count] == [1, 10] or lst_tokens[count] == [1, 11]:
        return 0
    else:
        return -1


'''4. <унарная_операция>::= ~
# [1,12]'''


def unary(count):
    logging.info("Проверка <унарная_операция>")
    if lst_tokens[count] == [1, 12]:
        return 0
    else:
        return -1


'''5. <логическая_константа>::= true | false 
# [0,14] | [0,15]'''


def logical(count):
    logging.info("Проверка <логическая_константа>")
    if lst_tokens[count] == [0, 14] or lst_tokens[count] == [0, 15]:
        return 0
    else:
        return -1


'''12. <тип>::=  % | ! | $ 
# [0,0] | [0,1] | [0,2]'''


def my_type(count):
    logging.info("Проверка <тип>")
    if lst_tokens[count] == [0, 1] or lst_tokens[count] == [0, 2] or lst_tokens[count] == [0, 0]:
        return 0
    else:
        return -1


# ===================== Expressions (build AST) =====================
# ВНИМАНИЕ: теперь все функции выражений возвращают (err, count, node),
# где count — следующий индекс после разобранной конструкции.


def multiplicador(count) -> Tuple[int, int, Optional[AST]]:
    logging.info("Проверка <множитель>")

    # <идентификатор>
    if lst_tokens[count][0] == 2:
        add_used_var(count, lst_tokens[count])
        node = AST("ident", value=lst_tokens[count], line=line_of(count))
        return 0, count + 1, node

    # <число>
    if lst_tokens[count][0] == 3:
        node = AST("num", value=lst_tokens[count], line=line_of(count))
        return 0, count + 1, node

    # <логическая_константа>
    if logical(count) != -1:
        node = AST("bool", value=lst_tokens[count], line=line_of(count))
        return 0, count + 1, node

    # <унарная_операция> <множитель>
    if unary(count) != -1:
        op_tok = lst_tokens[count]
        op_line = line_of(count)
        count += 1
        err, count, inner = multiplicador(count)
        if err != -1:
            return 0, count, AST("unary", value=op_tok, children=[inner], line=op_line)

        logging.error("Ожидается множитель после унарной операции")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки <множитель> = ~ <множитель>. Ожидается множитель")
        return -1, -1, None

    # '(' <выражение> ')'
    if lst_tokens[count] == [1, 19]:
        lpar_line = line_of(count)
        count += 1
        err, count, expr_node = expression(count)
        if err == -1:
            logging.error("Ожидается выражение в скобках")
            if count != -1:
                syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
            syntax_errors.append("Ошибка проверки <множитель> = (выражение). Ожидается выражение")
            return -1, -1, None

        if lst_tokens[count] != [1, 20]:
            logging.error("Ожидается ')'")
            if count != -1:
                syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
            syntax_errors.append("Ошибка проверки <множитель> = (выражение). Ожидается ')'")
            return -1, -1, None

        count += 1
        return 0, count, AST("group", children=[expr_node], line=lpar_line)

    logging.error("Ошибка проверки <множитель>")
    if count != -1:
        syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
    syntax_errors.append("Ошибка проверки <множитель>")
    return -1, -1, None


def addend(count) -> Tuple[int, int, Optional[AST]]:
    logging.info("Проверка <слагаемое>")
    err, count, left = multiplicador(count)
    if err == -1:
        logging.error("Ошибка в проверке <слагаемое>, ожидается множитель")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка в проверке <слагаемое>, ожидается множитель")
        return -1, -1, None

    while mult(count) != -1:
        op_tok = lst_tokens[count]
        op_line = line_of(count)
        count += 1

        err, count, right = multiplicador(count)
        if err == -1:
            logging.error("Ошибка в проверке <слагаемое>, ожидается множитель")
            if count != -1:
                syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
            syntax_errors.append("Ошибка в проверке <слагаемое>, ожидается множитель")
            return -1, -1, None

        left = AST("binop", value=op_tok, children=[left, right], line=op_line)

    return 0, count, left


def operand(count) -> Tuple[int, int, Optional[AST]]:
    logging.info("Проверка <операнд>")
    err, count, left = addend(count)
    if err == -1:
        logging.error("Ошибка в проверке <операнд>, ожидается слагаемое")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка в проверке <операнд>, ожидается слагаемое")
        return -1, -1, None

    while summ(count) != -1:
        op_tok = lst_tokens[count]
        op_line = line_of(count)
        count += 1

        err, count, right = addend(count)
        if err == -1:
            logging.error("Ошибка в проверке <операнд>, ожидается слагаемое")
            if count != -1:
                syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
            syntax_errors.append("Ошибка в проверке <операнд>, ожидается слагаемое")
            return -1, -1, None

        left = AST("binop", value=op_tok, children=[left, right], line=op_line)

    return 0, count, left


def expression(count) -> Tuple[int, int, Optional[AST]]:
    logging.info("Проверка <выражение>")
    err, count, left = operand(count)
    if err == -1:
        logging.error("Ошибка в проверке <выражение>, ожидается операнд")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка в проверке <выражение>, ожидается операнд")
        return -1, -1, None

    while ratio(count) != -1:
        op_tok = lst_tokens[count]
        op_line = line_of(count)
        count += 1

        err, count, right = operand(count)
        if err == -1:
            logging.error("Ошибка в проверке <выражение>, ожидается операнд")
            if count != -1:
                syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
            syntax_errors.append("Ошибка в проверке <выражение>, ожидается операнд")
            return -1, -1, None

        left = AST("relop", value=op_tok, children=[left, right], line=op_line)

    return 0, count, left


# ===================== Declarations =====================
# descript оставляем семантически как было, но возвращаем ещё узел decl.


def descript(count):
    logging.info("Проверка <описание>")
    add_dec_var(count - 1, lst_tokens[count - 1], "")
    start_count = count - 1
    id_nodes: List[AST] = [AST("ident", value=lst_tokens[count - 1], line=line_of(count - 1))]

    while True:
        # ':'
        if lst_tokens[count] == [1, 16]:
            logging.info("Проверка ': тип ;' " + str(lst_tokens[count]) + " " + str(count))
            count += 1
            if my_type(count) != -1:
                logging.info("Найден тип " + str(lst_tokens[count]) + " " + str(count))

                # семантика: тип переменных
                if lst_tokens[count] == [0, 0]:
                    var_type = "%"
                elif lst_tokens[count] == [0, 1]:
                    var_type = "!"
                elif lst_tokens[count] == [0, 2]:
                    var_type = "$"
                else:
                    var_type = ""

                for token_count in range(start_count, count):
                    if lst_tokens[token_count][0] == 2:
                        update_type_by_count(token_count, var_type)

                type_tok = lst_tokens[count]
                type_line = line_of(count)
                count += 1

                if lst_tokens[count] == [1, 15]:
                    logging.info("Найдено ';' " + str(lst_tokens[count]) + " " + str(count))
                    logging.info("Завершено без ошибок")
                    decl_node = AST("decl", value=type_tok, children=id_nodes, line=type_line)
                    return 0, count + 1, decl_node  # следующий после ';'
                else:
                    logging.error("Ожидается: ';' " + str(lst_tokens[count]) + " " + str(count))
                    if count != -1:
                        syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
                    syntax_errors.append("Ошибка проверки описания. Ожидается: ';'")
                    return -1, -1, None

            else:
                logging.error("Ожидается тип " + str(lst_tokens[count]) + " " + str(count))
                if count != -1:
                    syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
                syntax_errors.append("Ошибка проверки описания. Ожидается тип")
                return -1, -1, None

        # ','
        elif lst_tokens[count] == [1, 17]:
            logging.info("Проверка ', идентификатор' " + str(lst_tokens[count]) + " " + str(count))
            count += 1

            if lst_tokens[count][0] == 2:
                logging.info("Найден идентификатор " + str(lst_tokens[count]) + " " + str(count))
                add_dec_var(count, lst_tokens[count], "")
                id_nodes.append(AST("ident", value=lst_tokens[count], line=line_of(count)))
                count += 1
            else:
                logging.error("Ожидается идентификатор " + str(lst_tokens[count]) + " " + str(count))
                if count != -1:
                    syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
                syntax_errors.append("Ошибка проверки описания. Ожидается идентификатор")
                return -1, -1, None

        else:
            logging.error("Ожидается ',' или ':' " + str(lst_tokens[count]) + " " + str(count))
            if count != -1:
                syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
            syntax_errors.append("Ошибка проверки описания. Ожидается ',' или ':'")
            return -1, -1, None


# ===================== Statements (build AST) =====================


def opr_assignment(count, lhs_node: AST):
    logging.info("Проверка <оператор_присваивания> ")
    err, count, expr_node = expression(count)
    if err != -1:
        logging.info("Конец проверки <присваивания>")
        return 0, count, AST("assign", value=[1, 18], children=[lhs_node, expr_node], line=lhs_node.line)

    logging.error("Ожидается выражение " + str(lst_tokens[count]) + " " + str(count))
    if count != -1:
        syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
    syntax_errors.append("Ошибка в проверке <присваивания>. Ожидается выражение ")
    return -1, -1, None


def opr_readln(count):
    logging.info("Проверка <оператор_ввода>")
    args: List[AST] = []

    while True:
        if lst_tokens[count][0] == 2:
            logging.info("Найден 'идентификатор'  " + str(lst_tokens[count]) + " " + str(count))
            add_used_var(count, lst_tokens[count])
            args.append(AST("ident", value=lst_tokens[count], line=line_of(count)))
        else:
            logging.error("Ожидается 'идентификатор'  " + str(lst_tokens[count]) + " " + str(count))
            if count != -1:
                syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
            syntax_errors.append("Ошибка проверки <оператор_ввода>. Ожидается 'идентификатор'")
            return -1, -1, None

        count += 1

        if lst_tokens[count] == [1, 17]:
            logging.info("Найдено ','  " + str(lst_tokens[count]) + " " + str(count))
            count += 1
        else:
            logging.info("Конец проверки <оператор_ввода>  " + str(lst_tokens[count]) + " " + str(count))
            return 0, count, AST("readln", children=args, line=args[0].line if args else line_of(count))


def opr_writeln(count):
    logging.info("Проверка <оператор_вывода>")
    args: List[AST] = []

    while True:
        err, count2, expr_node = expression(count)

        if err != -1:
            args.append(expr_node)
            count = count2
        else:
            logging.error("Ожидается 'выражение'  " + str(lst_tokens[count]) + " " + str(count))
            if count != -1:
                syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
            syntax_errors.append("Ошибка проверки <оператор_вывода>. Ожидается 'выражение'")
            return -1, -1, None

        if lst_tokens[count] == [1, 17]:
            logging.info("Найдено ','  " + str(lst_tokens[count]) + " " + str(count))
            count += 1
        else:
            logging.info("Конец проверки <оператор_вывода>  " + str(lst_tokens[count]) + " " + str(count))
            return 0, count, AST("writeln", children=args, line=args[0].line if args else line_of(count))


def opr_composite(count):
    logging.info("Проверка <составной оператор>")
    stmts: List[AST] = []

    # первый оператор
    err, count, stmt = oper(count)
    if err == -1:
        logging.error("Ожидается оператор после begin")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки составного оператора. Ожидается оператор")
        return -1, -1, None
    stmts.append(stmt)

    while lst_tokens[count] == [1, 15]:
        logging.info("Найдено ';' " + str(lst_tokens[count]) + " " + str(count))
        count += 1
        err, count, stmt = oper(count)
        if err == -1:
            logging.error("Ожидается оператор после ';'")
            if count != -1:
                syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
            syntax_errors.append("Ошибка проверки составного оператора. Ожидается оператор")
            return -1, -1, None
        stmts.append(stmt)

    # end
    if lst_tokens[count] == [0, 4]:
        logging.info("Найдено 'end' " + str(lst_tokens[count]) + " " + str(count))
        count += 1
        return 0, count, AST("block", children=stmts, line=stmts[0].line if stmts else line_of(count))
    else:
        logging.error("Ожидается 'end' " + str(lst_tokens[count]) + " " + str(count))
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки составного оператора. Ожидается 'end'")
        return -1, -1, None


def opr_if(count):
    logging.info("Проверка <оператор_условный>")

    # '('
    if lst_tokens[count] == [1, 19]:
        logging.info("Найдено '(' " + str(lst_tokens[count]) + " " + str(count))
    else:
        logging.error("Ожидается '(' " + str(lst_tokens[count]) + " " + str(count))
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки услового опреатора. Ожидается '('")
        return -1, -1, None

    count += 1

    # выражение
    err, count, cond = expression(count)
    if err != -1:
        logging.info("Найдено <выражение> " + str(lst_tokens[count]) + " " + str(count))
    else:
        logging.error("Ожидается <выражение> " + str(lst_tokens[count - 1]) + " " + str(count - 1))
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки if. Ожидается выражение")
        return -1, -1, None

    # ')'
    if lst_tokens[count] == [1, 20]:
        logging.info("Найдено ')' " + str(lst_tokens[count]) + " " + str(count))
    else:
        logging.error("Ожидается ')' " + str(lst_tokens[count]) + " " + str(count))
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки услового опреатора. Ожидается ')'")
        return -1, -1, None

    count += 1

    # then оператор
    err, count, then_stmt = oper(count)
    if err != -1:
        logging.info("Найден оператор  " + str(lst_tokens[count - 1]) + " " + str(count - 1))
    else:
        logging.error("Ожидается оператор " + str(lst_tokens[count]) + " " + str(count))
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки услового опреатора. Ожидается оператор")
        return -1, -1, None

    else_stmt = None
    if lst_tokens[count] == [0, 6]:
        logging.info("Найдено 'else' " + str(lst_tokens[count]) + " " + str(count))
        count += 1
        err, count, else_stmt = oper(count)
        if err == -1:
            logging.error("Ожидается оператор после else")
            if count != -1:
                syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
            syntax_errors.append("Ошибка проверки услового опреатора. Ожидается оператор")
            return -1, -1, None

    children = [cond, then_stmt] + ([else_stmt] if else_stmt else [])
    return 0, count, AST("if", children=children, line=cond.line)


def opr_while(count):
    logging.info("Проверка <условный цикл>")

    # '('
    if lst_tokens[count] == [1, 19]:
        logging.info("Найдено '(' " + str(lst_tokens[count]) + " " + str(count))
    else:
        logging.error("Ожидается '(' " + str(lst_tokens[count]) + " " + str(count))
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки while. Ожидается '('")
        return -1, -1, None

    count += 1

    err, count, cond = expression(count)
    if err == -1:
        logging.error("Ожидается выражение в while")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки while. Ожидается выражение")
        return -1, -1, None

    if lst_tokens[count] == [1, 20]:
        logging.info("Найдено ')' " + str(lst_tokens[count]) + " " + str(count))
    else:
        logging.error("Ожидается ')' " + str(lst_tokens[count]) + " " + str(count))
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки while. Ожидается ')'")
        return -1, -1, None

    count += 1

    err, count, body = oper(count)
    if err == -1:
        logging.error("Ожидается оператор тела while")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки while. Ожидается оператор")
        return -1, -1, None

    return 0, count, AST("while", children=[cond, body], line=cond.line)


def opr_for(count):
    logging.info("Проверка <фиксированный цикл>")

    # ожидается идентификатор
    if lst_tokens[count][0] == 2:
        id_node = AST("ident", value=lst_tokens[count], line=line_of(count))
        add_used_var(count, lst_tokens[count])
        count += 1
    else:
        logging.error("Ожидается идентификатор в for")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки for. Ожидается идентификатор")
        return -1, -1, None

    # ':='
    if lst_tokens[count] == [1, 18]:
        count += 1
    else:
        logging.error("Ожидается ':=' в for")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки for. Ожидается ':='")
        return -1, -1, None

    # начальное выражение
    err, count, start_expr = expression(count)
    if err == -1:
        logging.error("Ожидается начальное выражение в for")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки for. Ожидается выражение")
        return -1, -1, None

    # to (по исходному коду это [0,10])
    if lst_tokens[count] == [0, 10]:
        count += 1
    else:
        logging.error("Ожидается 'to' в for")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки for. Ожидается 'to'")
        return -1, -1, None

    # конечное выражение
    err, count, end_expr = expression(count)
    if err == -1:
        logging.error("Ожидается конечное выражение в for")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки for. Ожидается выражение")
        return -1, -1, None

    # do (по исходному коду это [0,11])
    if lst_tokens[count] == [0, 11]:
        count += 1
    else:
        logging.error("Ожидается 'do' в for")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки for. Ожидается 'do'")
        return -1, -1, None

    # тело
    err, count, body = oper(count)
    if err == -1:
        logging.error("Ожидается оператор тела for")
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки for. Ожидается оператор")
        return -1, -1, None

    return 0, count, AST("for", children=[id_node, start_expr, end_expr, body], line=id_node.line)


def oper(count):
    logging.info("Проверка операторы")

    # 13 - составной оператор: begin ... end
    if lst_tokens[count] == [0, 3]:
        logging.info("Найдено 'begin' " + str(lst_tokens[count]) + " " + str(count))
        begin_line = line_of(count)
        count += 1
        err, count, node = opr_composite(count)
        if err != -1 and node is not None:
            node.line = node.line or begin_line
        return err, count, node

    # 14 - присваивание: <идентификатор> ':=' <выражение>
    elif lst_tokens[count][0] == 2:
        lhs = AST("ident", value=lst_tokens[count], line=line_of(count))
        add_used_var(count, lst_tokens[count])
        count += 1

        if lst_tokens[count] == [1, 18]:
            logging.info("Найдено <идентификатор>':=' " + str(lst_tokens[count]) + " " + str(count))
            count += 1
            err, count, node = opr_assignment(count, lhs)
            return err, count, node
        else:
            logging.error("Ожидается ':=' после идентификатора " + str(lst_tokens[count]) + " " + str(count))
            if count != -1:
                syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
            syntax_errors.append("Ошибка проверки присваивания. Ожидается ':='")
            return -1, -1, None

    # 15 - if
    elif lst_tokens[count] == [0, 5]:
        logging.info("Найдено 'if' " + str(lst_tokens[count]) + " " + str(count))
        count += 1
        err, count, node = opr_if(count)
        return err, count, node

    # 16 - for
    elif lst_tokens[count] == [0, 9]:
        logging.info("Найдено 'for' " + str(lst_tokens[count]) + " " + str(count))
        count += 1
        err, count, node = opr_for(count)
        return err, count, node

    # 17 - while
    elif lst_tokens[count] == [0, 7]:
        logging.info("Найдено 'while' " + str(lst_tokens[count]) + " " + str(count))
        count += 1
        err, count, node = opr_while(count)
        return err, count, node

    # 18 - readln
    elif lst_tokens[count] == [0, 12]:
        logging.info("Найдено 'readln' " + str(lst_tokens[count]) + " " + str(count))
        count += 1
        err, count, node = opr_readln(count)
        return err, count, node

    # 19 - writeln
    elif lst_tokens[count] == [0, 13]:
        logging.info("Найдено 'writeln' " + str(lst_tokens[count]) + " " + str(count))
        count += 1
        err, count, node = opr_writeln(count)
        return err, count, node

    else:
        logging.error("Как вообще сюда попало?")
        return -1, count, None


# ===================== Program (build AST) =====================


def prorgam(count):
    # { <описания и операторы> }
    if lst_tokens[count] != [1, 13]:
        logging.error("Ожидается '{' " + str(lst_tokens[count]) + " " + str(count))
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки программы. Ожидается '{'")
        return -1, None

    start_line = line_of(count)
    count += 1
    items: List[AST] = []

    while True:
        # конец программы
        if lst_tokens[count] == [1, 14]:
            count += 1
            return 0, AST("program", children=items, line=start_line)

        # описание начинается с идентификатора и затем ',' или ':'
        if lst_tokens[count][0] == 2:
            # безопасная проверка следующего токена
            nxt = lst_tokens[count + 1] if (count + 1) < len(lst_tokens) else None
            if nxt in ([1, 16], [1, 17]):  # ':' или ','
                count += 1
                err, count, decl_node = descript(count)
                if err == -1:
                    return -1, None
                if decl_node is not None:
                    items.append(decl_node)
                continue

            # иначе это присваивание / оператор
            err, count, stmt = oper(count)
            if err == -1:
                return -1, None
            if lst_tokens[count] != [1, 15]:
                logging.error("Ожидается ';' после оператора " + str(lst_tokens[count]) + " " + str(count))
                if count != -1:
                    syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
                syntax_errors.append("Ошибка проверки программы. Ожидается ';'")
                return -1, None
            count += 1
            items.append(stmt)
            continue

        # оператор начинается с ключевого слова
        if lst_tokens[count] in ([0, 3], [0, 5], [0, 7], [0, 9], [0, 12], [0, 13]):
            err, count, stmt = oper(count)
            if err == -1:
                return -1, None
            if lst_tokens[count] != [1, 15]:
                logging.error("Ожидается ';' после оператора " + str(lst_tokens[count]) + " " + str(count))
                if count != -1:
                    syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
                syntax_errors.append("Ошибка проверки программы. Ожидается ';'")
                return -1, None
            count += 1
            items.append(stmt)
            continue

        logging.error("Неожиданный токен в программе " + str(lst_tokens[count]) + " " + str(count))
        if count != -1:
            syntax_errors.append("Строка: " + str(lst_lines[count - 1]))
        syntax_errors.append("Ошибка проверки программы. Неожиданный токен")
        return -1, None


'''===================== main ====================='''

ast_root = None

if not lst_err:
    err, ast_root = prorgam(0)

if syntax_errors:
    print("❌ERRORS:")
    total = len(syntax_errors) - 1
    print(syntax_errors[0])
    for i, err in enumerate(reversed(syntax_errors), start=1):
        if i < total:
            print(err, ":")
        else:
            print(err)
            break

# семантика как было
existence_var()

if semantic_errors:
    semantic_errors.sort(key=lambda e: e[0])
    for error in semantic_errors:
        print(error)

# вывод дерева
if ast_root is not None and not syntax_errors:
    print("\n🌳 AST:")
    print_ast(ast_root)
