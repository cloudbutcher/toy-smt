import Model
import PhraseBasedModel
import LanguageModel
import codecs
import Utils
import sys
import Evaluation

if __name__ == "__main__":    

    #-------------------------STARTING-------------------------------------

    reverse = False
    alignFileName = 'mlalign_e_f.txt'
    if len(sys.argv) > 1 and sys.argv[1] == '-r': 
        reverse = True
        alignFileName = 'mlalign_f_e.txt'

    fileEn = 'Corpus/100k.en.tok'
    fileFr = 'Corpus/100k.fr.tok'

    if reverse: fileEn, fileFr = fileFr, fileEn

    enc = codecs.open(fileEn, encoding="utf-8")
    frc = codecs.open(fileFr, encoding="utf-8")
    
    #-------------------------EVALUATION-----------------------------------

    #Evaluation.evalAlign(fileFr, fileEn, 'mlalign_e_f.txt', 'evalresult_e_f.txt')
    #Evaluation.evalAlign(fileEn, fileFr, 'mlalign_f_e.txt', 'evalresult_f_e.txt')
    #Evaluation.evalalmat(enc, frc, 'almat.txt')
    #sys.exit(0)

    #----------------------------------------------------------------------

    #------------------- IBM MODEL 1 & 2 TRAINING -------------------------

    #ibmm2 = Model.IBMModel2(enc, frc)
    #ibmm2.train()
    #ibmm2.align(alignFileName, False)

    #ibmm2.genAlignMatrix('mlalign_e_f.txt', 'mlalign_f_e.txt', 'almat.txt')
    #ibmm2.closeFiles()

    #----------------------------------------------------------------------
    
    #---------- LANGUAGE MODEL & PHRASE BASED MODEL TRAINING --------------

    lm = LanguageModel.TrigramLM(enc)
    lm.train(False)

    lexFile, phraseTableFile = 'lexicon_fr2en.txt', 'pht_fr2en.txt'
    if reverse: lexFile, phraseTableFile = 'lexicon_en2fr.txt', 'pht_en2fr.txt'

    pb = PhraseBasedModel.PhraseBasedModel(enc, frc, lm, 1)
    #pb.trainLexicon(lexFile, phraseTableFile)
    pb.loadLexicon(lexFile, phraseTableFile)
    
    with codecs.open('testTranslate.txt', encoding='utf-8') as fp:
        for line in fp:
            pb.translate(line)
    
    #----------------------------------------------------------------------