import Utils
import math
import ast
from collections import Counter
from collections import defaultdict
import codecs

class PhraseBasedModel:
    def __init__(self, ecorp, fcorp, lm, k):
        self.lexicon = dict()
        self.lookuptab = defaultdict(lambda: [])
        self.fcorp = fcorp
        self.ecorp = ecorp
        self.beamWidth = 100
        self.ita = -0.1
        self.k_best = k
        self.d = 4
        self.lm = lm
        self.maximum_phrase_length = 5

    def trainLexicon(self, lexf, phtf):
        L = set()
        efdict = defaultdict(int)
        edict = Counter()

        self.fcorp.seek(0)
        self.ecorp.seek(0)

        alignMatFile = open("almat.txt")

        Utils.printMessage("Training lexicon...")

        for fline in self.fcorp:
            eline = self.ecorp.readline()
            align = alignMatFile.readline()

            f, e = fline.split(), eline.split()
            f.insert(0, '')
            e.insert(0, '')
            m, l = len(f), len(e)

            mat = ast.literal_eval(align)
            matlen = len(mat)

            #Utils.printAlignMat(mat)

            for i in range(matlen):
                for j in range(i, matlen):
                    zipmat = list(zip(*mat[i : j + 1]))
                    s, t = min(zipmat[0]), max(zipmat[0])
                    sprime, tprime = min(zipmat[1]), max(zipmat[1])
                    if (t - s + 1 >= self.maximum_phrase_length) or (tprime - sprime + 1) >= self.maximum_phrase_length:
                        break
                    if self.consistent(mat, (s, t), (sprime, tprime)):
                        fphrase, ephrase = Utils.unword(f[s:t + 1]), Utils.unword(e[sprime:tprime + 1])
                        efdict[ephrase, fphrase] += 1
                        edict[ephrase] += 1

        for ((e, f), v) in efdict.items():
            self.lookuptab[f].append(e)
            self.lexicon[f, e] = math.log((v - 0.7) / edict[e])

        Utils.printMessage("Training complete. Dumping files...")
        with codecs.open(lexf, mode="w", encoding="utf-8") as file:
            for (k, v) in self.lexicon.items():
                file.write(str(k) + '|||' + str(v) + '\n')
        with codecs.open(phtf, mode="w", encoding="utf-8") as file2:
            for (k, v) in self.lookuptab.items():
                file2.write(str(k) + '|||' + str(v) + '\n')
    
    def consistent(self, A, ind1, ind2):
        s, t = ind1
        sp, tp = ind2

        valset = set()
        #valset2 = set()
        for v in A:
            if s <= v[0] <= t:
                if not sp <= v[1] <= tp: return False
                valset.add(v[0])
            if sp <= v[1] <= tp:
                if not s <= v[0] <= t: return False
                #valset2.add(v[1])

        if len(valset) != t - s + 1: 
            return False
        #if len(valset2) != tp - sp + 1:
        #    return False

        return True

    def loadLexicon(self, lexf, phtf):
        Utils.printMessage("Loading lexicons...")
        with codecs.open(lexf, encoding="utf-8") as file:
            for line in file:
                parts = line.partition('|||')
                self.lexicon[ast.literal_eval(parts[0])] = ast.literal_eval(parts[2])

        with codecs.open(phtf, encoding="utf-8") as file2:
            for line in file2:
                parts = line.partition('|||')
                self.lookuptab[parts[0]] = ast.literal_eval(parts[2])
        Utils.printMessage("Loaded.")

    def decode(self, sentence):
        words = Utils.wordExtract(sentence.strip())

        OOV = []
        for word in words:
            if word not in self.lookuptab:
                OOV.append(word)
        if OOV:
            Utils.printMessage('Out of vocabulary:' + str(OOV))

        n = len(words)
        self.Q = [dict() for i in range(n + 1)]
        self.bp = dict()
        self.Q[0]['__*__', '__*__', 0, 0] = 0
        self.bp['__*__', '__*__', 0, 0, 0] = None

        for i in range(n):
            self.Q[i] = self.beam(self.Q[i])
            for _q, alpha in self.Q[i].items():
                q = _q + (alpha, )

                #qprimes = [(self.nextState(p, q, Utils.unword(words[p[0]:p[1] + 1]), n), p) for p in self.ph(q, words)]
                #qprimes = sorted(qprimes, reverse=True, key=(lambda t: t[0][-1]))[:10]
                #for (qi, p) in qprimes: self.Add(self.Q[self.bitlen(qi)], qi, q, p)

                for p in self.ph(q, words):
                    qprime = self.nextState(p, q, Utils.unword(words[p[0]:p[1] + 1]), n)
                    self.Add(self.Q[self.bitlen(qprime)], qprime, q, p)

        for Q in reversed(self.Q):
            if len(Q) > 0:
                Q = sorted(Q.items(), reverse=True, key=(lambda t: t[1]))[:self.k_best]
                for i in range(len(Q)):
                    qterminal = Q[i][0] + (Q[i][1], )
                    resstr = []
                    pair = self.bp[qterminal]
                    while pair:
                        resstr.append(pair[1][-1])
                        pair = self.bp.get(pair[0], None)

                    resstr.reverse()
                    return Utils.unword(resstr)
  
    def beam(self, Q):
        newdict = dict()
        lst = sorted(Q.items(), reverse=True, key=(lambda t: t[1]))[:self.beamWidth]
        for k in lst:
            newdict[k[0]] = k[1]
        return newdict

    def ph(self, q, words):
        e1, e2, b, r, alpha = q
        l = len(words)
        res = []
        bitstr = []
        for i in range(l):
            if b & 1 == 1: bitstr.append(True)
            else: bitstr.append(False)
            b >>= 1
        bitstr.reverse()

        for s in range(max(0, r + 1 - self.d), min(l, r + 2 + self.d)):
            if bitstr[s]: continue
            for t in range(s, l):
                if bitstr[t]: break
                word = Utils.unword(words[s:t + 1])
                res.extend([(s, t, k) for k in self.lookuptab.setdefault(word, [])])
        return res

    def nextState(self, p, q, fphrase, l):
        s, t, e = p
        e1, e2, b, r, alpha = q

        es = [e1, e2]
        es.extend(e.split())

        e1p, e2p = es[-2], es[-1]
        score = alpha + self.lexicon[fphrase, e] + self.ita * abs(r - s + 1)
        score += math.log(self.lm.probability(e))
        return (e1p, e2p, b | self.bitmask(l, s, t), t, score)

    def Add(self, Q, qprime, q, p):
        if qprime[:-1] in Q and Q[qprime[:-1]] > qprime[-1]:
            return
        Q[qprime[:-1]] = qprime[-1]
        self.bp[qprime] = (q, p)

    def bitlen(self, q):
        l, n = 0, q[2]
        while n > 0:
            if n & 1 == 1: l += 1
            n >>= 1
        return l

    def bitmask(self, l, s, t):
        bitstr = ""
        for i in range(l):
            if s <= i <= t: bitstr += '1'
            else: bitstr += '0'

        return int(bitstr, 2)

    def translate(self, sentence):
        Utils.printMessage('Decoding...')
        delim = ',.:;?!\n-()[]"{}'
        segments = Utils.wordExtract(sentence.lower(), True, delim)
        res = []
        for segment in segments:
            if segment in delim:
                res.append(segment)
            else:
                res.append(self.decode(segment))
        print(u'{}'.format(Utils.unword(res).capitalize()))