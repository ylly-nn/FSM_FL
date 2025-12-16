import os
import re
from .dicts import *
from .num import *

ident_table = {}  # {имя: номер}


## Добавляется идентификатор если его нет, возвращается номер
def identifier_add(name: str):
    
    if name not in ident_table:
        ident_table[name] = len(ident_table) + 0  # нумерация с 0
    return ident_table[name]



## Для элементов нацинающихся с буквы
def let(token):
    

    if (keywords_let(token))!=-1:
        table,token=keywords_let(token)
        res=[table, token]
        return res


    elif (separators_let(token))!=-1:
        table,token=separators_let(token)
        res=[table, token]
        return res

    elif re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', token):
        res=identifier_add(token)
        res=[2, res]
        return res

    else:
        res=[-1, "❌ERR index: " + str(token)]
        return res

## Для элементов начинающихся с символа
def symbols(token):
    if (keywords_symbols(token))!=-1:
        table,token=keywords_symbols(token)
        res=[table,token]
        return res
    
    elif (separators_symbols(token))!=-1:
        table,token = separators_symbols(token)
        res=[table,token]
        return res
    
    else:
        res=[-1, "❌ERR symbol: " + str(token)]
        return res

## Удаление комменариев
def _replace_block_comment(match: re.Match) -> str:
    """
    Заменяем /* ... */ на такое же количество '\n', чтобы
    сохранить нумерацию строк 1-в-1.
    """
    comment = match.group(0)
    newlines = comment.count('\n')
    # Если комментарий был однострочным, можно вернуть '' или ' '.
    # Но для единообразия оставим одну пустую строку при 0 переносах:
    if newlines == 0:
        return ''  # строка не "поднимется", потому что splitlines() всё равно делит по '\n'
    return '\n' * newlines

"""=============================main==========================================="""



TOKEN_REGEX = r'(:=|[%!$~{}\[\];:,\(\)]|[^ \t\n%!$~{}\[\];:,\(\)]+)'
lst_tokens=[] ##сисок токенов для дальнейшего анализа
lst_err=[] ##cписок ошибок
tokens_list_print = [] ##для печати список токено

BASE_DIR = os.path.dirname(__file__)
CODE_PATH = os.path.join(BASE_DIR, "code.txt")
#Чтение файла
with open(CODE_PATH, "r", encoding="utf-8") as f:
    code_with_comments = f.read()

#Убираются комментарии
code = re.sub(r'/\*.*?\*/', _replace_block_comment, code_with_comments, flags=re.S)

#Деление по строкам
lines = code.splitlines()

stop=False

for count, line in enumerate(lines, start=1):
        if stop:
            break
        line = line.strip()

        if not line:        
            continue
        
        #Разбиение
        tokens = re.findall(TOKEN_REGEX, line)
        if not tokens:      
            continue
        new_tokens=list(tokens)

        # Проход по токенам
        for i, token in enumerate(tokens):

            ## END
            if re.match(r'}', token):
                new_tokens[i]=[1,14]
                stop=True
                break
            
        

            ## Начинается с буквы
            if re.match(r'[A-Za-z]', token):
                    new_tokens[i] = let(token) 
            
                
             
            ## Начинается с символа
            if not re.match(r'[A-Za-z0-9]|}|[/.]', token):
                new_tokens[i]=symbols(token)
            


                

            ## Начинается c 0,1
            if re.match(r'[0-9]', token):
                if e_with_dot(token)!=-1:
                    new_tokens[i]=e_with_dot(token)
                elif e_not_dot(token)!=-1:
                    new_tokens[i]=e_not_dot(token)
                elif binary(token)!=-1:
                    new_tokens[i]=binary(token)
                elif octal(token)!=-1:
                    new_tokens[i]=octal(token)
                elif hex(token)!=-1:
                    new_tokens[i]=hex(token)
                elif decimal(token)!=-1:
                    new_tokens[i]=decimal(token)
                else:
                    new_tokens[i]=[-1, "❌ERR number: "+ str(token)];
                

            ## Начинается с 2-7
            if re.match(r'[2-7]',token):
                
                if e_with_dot(token)!=-1:
                    new_tokens[i]=e_with_dot(token)
                elif e_not_dot(token)!=-1:
                    new_tokens[i]=e_not_dot(token)
                elif octal(token)!=-1:
                    new_tokens[i]=octal(token)
                elif hex(token)!=-1:
                    new_tokens[i]=hex(token)
                elif decimal(token)!=-1:
                    new_tokens[i]=decimal(token)
                else:
                    new_tokens[i]=[-1,"❌ERR number: "+ str(token)];

        
            ## Начинается 8,9
            if re.match(r'[8|9]',token):
                if e_with_dot(token)!=-1:
                    new_tokens[i]=e_with_dot(token)
                elif e_not_dot(token)!=-1:
                    new_tokens[i]=e_not_dot(token)
                elif hex(token)!=-1:
                    new_tokens[i]=hex(token)
                elif decimal(token)!=-1:
                    new_tokens[i]=decimal(token)
                else: 
                    new_tokens[i]=[-1,"❌ERR number: "+ str(token)];


            ## Начинается с точки
            if re.match(r'[/.]',token):
                if e_from_dot(token)!=-1:
                    new_tokens[i]=e_from_dot(token)
                else: 
                    new_tokens[i]=[-1,"❌ERR number: "+ str(token)];
                

        ## Формирование списков для вывода
        tokens_list_print.append(count)
        tokens_list_print.append(new_tokens)

        ## Фомирование списков для синтаксического анализа
        for token in new_tokens:
            if token[0]!=-1:
                lst_tokens.append(token)
            else:
                lst_err.append(token)


if lst_tokens[len(lst_tokens)-1]!=[1, 14]:
    lst_err.append([-1, "❌ERR: the end is not found"])

        


'''=====================вывод=кодов=токенов========'''
string = ""

for i in range(0, len(tokens_list_print), 2):
    index = tokens_list_print[i]
    values = tokens_list_print[i+1]   # список вида ['{0,0}', '{0,1}', ...]

    # --- добавляем номер ---
    if index < 10:
        string += f"{index}   : "
    elif index < 100:
        string += f"{index}  : "
    else:
        string += f"{index} : "

    # --- добавляем значения без квадратных скобок ---
    for token in values:
        string += str(token)+" "  # сам тип уже в нужном формате {x,y}
        
    string += "\n"

# вывод или запись в файл
print("===========Лексический=анализ==========")
print()
if lst_tokens[len(lst_tokens)-1]==[1, 14]:
    string+=" end!"
print(string)

print("=======================================")
print
if not lst_err:
    print("✅Lexical analysis completed successfully")
else:
    print("Lexical analysis completed with errors:")
    print(lst_err)
print
print("=======================================")
    



'''=================вывод=таблиц================'''
# ===== IDENT TABLE =====
with open("idents.txt", "w", encoding="utf-8") as f:
    f.write("IDENT TABLE(2):\n")
    f.write("ID\tIDENT\n")
    f.write("-----------------\n")

    ident_sorted = sorted(ident_table.items(), key=lambda x: x[1])

    for ident, idx in ident_sorted:
        f.write(f"{idx}\t{ident}\n")


# ===== NUMBER TABLE =====
with open("numbers.txt", "w", encoding="utf-8") as f:
    f.write("NUMBER TABLE(3):\n")
    f.write("ID\tNUMBER\n")
    f.write("-----------------\n")

    num_sorted = sorted(number_table.items(), key=lambda x: x[1]["id"])

    for raw, info in num_sorted:
        f.write(f"{info['id']}\t{raw}\n")
