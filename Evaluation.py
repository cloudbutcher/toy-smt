import re
import codecs
import Utils
import ast

def evalAlign(src_name, tgt_name, alf_name, res_name):
    src = codecs.open(src_name, encoding='utf-8')
    tgt = codecs.open(tgt_name, encoding='utf-8')
    alf = codecs.open(alf_name, encoding='utf-8')
    
    res = codecs.open(res_name, mode='w', encoding='utf-8')

    src.seek(0)
    tgt.seek(0)
    alf.seek(0)

    for sl in src:
        tl = tgt.readline()
        al = alf.readline()

        sl = Utils.tokenExt(sl)
        tl = Utils.tokenExt(tl)
        alignment = ast.literal_eval(al)
        
        tl.insert(0, '__NULL__')
        alstr = ''
        for i, a_i in enumerate(alignment):
            alstr += '({0} {1})'.format(sl[i], tl[a_i])
        res.write(alstr + '\n')

    res.close()
    src.close()
    tgt.close()
    alf.close()

def evalalmat(enc, frc, almatfilename):
    with codecs.open(almatfilename, encoding='utf-8') as file:
        with codecs.open('evalalmat.txt', mode='w', encoding='utf-8') as writer:
            for line in file:
                es, fs = enc.readline().split(), frc.readline().split()
                es.insert(0, '__NULL__')
                fs.insert(0, '__NULL__')
                al = ast.literal_eval(line)
                for point in al:
                    writer.write(fs[point[0]] + ' ' + es[point[1]] + '\n')