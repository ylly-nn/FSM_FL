from lex.lex import *
##объявленные переменные
dec_var = {}

semantic_errors=[]

def add_dec_var(count: int, token: list, var_type: str):
    for info in dec_var.values():
        if info["token"] == token:
            token=ident_name_by_id(token[1])
            semantic_errors.append([lst_lines[count], ("Переменная: " + str(token) + " уже объявлена")])
            return

    dec_var[count] = {
        "token": token,
        "type": var_type,
    }
    

def update_type_by_count(count: int, new_type: str):
    if count not in dec_var:
        #raise Exception("Запись с таким count не найдена")
        return

    dec_var[count]["type"] = new_type



# update_type_by_count(4, "!")
# update_type_by_count(5, "%")

# print(dec_var)


used_var = {}

def add_used_var(count:int, token: list):
    used_var[count]={
        "token": token,
    }

def has_declared_token(token: list) -> int:
    for count in dec_var:
        dec_token=dec_var[count]["token"]
        if dec_token==token:
            return 0, count
    return -1,-1


## Исползование необъявленной переменной
def existence_var():
    # список уникальных использований: [{token, count}]
    for count in used_var:
        token=used_var[count]["token"]
        err, dec_count =  has_declared_token(token)
        if err==-1:
            token=ident_name_by_id(token[1])
            semantic_errors.append([lst_lines[count],("Использование необъявленной переменной: "+ str(token))])
        elif count<dec_count:
            token=ident_name_by_id(token[1])
            semantic_errors.append([lst_lines[count],("Переменая используется раньше объявления: "+ str(token))])


