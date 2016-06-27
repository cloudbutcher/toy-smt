class NgramLanguageModel:
    """
    Mathematically, a language model consists of a finite set V (vocabulary)
    and a function p(x1, x2, ..., xn) such that p forms a probability distribution
    over all sentence in V^.
    So the input should be a sentence and the output should be a probability.
    And also we need a dict to store all the q terms.
    """
    def __init__(self, languageNameString):
        self.name = languageNameString

    def probability(self, sentence):
        raise NotImplementedError

    def train(self, corpus):
        raise NotImplementedError

import Utils
import TrigramTreeStore
import re
import codecs
from collections import defaultdict
from collections import Counter


class TrigramLM(NgramLanguageModel):
    def __init__(self, corpus):
        self.corpus = corpus
        self.d = 0.75            # SMOOTH PARAMETER
        self.ts = TrigramTreeStore.TrigramTreeStore()
        self.all_distinct_bigram_count = 0

    def train(self, save):
        Utils.printMessage("Training Trigram Model...")

        for line in self.corpus:
            words = Utils.wordExtract(line)
            words.insert(0, '__*__')
            words.insert(0, '__*__')
            words.append('__STOP__')
            words.append('__STOP__')
            for i in range(2, len(words)):
                u, v, w = words[i - 2], words[i - 1], words[i]
                self.ts.insert(u, v, w)
        
        for (k, bigram) in self.ts.base.items():
            self.all_distinct_bigram_count += len(bigram.dict())

        Utils.printMessage("Trigram Model training complete.")

        if save:
            Utils.printMessage("Dumping files...")

            # TODO: Add saving logic

            Utils.printMessage("Dump complete.")


    # Kneser-Ney Smoothing

    def probability(self, sentence):
        words = ["__*__", "__*__"]
        words.extend(Utils.wordExtract(sentence))
        words.append("__STOP__")
        
        res = 1.0

        for i in range(2, len(words)):
            u, v, w = words[i - 2], words[i - 1], words[i]

            if self.ts.c2(u, v) != 0:
                abs_discount = max(self.ts.c3(u, v, w) - self.d, 0) / self.ts.c2(u, v)
                norm_discount = self.d / self.ts.c2(u, v) * self.ts.card3(u, v)
                res *= abs_discount + norm_discount * self.probBigramKN(v, w)
            else:
                res *= self.probBigramKN(u, v)

        return res

    def probBigramKN(self, v, w):
        if self.ts.c(v) == 0: 
            return 1 / self.all_distinct_bigram_count
        abs_discount = max(self.ts.c2(v, w) - self.d, 0) / self.ts.c(v)
        norm_discount = self.d / self.ts.c(v) * self.ts.card2(v)
        return abs_discount + norm_discount * self.ts.card2(v) / self.all_distinct_bigram_count