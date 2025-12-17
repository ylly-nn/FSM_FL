from lex.lex import *
import logging
import os

BASE_DIR = os.path.dirname(__file__)
LOG_PATH = os.path.join(BASE_DIR, "logs")

# очистка файла логов
open(LOG_PATH, "w", encoding="utf-8").close()

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(funcName)s(): %(message)s",
)

syntax_errors = []


# -----------------------------
# 1. <операции_группы_отношения>::= NE | EQ | LT | LE | GT | GE
# [1,0] | [1,1] | [1,2] | [1,3] | [1,4] | [1,5]
# -----------------------------
def ratio(count):
    logging.info("Проверка <операции_группы_отношения>")
    if lst_tokens[count] in ([1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5]):
        return 0
    return -1


# -----------------------------
# 2. <операции_группы_сложения>::= plus | min | or
# [1,6] | [1,7] | [1,8]
# -----------------------------
def summ(count):
    logging.info("Проверка <операции_группы_сложения>")
    if lst_tokens[count] in ([1, 6], [1, 7], [1, 8]):
        return 0
    return -1


# -----------------------------
# 3. <операции_группы_умножения>::= mult | div | and
# [1,9] | [1,10] | [1,11]
# -----------------------------
def mult(count):
    logging.info("Проверка <операции_группы_умножения>")
    if lst_tokens[count] in ([1, 9], [1, 10], [1, 11]):
        return 0
    return -1


# -----------------------------
# 4. <унарная_операция>::= ~
# [1,12]
# -----------------------------
def unary(count):
    logging.info("Проверка <унарная_операция>")
    if lst_tokens[count] == [1, 12]:
        return 0
    return -1


# -----------------------------
# 5. <логическая_константа>::= true | false
# [0,14] | [0,15]
# -----------------------------
def logical(count):
    logging.info("Проверка <логическая_константа>")
    if lst_tokens[count] in ([0, 14], [0, 15]):
        return 0
    return -1


# -----------------------------
# 6. <множитель>::=
# <идентификатор> | <число> | <логическая_константа> |
# <унарная_операция> <множитель> | "(" <выражение> ")"
# -----------------------------
def multiplicador(count):
    logging.info("Проверка <множитель>")

    # идентификатор
    if lst_tokens[count][0] == 2:
        logging.info("Найден идентификатор %s %s", lst_tokens[count], count)
        return 0, count

    # число
    if lst_tokens[count][0] == 3:
        logging.info("Найдено число %s %s", lst_tokens[count], count)
        return 0, count

    # логическая константа
    if logical(count) != -1:
        logging.info("Найдена логическая константа %s %s", lst_tokens[count], count)
        return 0, count

    # ~ <множитель>
    if unary(count) != -1:
        logging.info("Найдено '~' %s %s", lst_tokens[count], count)
        count += 1
        err, count = multiplicador(count)
        if err != -1:
            logging.info("Найден множитель %s %s", lst_tokens[count], count)
            return 0, count
        logging.error("Ожидается множитель %s %s", lst_tokens[count], count)
        syntax_errors.append("Ошибка проверки <множитель> = ~ <множитель>. Ожидается множитель")
        return -1, -1

    # ( <выражение> )
    if lst_tokens[count] == [1, 19]:
        logging.info("Найдено '(' %s %s", lst_tokens[count], count)
        count += 1

        err, count = expression(count)
        if err == -1:
            logging.error("Ожидается <выражение> %s %s", lst_tokens[count], count)
            syntax_errors.append("Ошибка проверки <множитель> = (выражение). Ожидается выражение")
            return -1, -1

        if lst_tokens[count] != [1, 20]:
            logging.error("Ожидается ')' %s %s", lst_tokens[count], count)
            syntax_errors.append("Ошибка проверки <множитель> = (выражение). Ожидается ')'")
            return -1, -1

        logging.info("Найдено ')' %s %s", lst_tokens[count], count)
        return 0, count

    logging.info("Ошибка проверки <множитель> %s %s", lst_tokens[count], count)
    syntax_errors.append("Ошибка проверки <множитель>")
    return -1, -1


# -----------------------------
# 7. <выражение>::= <операнд> {<операции_группы_отношения> <операнд>}
# -----------------------------
def expression(count):
    while True:
        logging.info("Проверка <выражение>")
        err, count = operand(count)
        if err == -1:
            logging.error("Ожидается операнд %s %s", lst_tokens[count], count)
            syntax_errors.append("Ошибка в проверке <выражение>, ожидается операнд")
            return -1, -1

        logging.info("Найден операнд (конец): %s %s", lst_tokens[count - 1], count - 1)

        if ratio(count) != -1:
            logging.info("Найдена опер_гр_отношения: %s %s", lst_tokens[count], count)
            count += 1
            # дальше снова operand
        else:
            logging.info("Конец проверки <выражение>")
            return 0, count


# -----------------------------
# 8. <операнд>::= <слагаемое> {<операции_группы_сложения> <слагаемое>}
# -----------------------------
def operand(count):
    logging.info("Проверка <операнд>")
    while True:
        err, count = addend(count)
        if err == -1:
            logging.error("Ожидается слагаемое %s %s", lst_tokens[count], count)
            syntax_errors.append("Ошибка в проверке <операнд>, ожидается слагаемое")
            return -1, -1

        logging.info("Найдено слагаемое (конец): %s %s", lst_tokens[count - 1], count - 1)

        if summ(count) != -1:
            logging.info("Найдена опер_гр_сложения: %s %s", lst_tokens[count], count)
            count += 1
        else:
            logging.info("Конец проверки <операнд>")
            return 0, count


# -----------------------------
# 9. <слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>}
# -----------------------------
def addend(count):
    while True:
        logging.info("Проверка <слагаемое>")

        err, count = multiplicador(count)
        if err == -1:
            logging.error("Ожидается множитель %s %s", lst_tokens[count], count)
            syntax_errors.append("Ошибка в проверке <слагаемое>, ожидается множитель")
            return -1, -1

        logging.info("Найден множитель: %s %s", lst_tokens[count], count)
        count += 1

        if mult(count) != -1:
            logging.info("Найдена опер_гр_умн: %s %s", lst_tokens[count], count)
            count += 1
        else:
            logging.info("Конец проверки <слагаемое>")
            return 0, count


# -----------------------------
# 12. <тип>::= % | ! | $
# [0,0] | [0,1] | [0,2]
# -----------------------------
def my_type(count):
    logging.info("Проверка <тип>")
    if lst_tokens[count] in ([0, 0], [0, 1], [0, 2]):
        return 0
    return -1


# -----------------------------
# 11. <описание>::= <идентификатор> {, <идентификатор>} : <тип> ;
# -----------------------------
def descript(count):
    logging.info("Проверка <описание>")

    while True:
        # ':'
        if lst_tokens[count] == [1, 16]:
            logging.info("Проверка ': тип ;' %s %s", lst_tokens[count], count)
            count += 1

            if my_type(count) == -1:
                logging.error("Ожидается тип %s %s", lst_tokens[count], count)
                syntax_errors.append("Ошибка проверки описания. Ожидается тип")
                return -1, -1

            logging.info("Найден тип %s %s", lst_tokens[count], count)
            count += 1

            if lst_tokens[count] != [1, 15]:
                logging.error("Ожидается ';' %s %s", lst_tokens[count], count)
                syntax_errors.append("Ошибка проверки описания. Ожидается ';'")
                return -1, -1

            logging.info("Найдено ';' %s %s", lst_tokens[count], count)
            return 0, count + 1  # следующий после ';'

        # ','
        if lst_tokens[count] == [1, 17]:
            logging.info("Проверка ', идентификатор' %s %s", lst_tokens[count], count)
            count += 1

            if lst_tokens[count][0] != 2:
                logging.error("Ожидается идентификатор %s %s", lst_tokens[count], count)
                syntax_errors.append("Ошибка проверки описания. Ожидается идентификатор")
                return -1, -1

            logging.info("Найден идентификатор %s %s", lst_tokens[count], count)
            count += 1
            continue

        logging.error("Ожидается ',' или ':' %s %s", lst_tokens[count], count)
        syntax_errors.append("Ошибка проверки описания. Ожидается ',' или ':'")
        return -1, -1


# =========================================================
#               ОПЕРАТОРЫ (полностью рабочие)
# =========================================================

# 14. <присваивание>::= <идентификатор> := <выражение>
# ВАЖНО: эта функция ожидает, что count стоит НА идентификаторе
def opr_assignment_stmt(count):
    logging.info("Проверка <оператор_присваивания> (stmt)")

    if lst_tokens[count][0] != 2:
        logging.error("Ожидается идентификатор %s %s", lst_tokens[count], count)
        syntax_errors.append("Ошибка присваивания: ожидается идентификатор")
        return -1, -1
    count += 1

    if lst_tokens[count] != [1, 18]:
        logging.error("Ожидается ':=' %s %s", lst_tokens[count], count)
        syntax_errors.append("Ошибка присваивания: ожидается ':='")
        return -1, -1
    count += 1

    # дальше выражение
    err, count = expression(count)
    if err == -1:
        logging.error("Ожидается выражение после ':='")
        syntax_errors.append("Ошибка присваивания: ожидается выражение")
        return -1, -1

    return 0, count  # count уже следующий после выражения


# 13. begin <оператор> { ; <оператор> } end
def opr_composite(count):
    logging.info("Проверка <оператор_составной>")

    # ждём первый оператор
    err, count = oper(count)
    if err == -1:
        logging.error("Ожидается оператор после begin")
        syntax_errors.append("Ошибка begin-end: ожидается оператор")
        return -1, -1

    # { ; <оператор> }
    while lst_tokens[count] == [1, 15]:
        count += 1
        # допускаем, что перед end может не быть оператора — если у тебя так нельзя, убери этот блок
        if lst_tokens[count] == [0, 4]:  # end
            break

        err, count = oper(count)
        if err == -1:
            logging.error("Ожидается оператор после ';' в begin-end")
            syntax_errors.append("Ошибка begin-end: ожидается оператор после ';'")
            return -1, -1

    # end
    if lst_tokens[count] != [0, 4]:
        logging.error("Ожидается 'end' %s %s", lst_tokens[count], count)
        syntax_errors.append("Ошибка begin-end: ожидается 'end'")
        return -1, -1

    count += 1
    return 0, count


# 15. if "(" <выражение> ")" <оператор> [else <оператор>]
def opr_if(count):
    logging.info("Проверка <оператор_условный>")

    if lst_tokens[count] != [1, 19]:
        logging.error("Ожидается '(' %s %s", lst_tokens[count], count)
        syntax_errors.append("Ошибка if: ожидается '('")
        return -1, -1
    count += 1

    err, count = expression(count)
    if err == -1:
        logging.error("Ожидается выражение в if")
        syntax_errors.append("Ошибка if: ожидается выражение")
        return -1, -1

    if lst_tokens[count] != [1, 20]:
        logging.error("Ожидается ')' %s %s", lst_tokens[count], count)
        syntax_errors.append("Ошибка if: ожидается ')'")
        return -1, -1
    count += 1

    err, count = oper(count)
    if err == -1:
        logging.error("Ожидается оператор после if(...)")
        syntax_errors.append("Ошибка if: ожидается оператор")
        return -1, -1

    if lst_tokens[count] == [0, 6]:  # else
        count += 1
        err, count = oper(count)
        if err == -1:
            logging.error("Ожидается оператор после else")
            syntax_errors.append("Ошибка if: ожидается оператор после else")
            return -1, -1

    return 0, count


# 16. for <присваивание> to <выражение> [step <выражение>] <оператор> next
def opr_for(count):
    logging.info("Проверка <фиксированного_цикла>")

    # ожидаем присваивание (начинается с id)
    err, count = opr_assignment_stmt(count)
    if err == -1:
        logging.error("Ожидается присваивание в for")
        syntax_errors.append("Ошибка for: ожидается присваивание")
        return -1, -1

    if lst_tokens[count] != [0, 8]:  # to
        logging.error("Ожидается 'to' %s %s", lst_tokens[count], count)
        syntax_errors.append("Ошибка for: ожидается 'to'")
        return -1, -1
    count += 1

    err, count = expression(count)
    if err == -1:
        logging.error("Ожидается выражение после to")
        syntax_errors.append("Ошибка for: ожидается выражение после 'to'")
        return -1, -1

    # [step <выражение>]
    if lst_tokens[count] == [0, 9]:  # step
        count += 1
        err, count = expression(count)
        if err == -1:
            logging.error("Ожидается выражение после step")
            syntax_errors.append("Ошибка for: ожидается выражение после 'step'")
            return -1, -1

    # тело цикла = оператор
    err, count = oper(count)
    if err == -1:
        logging.error("Ожидается оператор (тело) в for")
        syntax_errors.append("Ошибка for: ожидается оператор-тело")
        return -1, -1

    if lst_tokens[count] != [0, 10]:  # next
        logging.error("Ожидается 'next' %s %s", lst_tokens[count], count)
        syntax_errors.append("Ошибка for: ожидается 'next'")
        return -1, -1
    count += 1

    return 0, count


# 17. while "(" <выражение> ")" <оператор>
def opr_while(count):
    logging.info("Проверка <условного_цикла>")

    if lst_tokens[count] != [1, 19]:
        logging.error("Ожидается '(' %s %s", lst_tokens[count], count)
        syntax_errors.append("Ошибка while: ожидается '('")
        return -1, -1
    count += 1

    err, count = expression(count)
    if err == -1:
        logging.error("Ожидается выражение в while")
        syntax_errors.append("Ошибка while: ожидается выражение")
        return -1, -1

    if lst_tokens[count] != [1, 20]:
        logging.error("Ожидается ')' %s %s", lst_tokens[count], count)
        syntax_errors.append("Ошибка while: ожидается ')'")
        return -1, -1
    count += 1

    err, count = oper(count)
    if err == -1:
        logging.error("Ожидается оператор после while(...)")
        syntax_errors.append("Ошибка while: ожидается оператор")
        return -1, -1

    return 0, count


# 18. readln <идентификатор> {, <идентификатор>}
def opr_readln(count):
    logging.info("Проверка <оператор_ввода>")

    if lst_tokens[count][0] != 2:
        logging.error("Ожидается идентификатор после readln %s %s", lst_tokens[count], count)
        syntax_errors.append("Ошибка readln: ожидается идентификатор")
        return -1, -1
    count += 1

    while lst_tokens[count] == [1, 17]:  # ,
        count += 1
        if lst_tokens[count][0] != 2:
            logging.error("Ожидается идентификатор после ',' в readln %s %s", lst_tokens[count], count)
            syntax_errors.append("Ошибка readln: ожидается идентификатор после ','")
            return -1, -1
        count += 1

    return 0, count


# 19. writeln <выражение> {, <выражение>}
def opr_writeln(count):
    logging.info("Проверка <оператор_вывода>")

    err, count = expression(count)
    if err == -1:
        logging.error("Ожидается выражение после writeln")
        syntax_errors.append("Ошибка writeln: ожидается выражение")
        return -1, -1

    while lst_tokens[count] == [1, 17]:  # ,
        count += 1
        err, count = expression(count)
        if err == -1:
            logging.error("Ожидается выражение после ',' в writeln")
            syntax_errors.append("Ошибка writeln: ожидается выражение после ','")
            return -1, -1

    return 0, count


# ---------------------------------------------------------
# oper(): диспетчер операторов
#
# ВАЖНО:
# - На входе count указывает на первый токен оператора:
#   begin / if / for / while / readln / writeln / id :=
# - На выходе count указывает на первый токен ПОСЛЕ оператора.
# ---------------------------------------------------------
def oper(count):
    logging.info("Проверка <оператор>")

    # begin ... end
    if lst_tokens[count] == [0, 3]:
        logging.info("Найдено 'begin' %s %s", lst_tokens[count], count)
        count += 1
        return opr_composite(count)

    # if ...
    if lst_tokens[count] == [0, 5]:
        logging.info("Найдено 'if' %s %s", lst_tokens[count], count)
        count += 1
        return opr_if(count)

    # for ...
    if lst_tokens[count] == [0, 7]:
        logging.info("Найдено 'for' %s %s", lst_tokens[count], count)
        count += 1
        return opr_for(count)

    # while ...
    if lst_tokens[count] == [0, 11]:
        logging.info("Найдено 'while' %s %s", lst_tokens[count], count)
        count += 1
        return opr_while(count)

    # readln ...
    if lst_tokens[count] == [0, 12]:
        logging.info("Найдено 'readln' %s %s", lst_tokens[count], count)
        count += 1
        return opr_readln(count)

    # writeln ...
    if lst_tokens[count] == [0, 13]:
        logging.info("Найдено 'writeln' %s %s", lst_tokens[count], count)
        count += 1
        return opr_writeln(count)

    # id := ...
    if lst_tokens[count][0] == 2 and lst_tokens[count + 1] == [1, 18]:
        logging.info("Найдено присваивание (id :=) %s %s", lst_tokens[count], count)
        return opr_assignment_stmt(count)

    logging.error("Ожидается оператор, но получено %s %s", lst_tokens[count], count)
    syntax_errors.append("Ошибка проверки <оператор>: ожидается оператор")
    return -1, -1


# =========================================================
# 10. <программа>::= "{" { (<описание> | <оператор>) ";" } "}"
# =========================================================
def prorgam(count):
    logging.info("Проверка <программа>")

    if lst_tokens[count] != [1, 13]:
        syntax_errors.append("Не найдено начало программы: '{'")
        logging.error("Не найдено '{' %s %s", lst_tokens[count], count)
        return -1

    logging.info("Найдено начало: { %s %s", lst_tokens[count], count)
    count += 1

    while True:
        # конец программы
        if lst_tokens[count] == [1, 14]:
            logging.info("Найдено '}' (конец) %s %s", lst_tokens[count], count)
            return 0

        # описание или присваивание на верхнем уровне
        if lst_tokens[count][0] == 2:
            logging.info("Найден идентификатор: %s %s", lst_tokens[count], count)
            count += 1

            # присваивание: id := ...
            if lst_tokens[count] == [1, 18]:
                logging.info("Найдено ':=' %s %s", lst_tokens[count], count)
                count += 1

                err, count = expression(count)
                if err == -1:
                    logging.error("Ошибка в присваивании на верхнем уровне")
                    return -1

                # обязательно ';'
                if lst_tokens[count] != [1, 15]:
                    logging.error("Ожидается ';' %s %s", lst_tokens[count], count)
                    syntax_errors.append("Ошибка: ожидается ';' после присваивания")
                    return -1

                count += 1
                continue

            # описание: id , id : type ;
            if lst_tokens[count] in ([1, 17], [1, 16]):
                err, count = descript(count)
                if err == -1:
                    return -1
                continue

            logging.error("Ожидается описание или присваивание после идентификатора")
            syntax_errors.append("Ошибка: после идентификатора ожидается описание или присваивание")
            return -1

        # оператор на верхнем уровне
        if lst_tokens[count] in ([0, 3], [0, 5], [0, 7], [0, 11], [0, 12], [0, 13]):
            err, count = oper(count)
            if err == -1:
                logging.error("Анализ оператора завершился с ошибкой")
                return -1

            # по грамматике программы после оператора должен быть ';'
            if lst_tokens[count] != [1, 15]:
                logging.error("Ожидается ';' после оператора %s %s", lst_tokens[count], count)
                syntax_errors.append("Ошибка: ожидается ';' после оператора")
                return -1
            count += 1
            continue

        logging.error("Ожидается описание или оператор %s %s", lst_tokens[count], count)
        syntax_errors.append("Ошибка в <программа>: ожидается описание или оператор")
        return -1


# ===================== main =====================
if not lst_err:
    prorgam(0)

if syntax_errors:
    print("❌ERRORS:")
    print(syntax_errors)
