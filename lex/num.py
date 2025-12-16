import re
import struct

number_table = {}   # {число: номер}
"""Числа хрянятся в таблице в двоичном представлении
вещественные числа хранятся согдасно стандарту IEEE 754"""


##Если числа нет, добавляется в таблицу. Возврат номер в таблице
def number_add(value: str):
    if value not in number_table:
        number_table[value] = {
            "id": len(number_table)
        }
    return number_table[value]["id"]


## Бинарные
def binary(token):
    if re.fullmatch(r'[01]+[Bb]', token):

        token=re.sub(r"B", "", token)
        token=re.sub(r"b", "", token)

        token=int(token, 2)
        token=bin(token)

        res=number_add(token)
        res=[3, res]

        return res
    else:
        return -1

## Восьмиричные
def octal (token):
    if re.fullmatch(r'[01234567]+[Oo]',token):

        token=re.sub(r"O", "", token)
        token=re.sub(r"o", "", token)

        token=int(token,8)
        token=bin(token)

        res=number_add(token)
        res=[3,res]

        return res
    else:
        return -1  

## Десятичные
def decimal(token):
    if re.fullmatch(r'[0123456789]+[Dd]?',token):
        
        token=re.sub(r"D", "", token)
        token=re.sub(r"d", "", token)

        token=int(token, 10)
        token=bin(token)

        res=number_add(token)
        res=[3,res]

        return res
    else:
        return -1

## Шестнадцатиричные
def hex(token):
    if re.fullmatch(r'[0123456789abcdefABSDEF]+[Hh]',token):
        
        token=re.sub(r"H", "", token)
        token=re.sub(r"h", "", token)

        token=int(token, 16)
        token=bin(token)
        
        res=number_add(token)
        res=[3,res]

        return res
    else:
        return -1
    
## Начинается с точки    
def e_from_dot(token):
    if re.fullmatch(r'[/.]+[0-9]+([E|e]+([+|-]?)+[0-9])?',token):
        token=float(token)
        token = struct.unpack(">Q", struct.pack(">d", token))[0]
        token = format(token, "064b")
        res=number_add(token)

        res=[3,res]
        
        return res
    else:
        return -1

## Точка внутри
def e_with_dot(token):
    if re.fullmatch(r'[1-9]+[/.]+[1-9]+([E|e]+([+|-]?)+[0-9])?', token):
        token=float(token)
        token = struct.unpack(">Q", struct.pack(">d", token))[0]
        token = format(token, "064b")
        res=number_add(token)
        res=[3,res]

        return res
    else:
        return -1
        

## Вообще без точки
def e_not_dot(token):
    if re.fullmatch(r'[1-9]+[E|e]+([+|-]?)+[1-9]', token):
        token=float(token)
        token = struct.unpack(">Q", struct.pack(">d", token))[0]
        token = format(token, "064b")
        res=number_add(token)
        res=[3,res]
        
        return res
    else:
        return -1
        