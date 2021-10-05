from transformers import T5Tokenizer, RobertaForMaskedLM
import torch
import numpy as np
import json
import perturb
import copy
from gensim.models import KeyedVectors
import os
import pickle

device = "cuda:0" if torch.cuda.is_available() else "cpu"

tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-roberta-base")
tokenizer.do_lower_case = True

model = RobertaForMaskedLM.from_pretrained("rinna/japanese-roberta-base")
model = model.to(device)
print("== model loaded ==")

vecpath = "./vecsim_data.pickle"
if not os.path.isfile(vecpath):
    vec = KeyedVectors(vector_size = next(model.parameters()).shape[1])
    words = []
    for eachtoken in range(next(model.parameters()).shape[0]):
        words.append(eachtoken)
    vec.add_vectors(words, next(model.parameters()).tolist())
    print("== word vectors loaded ==")

    worddic = {}
    for i, eachword in enumerate(words):
        if i % 5000 == 4999:
            print("== {} word vectors similarity calculated ==".format(i))
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

with open("result.json") as fp:
    rightlist = json.load(fp)

with open("result.json.origin") as fp:
    wronglist = json.load(fp)

def robertaeval(orig_txt):
    tmplist = []
    txttmp = tokenizer.tokenize("[CLS]" + orig_txt)
    for i in range(1, len(txttmp)):
        txt = copy.deepcopy(txttmp)

        orig_idx = tokenizer.convert_tokens_to_ids([txt[i]])[0]

        txt[i] = tokenizer.mask_token
        txt_ids = tokenizer.convert_tokens_to_ids(txt)
        txt_tensor = torch.LongTensor([txt_ids]).to(device)

        posi_ids = list(range(0, txt_tensor.size(1)))
        posi_id_tensor = torch.LongTensor([posi_ids]).to(device)

        with torch.no_grad():
            outs = model(input_ids = txt_tensor, position_ids = posi_id_tensor)

        outs = outs[0].index_select(2, torch.LongTensor(list(worddic[orig_idx].keys())).to(device))

        max_ids = outs[0, i].topk(1).indices
        score = torch.nn.functional.softmax(outs[0,i], dim=0)
        score = score[worddic[orig_idx][orig_idx]] / score[max_ids[0]]

        tmplist.append(float(score))

    allscore = 0
    for eachscore in tmplist:
        allscore += eachscore

    return [tmplist, allscore/ (len(tmplist) ** 2)]


def roberta2test(text, tries = 100):
    rightprob = robertaeval(text)
    print("{} : {} \n -> avg. with length-penalty {}".format(text, str(rightprob[0]), rightprob[1]))
    print("*"*80)

    lowernum = 0
    for i in range(tries):
        tmptext = perturb.perturb(text)
        wrongprob = robertaeval(tmptext)
        if wrongprob[1] > rightprob[1]:
            print("{} : {} \n -> avg. with length-penalty {}".format(tmptext, str(wrongprob[0]), wrongprob[1]))
            lowernum += 1

    print("*"*80)
    print("# of successful perturbation : {}\t(lower is better)".format(lowernum))


for i in range(len(rightlist)):
    roberta2test(rightlist[i]["sent"])
    print("-"*80)
    roberta2test(wronglist[i]["sent"])
    print("-"*80)
    print("-"*80)
    print("-"*80)
