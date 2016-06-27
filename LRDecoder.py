from collections import namedtuple
from collections import Counter
from collections import defaultdict
import Utils
import queue

Vertex = namedtuple('State', ['w1', 'w2', 'n', 'l', 'm', 'r', 'b'])
Edge = namedtuple('Transition', ['s', 't', 'e'])

class LRDecoder:
    def __init__(self, pb, words):
        self.d = 4
        self.K = 10
        self.N = len(words)
        self.pb = pb
        self.words = words

    def optimize(self, C, u):
        u = [0 for i in range(self.N)]
        uprev = u
        while improving(uprev, u):
            ystar = argmax(C, u)
            if check(ystar): return ystar
            else: 
                uprev = u.copy()
                for i in range(len(u)): 
                    u[i] = u[i] - alpha * (bitstring(ystar)[i] - 1)
        count = Counter()
        for k in range(self.K):
            ystar = argmaxDP()
            if check(ystar): return ystar
            else:
                for i in range(len(u)): 
                    u[i] = u[i] - alpha * (bitstring(ystar)[i] - 1)
                    

    def argmax(C, uvec):
        predecessor = dict()
        path = dict()
        dp = defaultdict(lambda: -1000)
        q = Vertex('__*__', '__*__', 0, 0, 0, 0)
        predecessor[q] = None
        dp[q] = 0
        vertexq = queue.Queue()
        vset = set()
        vertexq.put(q)

        while not vertexq.empty():
            q = vertexq.get()
            for p in allTransitions(C, q):
                adjv = nextState(q, p)
                if adjv not in vset:
                    vertexq.put(adjv)
                    vset.add(adjv)
                _score = self.score(q, p) + dp[q] + sum(uvec[p.s : p.t + 1])
                if _score > dp[adjv]: 
                    dp[adjv] = _score
                    predecessor[adjv] = q
                    path[adjv] = p

        v = Vertex() # End state
        bestPath = []
        while v:
            bestPath.append(path[v])
            v = predecessor(v)
        bestPath.reverse()

        return bestPath

    def nextState(q, p):
        if len(p.e) >= 2: w1p, w2p = p.e[-2], p.e[-1]
        else: w1p, w2p = q.w2, e[0]

        np = q.n + p.t - p.s + 1

        if p.s == q.m + 1: lp, mp = q.l, p.t
        elif p.t == q.l - 1: lp, mp = p.s, q.m
        else: lp, mp = p.s, p.t

        rp = p.t

        return Vertex(w1p, w2p, np, lp, mp, rp)

    def allTransitions(self, C, q):
        if q.n == self.N: return Edge(self.N, self.N + 1, '__STOP__')
        res = []
        for s in range(max(0, r + 1 - self.d), min(l, r + 2 + self.d)):
            if q.l <= s <= q.m: continue
            for t in range(s, self.N):
                if q.l <= t <= q.m: break
                word = Utils.unword(words[s:t + 1])
                res.extend([(s, t, k) for k in self.pb.lookuptab.setdefault(word, [])])

        return res

    def score(self, q, p):
        fphrase = self.words[p.s:p.t + 1]
        _score = self.pb.lexicon[fphrase, e] + self.pb.ita * abs(q.r - p.s + 1)
        _score += math.log(self.pb.lm.probability(p.e))
        return _score

    def bitstring(derivation):
        res = [0 for i in range(self.N)]
        for p in derivation:
            for i in range(p.s, p.t + 1):
                res[i] = 1
        return res

    def check(self, derivation):
        for i in bitstring(derivation):
            if i != 1: return False
        return True

    def improving(uprev, u):
        return sum([up_i - u_i for up_i, u_i in zip(uprev, u)]) >= 0.002