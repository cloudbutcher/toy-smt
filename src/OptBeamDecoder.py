from collections import defaultdict
import PhraseBasedModel

class OptBeamDecoder(PhraseBasedModel):
    def __init__(self, ecorp, fcorp, lm, k):
        super().__init__(self, ecorp, fcorp, lm, k)

    def OptBeam():
        lambdaVec = [0 for i in range(N)]
        lbVec = [float('-infinity') for i in range(N)]