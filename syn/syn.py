from lex.lex import *
from sem.sem import *


import logging

BASE_DIR = os.path.dirname(__file__)
LOG_PATH = os.path.join(BASE_DIR, "logs")

open(LOG_PATH, "w").close()

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(funcName)s(): %(message)s",
)

syntax_errors=[]

ast_program=AST("program")

# descript = AST("descript")

# descript.children.append(AST("ident", "a"))
# descript.children.append(AST("ident", "b"))

# node.children.append(descript)
# node.children.append(descript)




##1. <операции_группы_отношения>::= NE | EQ | LT| LE | GT | GE 
# [1,0] | [1,1] | [1,2] | [1,3] | [1,4] | [1,5]

def ratio(count) :
    logging.info("Проверка <операции_группы_отношения>")
    if lst_tokens[count]==[1,0] or lst_tokens[count]==[1,1] or lst_tokens[count]==[1,2] or lst_tokens[count]==[1,3] or lst_tokens[count]==[1,4] or lst_tokens[count]==[1,5]:
        ast_ratio=AST("ratio", lst_tokens[count], line=lst_lines[count])
        return 0, ast_ratio
    else:
        return -1, -1


##2. <операции_группы_сложения>:: = plus | min | or 
# [1,6] | [1,7] | [1,8]


def summ(count):
    logging.info("Проверка <операции_группы_сложения>")
    if lst_tokens[count] == [1,6] or lst_tokens[count] == [1,7] or lst_tokens[count] == [1,8]:
        ast_sum=AST("sum", lst_tokens[count], line=lst_lines[count])
        return 0, ast_sum
    else:
        return -1, -1


##3. <операции_группы_умножения>::= mult| div | and 
# [1,9] | [1,10] | [1,11]

def mult(count):
    logging.info("Проверка <операции_группы_умножения>")
    if lst_tokens[count]==[1,9] or lst_tokens[count]==[1,10] or lst_tokens[count]==[1,11]:
        ast_mult=AST("mult", lst_tokens[count], line=lst_lines[count])
        return 0, ast_mult
    else:
        return -1, -1

##4. <унарная_операция>::= ~
#[1,12]

def unary(count):
    logging.info("Проверка <унарная_операция>")
    if lst_tokens[count]==[1,12]:
        ast_unary=AST("unary", lst_tokens[count], line=lst_lines[count])
        return 0, ast_unary
    else:
        return -1, -1


##5. <логическая_константа>::= true | false 
# [0,14] | [0,15]

def logical(count):
    logging.info("Проверка <логическая_константа>")
    if lst_tokens[count] == [0,14] or lst_tokens[count] == [0,15]:
        ast_logical=AST("logical", lst_tokens[count], line=lst_lines[count])
        return 0, ast_logical
    else:
        return -1, -1
    


##6. <множитель>::= <идентификатор> | <число> | <логическая_константа> <унарная_операция> <множитель>| | « (»<выражение>«)»
# [2,?] | [3,?] | 5 |  4 6 |  [1,19] 7 [1,20]

#! возвращается count на котором закончился анализ
def multiplicador(count):
    logging.info("Проверка <множитель>")
    

    if lst_tokens[count][0]==2:
        logging.info("Найден идентификатор "+ str(lst_tokens[count])+" "+ str(count))
        ast_multiplicador=AST("ident", lst_tokens[count], line=lst_lines[count])
        return 0, count, ast_multiplicador
    
    if lst_tokens[count][0]==3:
        logging.info("Найдено число "+ str(lst_tokens[count])+" "+ str(count))
        ast_multiplicador=AST("num", lst_tokens[count], line=lst_lines[count])
        return 0, count, ast_multiplicador
    
    err, ast_logical=logical(count)
    if err !=-1:
        logging.info("Найдена логическая константа "+ str(lst_tokens[count])+" "+ str(count))
        ast_multiplicador=ast_logical
        return 0, count, ast_multiplicador
    
    err, ast_unary=unary(count)
    if err!=-1:
        logging.info("Найдено '~' "+ str(lst_tokens[count])+" "+ str(count))
        ast_multiplicador=ast_unary
        count+=1
        err, count, ast_multiplicador_children=multiplicador(count)
        if err!=-1:
            logging.info("Найден множитель "+ str(lst_tokens[count])+" "+ str(count))
            ast_multiplicador.children.append(ast_multiplicador_children)
            return 0, count, ast_multiplicador
        else:
            logging.error(("Ожидается множитель "+ str(lst_tokens[count])+" "+ str(count)))
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
            syntax_errors.append("Ошибка проверки <множитель> = ~ <множитель>. Ожидается множитель")
            return -1, -1, -1
        
    if lst_tokens[count]==[1,19]:
        logging.info("Найдено '(' "+ str(lst_tokens[count])+" "+ str(count))
        count+=1
        err, count, ast_expression=expression(count)

        if err!=-1:
            logging.info("Найдено <выражение> "+ str(lst_tokens[count])+" "+ str(count))
            ast_multiplicador=ast_expression
            if lst_tokens[count]==[1,20]:
                logging.info("Найдено ')' "+ str(lst_tokens[count])+" "+ str(count))
                return 0, count , ast_multiplicador
                
            else:
                logging.error("Ожидается ')' "+ str(lst_tokens[count])+" "+ str(count))
                syntax_errors.append("Строка: " + str(lst_lines[count-1]))
                syntax_errors.append("Ошибка проверки <множитель> = (выражение). Ожидается ')'")
                return -1, -1, -1

        else:
            logging.info("Ожидается <выражение> "+ str(lst_tokens[count-1])+" "+ str(count-1))
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
            syntax_errors.append("Ошибка проверки <множитель> = (выражение). Ожидается выражение")
            return -1, -1, -1


    else:
        logging.info("Ошибка проверки <множитель> " + str(lst_tokens[count])+" "+ str(count))
        syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка проверки <множитель>")
        return -1, -1, -1



##7 <выражение>::= <операнд>{<операции_группы_отношения> <операнд>}
# 8 {1 8}

def expression(count):
    ast_expression=AST("expression")
    while True:
        logging.info("Проверка <выражение> ")
        err, count, ast_operand = operand(count)
        ast_expression.children.append(ast_operand)
        #! count - следующий после операнда
        if err!=-1:
            # count - 1 чтобы вывести конец операнда
            logging.info("Найден операнд: "+ str(lst_tokens[count-1])+" "+ str(count-1))
            err, ast_ratio = ratio(count)
            if err!=-1:
                logging.info("Найдена опер_гр_отношения: "+ str(lst_tokens[count])+" "+ str(count))
                ast_expression.children.append(ast_ratio)

                
                count+=1

            else:
                logging.info("Конец проверки <выражение>")
                return 0, count, ast_expression #! count - Следующий после проверенного

        else:
            logging.error("Ожидается операнд: "+ str(lst_tokens[count])+" "+ str(count))
            if count!=-1:
                syntax_errors.append("Строка: " + str(lst_lines[count-1]))
            syntax_errors.append("Ошибка в проверке <выражение>, ожидается операнд")
            return -1, -1, -1




##8.<операнд>::= <слагаемое> {<операции_группы_сложения> <слагаемое>}
# 9 {2 9}

def operand(count):
    logging.info("Проверка <операнд>")
    ast_operand=AST("operand")
    while True:
        err,count, ast_added=addend(count)
        #! count - следующий после слагаемого
        if err!=-1:
            # count - 1 чтобы вывести конец слагаемого
            logging.info("Найдено слагаемое: "+ str(lst_tokens[count-1])+" "+ str(count-1)) 
            ast_operand.children.append(ast_added)
            

            err, ast_summ = summ(count)
            if err!=-1:
                logging.info("Найдена опер_гр_сложения: "+ str(lst_tokens[count])+" "+ str(count))
                ast_operand.children.append(ast_summ)
                count+=1


            else:
                logging.info("Конец проверки <операнд>")
                return 0, count, ast_operand  #! Следующий после проверенного

        else:
            logging.error("Ожидается слагаемое: "+ str(lst_tokens[count])+" "+ str(count))
            if count!=-1:
                syntax_errors.append("Строка: " + str(lst_lines[count-1]))
            syntax_errors.append("Ошибка в проверке <операнд>, ожидается слагаемое")
            return -1, -1, -1




##9. <слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>}
# 6 {3 6} 

def addend(count):
    ast_addend=AST("addend")
    while True:
        logging.info("Проверка <слагаемое>")

        err, count, ast_multiplicador = multiplicador(count)
        if err!=-1:
            logging.info("Найден множитель: "+ str(lst_tokens[count])+" "+ str(count))
            ast_addend.children.append(ast_multiplicador)
            count+=1

            err, ast_mult = mult(count)
            if err!=-1:
                logging.info("Найдена опер_гр_умн: "+ str(lst_tokens[count])+" "+ str(count))
                ast_addend.children.append(ast_mult)
                count+=1
               
            else:
                logging.info("Конец проверки <слагаемое>")
                return 0, count, ast_addend #! Следующий после проверенного

        else:
            logging.error("Ожидается множитель: "+ str(lst_tokens[count])+" "+ str(count))
            if count!=-1:
                syntax_errors.append("Строка: " + str(lst_lines[count-1]))
            syntax_errors.append("Ошибка в проверке <слагаемое>, ожидается множитель")
            return -1, -1, -1
    



##10. <программа>::= «{» {/ (<описание> | <оператор>) ; /} «}»
# [1,13] {/ (11|13-19) [1,15] /} [1,14]

def prorgam(count):    
    logging.info("Проверка <программа>")

    '''Поиск начала программы'''
    
    if lst_tokens[count]==[1,13]:
        logging.info("Найдено начало: { "+ str(lst_tokens[count])+" "+ str(count))
        count+=1
    else:
        syntax_errors.append("Не найдено начало программы: { ")
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
                err, count,  ast_assigmen = opr_assignment(count)
                #!count - следующий после присваивания
                if err!=-1:
                    if lst_tokens[count]==[1,15]:
                        ast_program.children.append(ast_assigmen)
                        logging.info("Найдено ';' "+ str(lst_tokens[count])+" "+ str(count))
                        count+=1
                    else:
                        logging.error("Ожидается ';' "+ str(lst_tokens[count])+" "+ str(count))
                        if count!=-1:
                            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
                        syntax_errors.append("Ошибка в проверке <программа>: Ожидается: ';'")
                        return -1
                if err==-1:
                    logging.error("Завершение анализа с ошибкой <присваивание>" )
                    return -1


            ##11 - описание
            elif lst_tokens[count]==[1,17] or lst_tokens[count]== [1,16]:
                logging.info("Найдено ',' или ':' "+ str(lst_tokens[count])+" "+ str(count))
                err, count, node =descript(count) 
                if err==-1:
                    logging.error("Завершение анализа с ошибкой <описание>" )
                    return -1
                else:
                    ast_program.children.append(node)
                

                
            else:
                logging.error("Ожидается: описание или присваивание")
                if count!=-1:
                    syntax_errors.append("Строка: " + str(lst_lines[count-1]))
                syntax_errors.append("Ошибка в проверке <программа>: Ожидается: описание или присваивание")

        elif lst_tokens[count]==[0,3] or lst_tokens[count]==[0,5] or lst_tokens[count]==[0,7] or lst_tokens[count]==[0,11] or lst_tokens[count]==[0,12] or lst_tokens[count]==[0,13]:
            err, count, ast_oper = oper(count)
             
            if err!=-1:
                logging.info("Найден <оператор> "+ str(lst_tokens[count])+" "+ str(count))
                ast_program.children.append(ast_oper)
            
            else:
                logging.error("Анализ оператора завершился с ошибкой")
                if count!=-1:
                    syntax_errors.append("Строка: " + str(lst_lines[count-1]))
                syntax_errors.append("В проверка <программа> aнализ оператора завершился с ошибкой")
                return -1
            
            if lst_tokens[count]==[1,15]:
                count+=1
                logging.info("Найдено ';' "+ str(lst_tokens[count])+" "+ str(count))
            else:
                logging.error("Ожидается ';' "+ str(lst_tokens[count])+" "+ str(count))
                if count!=-1:
                    syntax_errors.append("Строка: " + str(lst_lines[count-1]))
                syntax_errors.append("Ошибка в проверка программа. Ожидается ';'")
                return -1
    
        elif lst_tokens[count]==[1,14]:
            logging.info("Найдено '}', КОНЕЦ " +  str(lst_tokens[count])+" "+ str(count))
            return 0
        else: 
            logging.error("Ожидается описание или оператор " + str(lst_tokens[count])+" "+ str(count))
            if count!=-1:
                syntax_errors.append("Строка: " + str(lst_lines[count-1]))
            syntax_errors.append("Ошибка в проверке <программа>. Ожидается описание или оператор")
            return -1
        

    

##11. <описание>::= <идентификатор> {, <идентификатор> } : <тип> ;}
# [2,?]{[1,17] [2,?]} [1,16] 12 [1,15]}

def descript(count):
    logging.info("Проверка <описание>")

    ast_descript=AST("descript")

   
   
    #add_dec_var(count-1, lst_tokens[count-1], "")
    start_count=count-1
    while True:
        ##если ':'
        if lst_tokens[count]==[1,16]:

            logging.info("Проверка ': тип ;' "+ str(lst_tokens[count]) +" "+ str(count))
            count+=1
            err, ast_type = my_type(count)
            if err!=-1:
                logging.info("Найден тип " +str(lst_tokens[count])+" "+ str(count))

                #!Семантический

                for token_count in range(start_count, count):
                    if lst_tokens[token_count][0]==2:
                        #update_type_by_count(token_count, var_type)
                        ast_descript.children.append(AST("ident", lst_tokens[token_count], line=lst_lines[count]))
        
                ast_descript.children.append(ast_type)
                
                count+=1


                if lst_tokens[count]==[1,15]:
                    logging.info("Найдено ';' "+str(lst_tokens[count])+" "+ str(count))
                    logging.info("Завершено без ошибок")
                    return 0, count+1, ast_descript #! Следующий после проверенного
                else:
                    logging.error("Ожидается: ';' "+ str(lst_tokens[count])+" "+ str(count))
                    if count!=-1:
                        syntax_errors.append("Строка: " + str(lst_lines[count-1]))
                    syntax_errors.append("Ошибка проверки описания. Ожидается: ';'")
                    return -1, -1, -1
                
            else:
                logging.error("Ожидается тип "+str(lst_tokens[count])+" "+ str(count))
                if count!=-1:
                    syntax_errors.append("Строка: " + str(lst_lines[count-1]))
                syntax_errors.append("Ошибка проверки описания. Ожидается тип")
                return -1, -1, -1
            
        ##если ','
        elif lst_tokens[count]==[1,17]:
            logging.info("Проверка ', идентификатор' "+str(lst_tokens[count])+" "+ str(count))
            count+=1

            if lst_tokens[count][0]==2:
                logging.info("Найден идентификатор "+ str(lst_tokens[count])+" "+ str(count))
                #add_dec_var(count, lst_tokens[count], "")
                count+=1
            else:
                logging.error("Ожидается идентификатор "+str(lst_tokens[count])+" "+ str(count))
                if count!=-1:
                    syntax_errors.append("Строка: " + str(lst_lines[count-1]))
                syntax_errors.append("Ошибка проверки описания. Ожидается идентификатор")
                return -1, -1, -1
        else:
            logging.error("Ожидается ',' или ':' "+str(lst_tokens[count])+" "+ str(count))
            if count!=-1:
                syntax_errors.append("Строка: " + str(lst_lines[count-1]))
            syntax_errors.append("Ошибка проверки описания. Ожидается ',' или ':'")
            print(lst_tokens[count])
            return -1, -1, -1


##12. <тип>::=  % | ! | $ 
# [0,0] | [0,1] | [0,2]

def my_type(count):
    logging.info("Проверка <тип>")
    if lst_tokens[count]==[0,1] or lst_tokens[count]==[0,2] or lst_tokens[count]==[0,0]:
        ast_type=AST("type", lst_tokens[count], line=lst_lines[count])
        return 0, ast_type
    else:
        return -1, -1


## 13. (оператор)<составной>::= begin <оператор> { ; <оператор> } end
# [0,3] 13-19 {[1,15] 13-19} [0,4]

def opr_composite(count):
    ast_composite=AST("begin")
    logging.info("Проверка <оператор_составной>")
    flag=True
    while flag == True: 
        err, count, ast_oper= oper(count)
        if err !=-1:
            logging.info("Найден 'оператор' "+ str(lst_tokens[count])+" "+ str(count))
            ast_composite.children.append(ast_oper)
        else:
            logging.error("Ожидается 'оператор' "+str(lst_tokens[count])+" "+ str(count))
            if count!=-1:
                syntax_errors.append("Строка: " + str(lst_lines[count-1]))
            syntax_errors.append("Ошибка проверки оператора <составной>. Ожидается 'оператор'")
            return -1, -1,-1
        
        if lst_tokens[count]== [1,15]:
            logging.info("Найдено ';' "+ str(lst_tokens[count])+" "+ str(count))
            count+=1
        
        else:
            flag = False
    
    if lst_tokens[count] == [0,4]:
        logging.info("Найдено 'end' "+ str(lst_tokens[count])+" "+ str(count))
        return 0, count+1, ast_composite
    else:
        logging.error("Ожидается 'end' "+str(lst_tokens[count])+" "+ str(count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка проверки оператора <составной>. Ожидается 'end'")
        return -1, -1, -1
    


## 14. (оператор)<присваивания>::= <идентификатор> :=  <выражение>
# [2,?] [1,18] 7

def opr_assignment(count):
    ast_assigment=AST("assigment", lst_tokens[count-2], line=lst_lines[count-2])
    in_count=count
    logging.info("Проверка <оператор_присваивания> ")
    err, count, ast_expression = expression(count)
    
    #! count - следующий после выражение
    if err!=-1:
        # count - 1 чтобы вывести конец слагаемого
        logging.info("Найдено выражение " +str(lst_tokens[count-1])+" "+ str(count-1))
        ast_assigment.children.append(ast_expression)
        logging.info("Конец проверки <присваивания>")
        return 0, count, ast_assigment #! count - следующий после поверенного
    else:
        logging.error("Ожидается выражение "+str(lst_tokens[in_count])+" "+ str(in_count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка в проверке <присваивания>. Ожидается выражение ")
        return -1, -1, -1


## 15. (оператор)<условный>::= if «(»<выражение>«)»<оператор> [else <оператор>]
# [0,5] [1,19] 7 [1,20] 13-19 [[0,6] 13-19]

def opr_if(count):
    ast_if=AST("if")
    logging.info("Проверка <оператор_условный>")

    ## (
    if lst_tokens[count]==[1,19]:
        logging.info("Найдено '(' "+str(lst_tokens[count])+" "+ str(count))
    else:
        logging.error("Ожидается '(' "+str(lst_tokens[count])+" "+ str(count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка проверки услового опреатора. Ожидается '('")
        return -1, -1, -1
    
    count+=1

    ## выражение
    err, count, ast_expression=expression(count)
    if err!=-1:
        logging.info("Найдено <выражение> "+ str(lst_tokens[count])+" "+ str(count))
        ast_if.children.append(ast_expression)

    else:
        logging.info("Ожидается <выражение> "+ str(lst_tokens[count-1])+" "+ str(count-1))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка проверки if. Ожидается выражение")
        return -1, -1, -1
    
    ## )

    if lst_tokens[count]==[1,20]:
        logging.info("Найдено ')' "+str(lst_tokens[count])+" "+ str(count))
    else:
        logging.error("Ожидается ')' "+str(lst_tokens[count])+" "+ str(count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))  
        syntax_errors.append("Ошибка проверки услового опреатора. Ожидается ')'")
        return -1, -1, -1
    
    count+=1

    ## оператор
    err, count, ast_oper = oper(count)
    if err !=-1:
        logging.info("Найден оператор  "+str(lst_tokens[count-1])+" "+ str(count-1))
        ast_if.children.append(ast_oper)
    else:
        logging.error("Ожидается оператор "+str(lst_tokens[count])+" "+ str(count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка проверки услового опреатора. Ожидается оператор")
        return -1, -1, 1
    
    ## [else оператор]

    if lst_tokens[count]==[0,6]:    
        ast_else=AST("else")
        logging.info("Найдено 'else' " +str(lst_tokens[count])+" "+ str(count))

        count+=1

        err, count, ast_oper = oper(count)

        if err!=-1:
            logging.info("Найден оператор  "+str(lst_tokens[count-1])+" "+ str(count-1))
            ast_else.children.append(ast_oper)
            ast_if.children.append(ast_else)
            return 0, count, ast_if
        else:
            logging.error("Ожидается оператор  "+str(lst_tokens[count])+" "+ str(count))
            if count!=-1:
                syntax_errors.append("Строка: " + str(lst_lines[count-1]))
            syntax_errors.append("Ошибка проверки услового опреатора. Ожидается оператор")
            return -1, -1, -1

    else:
        logging.info("Проверка  <оператор_условный> завершена")
        return 0, count, ast_if








## 16.<фиксированного_цикла>::= for <присваивания> to <выражение> [step <выражение>] <оператор> next
# [0,7] 14 [0,8] 7 [[0,9] 7] 13-19 [0,10]

def opr_for(count):
    ast_for=AST("for")
    logging.info("Проверка <фиксированного_цикла>")
    ## <идентификатор>:=
    if lst_tokens[count][0]==2 and lst_tokens[count+1] == [1,18]:
        logging.info("Найдено 'идентификатор := ' "+str(lst_tokens[count])+" "+ str(count))
        #add_used_var(count, lst_tokens[count])
        count+=2
    else:
        logging.error("Ожидается <присваивания> "+str(lst_tokens[count])+" "+ str(count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка for. Ожидается оператор <присваивания>")
        return -1, -1, -1
    
    ## присваивания
    err, count,  ast_assigmen=opr_assignment(count)
    if err!=-1:
        logging.info("Найдено <присваивания> "+str(lst_tokens[count])+" "+ str(count))
        ast_for.children.append(ast_assigmen)
    else:
        logging.error("Ожидается <присваивания> "+str(lst_tokens[count])+" "+ str(count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка for. Ожидается опреатор <присваивания>")
        return -1, -1, -1

    ## to
    if lst_tokens[count]==[0,8]:
        logging.info("Найдено  'to' "+str(lst_tokens[count])+" "+ str(count))
    else:
        logging.error("Ожидается 'to'  "+str(lst_tokens[count])+" "+ str(count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка for. Ожидается 'to'")
        return -1, -1, -1
    
    count+=1

    ## выражение
    res,count, ast_expression=expression(count)
    if res !=-1:
        logging.info("Найдено  'выражение' "+str(lst_tokens[count])+" "+ str(count))
        ast_for.children.append(ast_expression)
    else:
        logging.error("Ожидается выражение  "+str(lst_tokens[count])+" "+ str(count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка for. Ожидается выражение")
        return -1, -1, -1
    
    ##step
    if lst_tokens[count]==[0,9]:
        ast_step=AST("step")
        logging.info("Найдено 'step' " +str(lst_tokens[count])+" "+ str(count))
        
        count+=1
        
        ##выражение
        err,count, ast_expression = expression(count)
        if err!=-1:
            logging.info("Найдено 'выражение' " +str(lst_tokens[count])+" "+ str(count))
            ast_step.children.append(ast_expression)
            ast_for.children.append(ast_step)
        else:
            logging.error("Ожидается выражение  "+str(lst_tokens[count])+" "+ str(count))
            if count!=-1:
                syntax_errors.append("Строка: " + str(lst_lines[count-1]))
            syntax_errors.append("Ошибка проверки step <выражение>. Ожидается выражение")
            return -1, -1, -1
    
    err, count, ast_oper=oper(count)

    ## оператор
    if err!=-1:
            logging.info("Найден оператор  "+str(lst_tokens[count-1])+" "+ str(count-1))
            ast_for.children.append(ast_oper)
    else:
        logging.error("Ожидается оператор  "+str(lst_tokens[count])+" "+ str(count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка проверки фиксированного цикла. Ожидается оператор")
        return -1, -1, -1
    
    ## next
    if lst_tokens[count]==[0,10]:
        logging.info("Заершён анализ foor")
        return 0, count+1, ast_for
    else:
        logging.error("Ожидается 'next' "+str(lst_tokens[count-1])+" "+ str(count-1))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка проверки фиксированного цикла. Ожидается 'next'")
        return -1, -1, -1
            


    

    
    



## 17. <условного_цикла>::= while «(» <выражение>«)» <оператор>
# [0,11] [1,19] 7 [1,20] 13-19

def opr_while(count):
    ast_while=AST("while")
    logging.info("Проверка <условного_цикла>")

    ## (
    if lst_tokens[count]==[1,19]:
        logging.info("Найдено '('  "+str(lst_tokens[count])+" "+ str(count))
    else:
        logging.error("Ожидается '('  "+str(lst_tokens[count])+" "+ str(count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка проверки <условного_цикла>. Ожидается '('")
        return -1, -1, -1
    
    count+=1

    ##  <выражение>
    err, count, ast_expression = expression(count)

    if err!=-1:
        ast_while.children.append(ast_expression)
        logging.info("Найдено 'выражение'  "+str(lst_tokens[count])+" "+ str(count))
    else:
        logging.error("Ожидается 'выражение'  "+str(lst_tokens[count])+" "+ str(count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка проверки <условного_цикла>. Ожидается 'выражение'")
        return -1, -1, -1
    
    
    ## )
    if lst_tokens[count]==[1,20]:
        logging.info("Найдено ')'  "+str(lst_tokens[count])+" "+ str(count))
    else:
        logging.error("Ожидается ')'  "+str(lst_tokens[count])+" "+ str(count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка проверки <условного_цикла>. Ожидается ')'")
        return -1, -1, -1
    
    count+=1

    ## <опрератор>
    err, count, ast_oper = oper(count)
    if err!=-1:
        ast_while.children.append(ast_oper)
        logging.info("Найден 'оператор'  "+str(lst_tokens[count])+" "+ str(count))
        logging.info("Завершена проверка <условного_цикла>")
        return 0, count, ast_while
    else:
        logging.error("Ожидается 'оператор'  "+str(lst_tokens[count])+" "+ str(count))
        if count!=-1:
            syntax_errors.append("Строка: " + str(lst_lines[count-1]))
        syntax_errors.append("Ошибка проверки <условного_цикла>. Ожидается 'оператор'")
        return -1, -1, -1






## 18. (оператор) <ввода>::= readln <идентификатор> {, <идентификатор> }
# [0,12] [2,?] {[1,17] [2,?]}

def opr_readln(count):
    ast_readln=AST("readln")
    logging.info("Проверка <оператор_ввода>")

    while True:
        ## идентификатор
        if lst_tokens[count][0]==2:
            logging.info("Найден 'идентификатор'  "+str(lst_tokens[count])+" "+ str(count))
            ast_readln.children.append(AST("ident", lst_tokens[count], line=lst_lines[count]))
            #add_used_var(count, lst_tokens[count])
        else:
            logging.error("Ожидается 'идентификатор'  "+str(lst_tokens[count])+" "+ str(count))
            if count!=-1:
                syntax_errors.append("Строка: " + str(lst_lines[count-1]))
            syntax_errors.append("Ошибка проверки <оператор_ввода>. Ожидается 'идентификатор'")
            return -1, -1, -1
        
        count+=1

        ## ,
        if lst_tokens[count]==[1,17]:
            logging.info("Найдено ','  "+str(lst_tokens[count])+" "+ str(count))
            count+=1
        else:
            logging.info("Конец проверки <оператор_ввода>  "+str(lst_tokens[count])+" "+ str(count))
            return 0, count, ast_readln


## 19. (оператор) <вывода>::= writeln <выражение> {, <выражение> }
# [0,13] 7 {[1,17] 7}

def opr_writeln(count):
    ast_writeln=AST("writeln")
    logging.info("Проверка <оператор_вывода>")

    while True:
        err, count, ast_expression = expression(count)
        ast_writeln.children.append(ast_expression)
        ## <выражение>
        if err!=-1:
            logging.info("Найдено 'выражение'  "+str(lst_tokens[count])+" "+ str(count))
        else:
            logging.error("Ожидается 'выражение'  "+str(lst_tokens[count])+" "+ str(count))
            if count!=-1:
                syntax_errors.append("Строка: " + str(lst_lines[count-1]))
            syntax_errors.append("Ошибка проверки <оператор_вывода>. Ожидается 'выражение'")
            return -1, -1, -1
        
        ## ,
        if lst_tokens[count] == [1,17]:
            logging.info("Найдено ','  "+str(lst_tokens[count])+" "+ str(count))
            count+=1
        else:
            logging.info("Конец проверки <оператор_вывода>  "+str(lst_tokens[count])+" "+ str(count))
            return 0, count, ast_writeln

def oper(count):
    ast_oper=AST("oper")
    logging.info("Проверка операторы")

    '''13 - составной оператор'''
    if lst_tokens[count]==[0,3]:
        logging.info("Найдено 'begin' "+str(lst_tokens[count])+" "+ str(count))
        count+=1
        err, count, ast_composite = opr_composite(count)
        if err!=-1:
            logging.info("Найден составной опратор")
            ast_oper=ast_composite
            return err, count, ast_oper
        else:
            return -1, -1, -1

        '''14 - оператор присваивания'''
    elif lst_tokens[count][0]==2 and lst_tokens[count+1]==[1,18]:
        logging.info("Найдено <идентификатор>':=' "+str(lst_tokens[count])+" "+ str(count))
        #add_used_var(count, lst_tokens[count])
        count+=2
        err, count, ast_assigmen = opr_assignment(count)
        if err !=-1:
            ast_oper=ast_assigmen
            return err, count, ast_oper
        else:
            return -1, -1, -1

        '''15 - условный оператор'''
    elif lst_tokens[count]==[0,5]:
        logging.info("Найдено 'if' "+ str(lst_tokens[count])+" "+ str(count))
        count+=1
        
        err, count, ast_if=opr_if(count)
        
        if err!=-1:
            logging.info("Найден <оператор_условный> "+ str(lst_tokens[count])+" "+ str(count))
            ast_oper=ast_if
            return err, count, ast_oper
        else:
            logging.info("Ожидается <оператор_условный> "+ str(lst_tokens[count])+" "+ str(count))
            if count!=-1:
                syntax_errors.append("Строка: " + str(lst_lines[count-1]))
            syntax_errors.append("Оператор if. Ожидается <оператор_условный")
            return -1,-1, -1
        
        

        '''16 - фиксированного )цикла'''
    elif lst_tokens[count]==[0,7]:
        logging.info("Найдено 'for' "+ str(lst_tokens[count])+" "+ str(count))
        count+=1
        err, count, ast_for=opr_for(count)
        if err!=-1:
            ast_oper=ast_for
            return err, count, ast_oper
        else:
            return -1, -1, -1

        '''17 - условного цикла'''
    elif lst_tokens[count]==[0,11]:
        logging.info("Найдено 'while' "+ str(lst_tokens[count])+" "+ str(count))
        count+=1
        err, count, ast_while=opr_while(count)
        if err!=-1:
            ast_oper=ast_while
            return err, count, ast_oper
        else:
            return -1, -1, -1


        '''18 - ввода'''
    elif lst_tokens[count]==[0,12]:
        logging.info("Найдено 'readln' "+ str(lst_tokens[count])+" "+ str(count))
        count+=1
        err, count, ast_readln=opr_readln(count)
        if err!=-1:
            ast_oper=ast_readln
            return err, count, ast_oper
        else:
            return -1, -1, -1


        '''19 -вывода'''
    elif lst_tokens[count]==[0,13]:
        logging.info("Найдено 'writeln' "+ str(lst_tokens[count])+" "+ str(count))
        count+=1
        err, count, ast_writeln=opr_writeln(count)
        if err!=-1:
            ast_oper=ast_writeln
            return err, count, ast_oper
        else:
            return -1, -1, -1
    else:
        logging.error("Как вообще сюда попало?")
        return -1, count, ast_oper


'''=====================main================================================='''


if not lst_err:
    # print("not error in lex")
    prorgam(0)

if syntax_errors:
    print("❌ERRORS:")

    total = len(syntax_errors)-1
    print (syntax_errors[0])
    for i, err in enumerate(reversed(syntax_errors), start=1):
        if i < total:
            print(err, ":")
        else:
            print(err)
            break
else:
    print("===========================================")
    print("✅Syntactic analysis completed successfully")
    print("===========================================")

        

#existence_var()

# if semantic_errors:
#     semantic_errors.sort(key=lambda e: e[0])
#     for error in semantic_errors:
#         print(error)

## красивая печать дерева 

def print_ast(node, prefix="", is_last=True):
    if node is None:
        return

    branch = "└─ " if is_last else "├─ "
    if node.value is not None:
        print(prefix + branch + f"{node.kind}: {node.value}, {node.line}")
    else:
        print(prefix + branch + f"{node.kind}")

    new_prefix = prefix + ("   " if is_last else "│  ")

    for i, child in enumerate(node.children):
        print_ast(child, new_prefix, i == len(node.children) - 1)



if not syntax_errors:
   

    semantic_analysis(ast_program)

    if not semantic_err:
        print("==========================================")
        print("✅Semantic analysis completed successfully")
        print("==========================================")
    else:
        print("❌ERRORS:")
        for err in semantic_err:
            print(err)

    # print("AST")
    # print_ast(ast_program)

