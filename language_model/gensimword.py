from gensim.models import KeyedVectors
import os
import pickle

def gensim_load(model, vecpath):
    if not os.path.isfile(vecpath):
        vec = KeyedVectors(vector_size = next(model.parameters()).shape[1])
        words = []
        for eachtoken in range(next(model.parameters()).shape[0]):
            words.append(eachtoken)
        vec.add_vectors(words, next(model.parameters()).tolist())
        print("== {} will be created ==".format(vecpath))

        worddic = {}
        for i, eachword in enumerate(words):
            if i % 5000 == 4999:
                print("== {} word vectors similarities have been calculated ==".format(i))
            worddic[eachword] = {k:v for k,v in vec.similar_by_word(eachword, topn = int(len(words)/1000))}
            selfposition = 0
            for k,v in worddic[eachword].items():
                if v > eachword:
                    break
                selfposition += 1
            worddic[eachword][eachword] = selfposition

        with open(vecpath, "wb") as fp:
            pickle.dump(worddic, fp)
    else:
        with open(vecpath, "rb") as fp:
            worddic = pickle.load(fp)

    return worddic

