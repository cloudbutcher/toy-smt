from collections import defaultdict

class TreeStore:
    def __init__(self):
        self.element = defaultdict(TreeStore)
        self.count = 0
         
    def incr(self): 
        self.count += 1

    def c(self): 
        return self.count

    def dict(self):
        return self.element

class TrigramTreeStore:
    def __init__(self):
        self.base = defaultdict(TreeStore)

    def insert(self, u, v, w):
        # get TreeStore with w. In this tree store we have unigram count for w.
        uni_ts = self.base[u]
        uni_ts.incr()

        # get TreeStore with w, v. In this tree store we have bigram count for v, w
        bi_ts = uni_ts.dict()[v]
        bi_ts.incr()

        # get TreeStore with w, v, u. In this tree store we have trigram count for u, v, w
        tri_ts = bi_ts.dict()[w]
        tri_ts.incr()
        tri_ts.element = None

    def c(self, u):
        return self.base[u].c()

    def c2(self, u, v):
        return self.base[u].dict()[v].c()

    def c3(self, u, v, w):
        return self.base[u].dict()[v].dict()[w].c()

    def card(self):
        return len(self.base)

    def card2(self, u):
        return len(self.base[u].dict())

    def card3(self, u, v):
        return len(self.base[u].dict()[v].dict())