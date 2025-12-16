def keywords_let(token):
    keywords={
        "begin":  3,
        "end":    4,
        "if":     5,
        "else":   6, 
        "for":    7,
        "to":     8,
        "step":   9,
        "next":   10,
        "while":  11,
        "readln": 12, 
        "writeln":13, 
        "true":   14,
        "false":  15,
    }
    
    if token in keywords:
        return 0,keywords[token]
    else:
        return -1
    
    
def keywords_symbols(token):
    keywords={
        "%": 0,
        "!": 1,
        "$": 2,
    }
    if token in keywords:
        return 0,keywords[token]
    else:
        return -1


def separators_let(token):
    separators={
        "NE":   0,
        "EQ":   1,
        "LT":   2,
        "LE":   3,
        "GT":   4,
        "GE":   5,
        "plus": 6,
        "min":  7,
        "or":   8,
        "mult": 9, 
        "div":  10, 
        "and":  11,
    }
    if token in separators:
        return 1, separators[token]
    else:
        return -1

def separators_symbols(token):
    separators={
        "~":  12,
        "{":  13,
        "}":  14,
        ";":  15,
        ":":  16,
        ",":  17,
        ":=": 18,
        "(":  19,
        ")":  20,
        "/":  21, 
        "*":  22,
    }
    if token in separators:
        return 1, separators[token]
    else:
        return -1


