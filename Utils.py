"""
Some useful helper functions.
"""
from decimal import Decimal
import re
import codecs
import sys

def corpusIterator(file):
    while True:
        line = file.readline()
        line = line.strip()
        if line: yield line
        else: break

def naiveWordSegChs(line):
    l = []
    t = ""
    for c in line:
        if u'\u4e00' <= c <= u'\u9fff':
            if t != "":
                l.append(t)
                t = ""
            l.append(str(c))
        else:
            t += c
    return l

def writeDictToFile(filename, d):
    with codecs.open(filename, mode='w', encoding='utf-8') as file:
        file.write(str(d))

def loadFromFile(filename, d):
    import ast
    with open(filename) as file:
        d = ast.literal_eval(file.read())

def unword(words):
    if not words: return ""

    s = words[0]
    for word in words[1:]:
        s += " " + word

    return s

def wordExtract(sentence, keepdelim=False, delimiters=' \',.:;?!\n-()[]"{}'):
    resList = []
    curWord = []
    for ch in sentence:
        if ch not in delimiters:
            curWord += ch
        else:
            if curWord:
                resList.append(''.join(curWord))
                curWord = []
            if ch == "'" or keepdelim:
                resList.append(ch)
    if curWord:
        resList.append(''.join(curWord))
    return resList

def toMatrix(lst1, lst2):
    l, m = len(lst2), len(lst1)
    matrix_ef = set()
    matrix_fe = set()
    for (fw_ind, aligned_to_ew) in enumerate(lst1):
        matrix_ef.add((fw_ind, aligned_to_ew))
    for (ew_ind, aligned_to_fw) in enumerate(lst2):
        matrix_fe.add((aligned_to_fw, ew_ind))
    return (matrix_ef, matrix_fe)

def neighborPoints(point):
    neighbors = [(-1, 0), (1, 0), (0, 1), (0, -1), (-1, -1), (1, 1), (1, -1), (-1, 1)]
    return [(point[0] + offset[0], point[1] + offset[1]) for offset in neighbors]
    
def printMessage(m):
    print(m, file=sys.stderr)

def tokenExt(sentence):
    return [int(tok) for tok in sentence.split()]

def printAlignMat(mat):
    zipmat = list(zip(*mat))
    m, n = max(zipmat[0]), max(zipmat[1])

    g = [[' ' for i in range(n + 1)] for j in range(m + 1)]
    for point in mat:
        g[point[0]][point[1]] = '*'

    for i, line in enumerate(g):
        print(str(i) + ':' + ''.join(line))