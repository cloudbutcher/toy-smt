from collections import defaultdict
import codecs
import ast
import Utils

class Model:
    def __init__(self, corpus1, corpus2):
        self.q = defaultdict(lambda: defaultdict(lambda: 0.00001))
        self.t = defaultdict(lambda: defaultdict(lambda: 0.00001))
        self.numIter = 10      # How many iterative process should we go through

        self.linenum = 0

        self.ef = defaultdict(float)
        self.e = defaultdict(float)
        self.jilm = defaultdict(lambda: defaultdict(float))
        self.ilm = defaultdict(lambda: defaultdict(float))

        self.corpus1 = corpus1
        self.corpus2 = corpus2

    def rewindPointer(self):
        self.corpus1.seek(0)
        self.corpus2.seek(0)
        self.linenum = 0

    def iterInit(self):
        self.rewindPointer()
        self.linenum = 0
        self.ef.clear()
        self.e.clear()
        self.jilm.clear()
        self.ilm.clear()

    def pairs(self):
        for line1 in self.corpus1:
            line2 = self.corpus2.readline()
            local = Utils.tokenExt(line1)
            foreign = Utils.tokenExt(line2)
            self.linenum += 1
            if self.linenum % 10000 == 0: Utils.printMessage(self.linenum)
            local.insert(0, -1)
            yield (local, foreign)

    def closeFiles(self):
        self.corpus1.close()
        self.corpus2.close()

    def loadFromFile(self, fname, dname):
        d = self.t
        if dname == 'q': d = self.q

        with codecs.open(fname, encoding='utf-8') as file:
            for line in file:
                parts = line.partition('|||')
                d[parts[0]] = ast.literal_eval(parts[2])

    def writeDict(self, d, fname):
        with codecs.open(fname, mode='w', encoding='utf-8') as file:
            for (k, v) in d.items():
                file.write(str(k) + '|||' + str(dict(v)) + '\n')
                

class IBMModel1(Model):
    def __init__(self, corpus1, corpus2):
        super().__init__(corpus1, corpus2)
        self.t_fi = defaultdict(int)

    def train(self):
        Utils.printMessage("Training IBM Model 1...")

        evocab = set()
        for (e, f) in self.pairs():
            for ew in e:
                evocab.add(ew)
        self.t = defaultdict(lambda: defaultdict(lambda: 1 / len(evocab)))

        for s in range(self.numIter):
            self.iterInit()
            Utils.printMessage("Start iteration {0}...".format(s + 1))
            for (e, f) in self.pairs():
                for f_i in f:
                    tmp = 0
                    for e_j in e:
                        tmp += self.t[f_i][e_j]
                    self.t_fi[f_i] = tmp

                for f_i in f:
                    for e_j in e:
                        delta = self.t[f_i][e_j] / self.t_fi[f_i]
                        self.ef[e_j, f_i] += delta
                        self.e[e_j] += delta

            for ((e, f), v) in self.ef.items():
                self.t[f][e] = v / self.e[e]
        Utils.printMessage("IBM Model 1 training complete.")


class IBMModel2(IBMModel1):
    def __init__(self, corpus1, corpus2):
        return super().__init__(corpus1, corpus2)

    def train(self):

        ibmm1 = IBMModel1(self.corpus1, self.corpus2)
        ibmm1.train()
        self.t = ibmm1.t

        Utils.printMessage("Training IBM Model 2...")
        for s in range(self.numIter):
            self.iterInit()
            Utils.printMessage("Start iteration {0}...".format(s + 1))
            for (e, f) in self.pairs():
                l, m = len(e), len(f)
                for (i, f_i) in enumerate(f):
                    tmp = 0
                    for (j, e_j) in enumerate(e):
                        if self.q[j, i][l, m] == 0: self.q[j, i][l, m] = 1 / (l + 1)
                        tmp += self.q[j, i][l, m] * self.t[f_i][e_j]
                    self.t_fi[f_i] = tmp

                for (i, f_i) in enumerate(f):
                    for (j, e_j) in enumerate(e):
                        delta = self.q[j, i][l, m] * self.t[f_i][e_j] / self.t_fi[f_i]
                        self.ef[e_j, f_i] += delta
                        self.e[e_j] += delta
                        self.jilm[j, i][l, m] += delta
                        self.ilm[i][l, m] += delta

            for ((e, f), v) in self.ef.items():
                self.t[f][e] = v / self.e[e]

            for ((j, i), subd) in self.jilm.items():
                for ((l, m), v) in subd.items():
                    self.q[j, i][l, m] = v / self.ilm[i][l, m]

        Utils.printMessage("IBM Model 2 training complete.")

    def align(self, filename, loadFromFile):
        super().rewindPointer()

        Utils.printMessage("Calculating most likely alignment...")
        with codecs.open(filename, mode="w", encoding='utf-8') as fp:
            for (e, f) in self.pairs():
                l, m = len(e), len(f)
                alignment = []
                for (i, f_i) in enumerate(f):
                    tmpmax, argmax = -1000, 0
                    for (j, e_j) in enumerate(e):
                        term = self.q[j, i][l, m] * self.t[f_i][e_j]
                        if term > tmpmax:
                            tmpmax = term
                            argmax = j
                    alignment.append(argmax)
                fp.write(str(alignment) + '\n')

    def genAlignMatrix(self, effile, fefile, matfile):
        efa = codecs.open(effile, encoding='utf-8')
        fea = codecs.open(fefile, encoding='utf-8')
        almat = codecs.open(matfile, "w", encoding='utf-8')

        for line1 in efa:
            line2 = fea.readline()

            lst1 = ast.literal_eval(line1)
            lst2 = ast.literal_eval(line2)
            lst1.insert(0, 0)
            lst2.insert(0, 0)

            m_ef, m_fe = Utils.toMatrix(lst1, lst2)
            alignment = m_ef.intersection(m_fe)
            newPoints = set()
            before_al_size = len(alignment)

            while True:
                for point in alignment:
                    for neighbor in Utils.neighborPoints(point):
                        if neighbor not in alignment and \
                            neighbor in m_ef.symmetric_difference(m_fe):
                            newPoints.add(neighbor)
                alignment.update(newPoints)
                if len(alignment) == before_al_size: break
                before_al_size = len(alignment)
                newPoints.clear()

            alist = list(alignment)
            alist.sort(key=(lambda t: t[0]))
            almat.write(str(alist[1:]) + '\n')

        efa.close()
        fea.close()
        almat.close()