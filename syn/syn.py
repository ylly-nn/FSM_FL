from lex.lex import *
import logging

BASE_DIR = os.path.dirname(__file__)
LOG_PATH = os.path.join(BASE_DIR, "logs")

open(LOG_PATH, "w").close()

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(funcName)s(): %(message)s",
)

syntax_errors=[]


##1. <операции_группы_отношения>::= NE | EQ | LT| LE | GT | GE 
# [1,0] | [1,1] | [1,2] | [1,3] | [1,4] | [1,5]

def ratio(count) :
    logging.info("Проверка <операции_группы_отношения>")
    if lst_tokens[count]==[1,0] or lst_tokens[count]==[1,2] or lst_tokens[count]==[1,3] or lst_tokens[count]==[1,4] or lst_tokens[count]==[1,5]:
        return 0
    else:
        return -1


##2. <операции_группы_сложения>:: = plus | min | or 
# [1,6] | [1,7] | [1,8]


def summ(count):
    logging.info("Проверка <операции_группы_сложения>")
    if lst_tokens[count] == [1,6] or lst_tokens[count] == [1,7] or lst_tokens[count] == [1,8]:
        return 0
    else:
        return -1


##3. <операции_группы_умножения>::= mult| div | and 
# [1,9] | [1,10] | [1,11]

def mult(count):
    logging.info("Проверка <операции_группы_умножения>")
    if lst_tokens[count]==[1,9] or lst_tokens[count]==[1,10] or lst_tokens[count]==[1,11]:
        return 0
    else:
        return -1

##4. <унарная_операция>::= ~
#[1,12]

def unary(count):
    logging.info("Проверка <унарная_операция>")
    if lst_tokens[count]==[1,12]:
        return 0
    else:
        return -1


##5. <логическая_константа>::= true | false 
# [0,14] | [0,15]

def logical(count):
    logging.info("Проверка <логическая_константа>")
    if lst_tokens[count] == [0,14] or lst_tokens[count] == [0,15]:
        return 0
    else:
        return -1
    


##6. <множитель>::= <идентификатор> | <число> | <логическая_константа> <унарная_операция> <множитель>| | « (»<выражение>«)»
# [2,?] | [3,?] | 5 |  4 6 |  [1,19] 7 [1,20]

#! возвращается count на котором закончился анализ
def multiplicador(count):
    logging.info("Проверка <множитель>")
    
    if lst_tokens[count][0]==2:
        logging.info("Найден идентификатор "+ str(lst_tokens[count])+" "+ str(count))
        return 0, count
    
    elif lst_tokens[count][0]==3:
        logging.info("Найдено число "+ str(lst_tokens[count])+" "+ str(count))
        return 0, count
    
    elif logical(count)!=-1:
        logging.info("Найдена логическая константа "+ str(lst_tokens[count])+" "+ str(count))
        return 0, count
    elif unary(count)!=-1:
        logging.info("Найдено '~' "+ str(lst_tokens[count])+" "+ str(count))
        count+=1
        err, count=multiplicador(count)
        if err!=-1:
            logging.info("Найден множитель "+ str(lst_tokens[count])+" "+ str(count))
            return 0, count
        else:
            logging.error(("Ожидается множитель "+ str(lst_tokens[count])+" "+ str(count)))
            syntax_errors.append("Ошибка проверки <множитель> = ~ <множитель>. Ожидается множитель")
            return -1, -1
    elif lst_tokens[count]==[1,19]:
        logging.info("Найдено '(' "+ str(lst_tokens[count])+" "+ str(count))
        count+=1
        err, count=expression(count)

        if err!=-1:
            logging.info("Найдено <выражение> "+ str(lst_tokens[count])+" "+ str(count))

            if lst_tokens[count]==[1,20]:
                logging.info("Найдено ')' "+ str(lst_tokens[count])+" "+ str(count))
                return 0, count 
                
            else:
                logging.error("Ожидается ')' "+ str(lst_tokens[count])+" "+ str(count))
                syntax_errors.append("Ошибка проверки <множитель> = (выражение). Ожидается ')'")
                return -1, -1

        else:
            logging.info("Ожидается <выражение> "+ str(lst_tokens[count-1])+" "+ str(count-1))
            syntax_errors.append("Ошибка проверки <множитель> = (выражение). Ожидается выражение")
            return -1, -1


    else:
        logging.info("Ошибка проверки <множитель> " + str(lst_tokens[count])+" "+ str(count))
        syntax_errors.append("Ошибка проверки <множитель>")
        return -1, -1



##7 <выражение>::= <операнд>{<операции_группы_отношения> <операнд>}
# 8 {1 8}

def expression(count):

    while True:
        logging.info("Проверка <выражение> ")
        err,count = operand(count)
        #! count - следующий после операнда
        if err!=-1:
            # count - 1 чтобы вывести конец операнда
            logging.info("Найден операнд: "+ str(lst_tokens[count-1])+" "+ str(count-1))
            

            if ratio(count)!=-1:
                logging.info("Найдена опер_гр_отношения: "+ str(lst_tokens[count])+" "+ str(count))
                count+=1

            else:
                logging.info("Конец проверки <выражение>")
                return 0, count #! Следующий после проверенного

        else:
            logging.error("Ожидается операнд: "+ str(lst_tokens[count])+" "+ str(count))
            syntax_errors.append("Ошибка в проверке <выражение>, ожидается операнд")
            return -1, -1




##8.<операнд>::= <слагаемое> {<операции_группы_сложения> <слагаемое>}
# 9 {2 9}

def operand(count):
    logging.info("Проверка <операнд>")
    while True:
        err,count=addend(count)
        #! count - следующий после слагаемого
        if err!=-1:
            # count - 1 чтобы вывести конец слагаемого
            logging.info("Найдено слагаемое: "+ str(lst_tokens[count-1])+" "+ str(count-1)) 
            

            if summ(count)!=-1:
                logging.info("Найдена опер_гр_сложения: "+ str(lst_tokens[count])+" "+ str(count))
                count+=1

            else:
                logging.info("Конец проверки <операнд>")
                return 0, count #! Следующий после проверенного

        else:
            logging.error("Ожидается слагаемое: "+ str(lst_tokens[count])+" "+ str(count))
            syntax_errors.append("Ошибка в проверке <операнд>, ожидается слагаемое")
            return -1, -1




##9. <слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>}
# 6 {3 6} 

def addend(count):
    while True:
        logging.info("Проверка <слагаемое>")

        err, count = multiplicador(count)
        if err!=-1:
            logging.info("Найден множитель: "+ str(lst_tokens[count])+" "+ str(count))
            count+=1

            if mult(count)!=-1:
                logging.info("Найдена опер_гр_умн: "+ str(lst_tokens[count])+" "+ str(count))
                count+=1
            else:
                logging.info("Конец проверки <слагаемое>")
                return 0, count #! Следующий после проверенного

        else:
            logging.error("Ожидается множитель: "+ str(lst_tokens[count])+" "+ str(count))
            syntax_errors.append("Ошибка в проверке <слагаемое>, ожидается множитель")
            return -1, -1
    



##10. <программа>::= «{» {/ (<описание> | <оператор>) ; /} «}»
#do [1,13] {/ (11|13-19) [1,15] /} [1,14]

def prorgam(count):
    logging.info("Проверка <программа>")

    '''Поиск начала программы'''
    
    if lst_tokens[count]==[1,13]:
        logging.info("Найдено начало: { "+ str(lst_tokens[count])+" "+ str(count))
        count+=1
    else:
        syntax_errors.append("Не найдено начало программы: { "+ str(lst_tokens[count])+" "+ str(count))
        logging.error("не найдено {")
        return -1
    
    while True:
        ''' 11 - описание + 14 - присваивание'''
        if lst_tokens[count][0]==2:
            logging.info("Найден идентификатор: "+ str(lst_tokens[count])+" "+ str(count))

            count+=1

            '''14 - присваивание'''
            if lst_tokens[count]==[1,18]:
                logging.info("Найдено ':=' "+ str(lst_tokens[count])+" "+ str(count))
                count+=1
                err, count = opr_assignment(count)
                #!count - следующий после присваивания
                if err!=-1:
                    if lst_tokens[count]==[1,15]:
                        logging.info("Найдено ';' "+ str(lst_tokens[count])+" "+ str(count))
                        count+=1
                    else:
                        logging.error("Ожидается ';' "+ str(lst_tokens[count])+" "+ str(count))
                        syntax_errors.append("Ошибка в проверке <программа>: Ожидается: ';'")
                        return -1
                if err==-1:
                    logging.error("Завершение анализа с ошибкой <присваивание>" )
                    return -1


            ##11 - описание
            elif lst_tokens[count]==[1,17] or lst_tokens[count]== [1,16]:
                logging.info("Найдено ',' или ':' "+ str(lst_tokens[count])+" "+ str(count))
                err,count=descript(count) 
                if err==-1:
                    logging.error("Завершение анализа с ошибкой <описание>" )
                    return -1
                

                
            else:
                logging.error("Ожидается: описание или присваивание")
                syntax_errors.append("Ошибка в проверке <программа>: Ожидается: описание или присваивание")

            '''13 - составной оператор'''
        elif lst_tokens[count]==[0,3]:
            logging.info("Вызов opr_composite() (begin)")
            opr_composite()
        
            '''15 - условный оператор'''
        elif lst_tokens[count]==[0,5]:
            logging.info("Вызов opr_if() (if)")
            opr_if()

            '''16 - фиксированного цикла'''
        elif lst_tokens[count]==[0,7]:
            logging.info("Вызов opr_for (for)")
            opr_for

            '''17 - условного цикла'''
        elif lst_tokens[count]==[0,11]:
            logging.info("Вызов opr_while (while)")
            opr_while()


            '''18 - ввода'''
        elif lst_tokens[count]==[0,12]:
            logging.info("Вызов opr_readln() (readln)")
            opr_readln()


            '''19 -вывода'''
        elif lst_tokens[count]==[0,13]:
            logging.info("Вызоы opr_writeln() (writeln)")
            opr_writeln()
        elif lst_tokens[count]==[1,14]:
            logging.info("Найдено '}', КОНЕЦ " +  str(lst_tokens[count])+" "+ str(count))
            print("КОНЕЦ")
            return 0
        else: 
            logging.error("Ожидается описание или оператор " + str(lst_tokens[count])+" "+ str(count))
            syntax_errors.append("Ошибка в проверке <программа>. Ожидается описание или оператор")
            return -1
        print(count)
        print(lst_tokens[count])

    

##11. <описание>::= <идентификатор> {, <идентификатор> } : <тип> ;}
# [2,?]{[1,17] [2,?]} [1,16] 12 [1,15]}

def descript(count):
    logging.info("Проверка <описание>")

    while True:
        ##если ':'
        if lst_tokens[count]==[1,16]:

            logging.info("Проверка ': тип ;' "+ str(lst_tokens[count]) +" "+ str(count))
            count+=1
            if my_type(count)!=-1:
                logging.info("Найден тип " +str(lst_tokens[count])+" "+ str(count))
                count+=1

                if lst_tokens[count]==[1,15]:
                    logging.info("Найдено ';' "+str(lst_tokens[count])+" "+ str(count))
                    logging.info("Завершено без ошибок")
                    return 0, count+1 #! Следующий после проверенного
                else:
                    logging.error("Ожидается: ';' "+ str(lst_tokens[count])+" "+ str(count))
                    syntax_errors.append("Ошибка проверки описания. Ожидается: ';'")
                    return -1, -1
                
            else:
                logging.error("Ожидается тип "+str(lst_tokens[count])+" "+ str(count))
                syntax_errors.append("Ошибка проверки описания. Ожидается тип")
                return -1, -1
            
        ##если ','
        elif lst_tokens[count]==[1,17]:
            logging.info("Проверка ', идентификатор' "+str(lst_tokens[count])+" "+ str(count))
            count+=1

            if lst_tokens[count][0]==2:
                logging.info("Найден идентификатор "+ str(lst_tokens[count])+" "+ str(count))
                count+=1
            else:
                logging.error("Ожидается идентификатор "+str(lst_tokens[count])+" "+ str(count))
                syntax_errors.append("Ошибка проверки описания. Ожидается идентификатор")
                return -1, -1
        else:
            logging.error("Ожидается ',' или ':' "+str(lst_tokens[count])+" "+ str(count))
            syntax_errors.append("Ошибка проверки описания. Ожидается ',' или ':'")
            print(lst_tokens[count])
            return -1, -1


##12. <тип>::=  % | ! | $ 
#do [0,0] | [0,1] | [0,2]

def my_type(count):
    logging.info("Проверка <тип>")
    if lst_tokens[count]==[0,1] or lst_tokens[count]==[0,2] or lst_tokens[count]==[0,0]:
        return 0
    else:
        return -1


## 13. (оператор)<составной>::= begin <оператор> { ; <оператор> } end
#do [0,3] 13-19 {[1,15] 13-19} [0,4]

def opr_composite():
    logging.info("Проверка <оператор_составной>")


## 14. (оператор)<присваивания>::= <идентификатор> :=  <выражение>
# [2,?] [1,18] 7

def opr_assignment(count):
    in_count=count
    logging.info("Проверка <оператор_присваивания> ")
    err, count = expression(count)
    #! count - следующий после выражение
    if err!=-1:
        # count - 1 чтобы вывести конец слагаемого
        logging.info("Найдено выражение " +str(lst_tokens[count-1])+" "+ str(count-1))
        logging.info("Конец проверки <присваивания>")
        return 0, count #! - следующий после поверенного
    else:
        logging.error("Ожидается выражение "+str(lst_tokens[in_count])+" "+ str(in_count))
        syntax_errors.append("Ошибка в проверке <присваивания>. Ожидается выражение ")
        return -1, -1


## 15. (оператор)<условный>::= if «(»<выражение>«)»<оператор> [else <оператор>]
#do [0,5] [1,19] 7 [1,20] 13-19 [[0,6] 13-19]

def opr_if():
    logging.info("Проверка <оператор_условный>")


## 16.<фиксированного_цикла>::= for <присваивания> to <выражение> [step <выражение>] <оператор> next
#do [0,7] 14 [0,8] 7 [[0,9] 7] 13-19 [0,10]

def opr_for():
    logging.info("Проверка <фиксированного_цикла>")


## 17. <условного_цикла>::= while «(» <выражение>«)» <оператор>
#do [0,11] [1,19] 7 [1,20] 13-19

def opr_while():
    logging.info("Проверка <условного_цикла>")


## 18. (оператор) <ввода>::= readln <идентификатор> {, <идентификатор> }
#do [0,12] [2,?] {[1,17] [2,?]}

def opr_readln():
    logging.info("Проверка <оператор_ввода>")


## 19. (оператор) <вывода>::= writeln <выражение> {, <выражение> }
#do [0,13] 7 {[1,17] 7}

def opr_writeln():
    logging.info("Проверка <оператор_вывода>")



'''=====================main================================================='''


if not lst_err:
    # print("not error in lex")
    prorgam(0)

if syntax_errors:
    print("❌ERRORS:")
    print(syntax_errors)


