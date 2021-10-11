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

        #outs = outs[0].index_select(2, torch.LongTensor(list(worddic[orig_idx].keys())).to(device))

        max_ids = outs[0][0, i].topk(1).indices
        score = torch.nn.functional.softmax(outs[0][0,i], dim=0)
        #score = score[worddic[orig_idx][orig_idx]] / score[max_ids[0]]
        score = score[orig_idx] / score[max_ids[0]]

        tmplist.append(float(score))

    allscore = 0
    for eachscore in tmplist:
        allscore += eachscore

    return [tmplist, allscore/ (len(tmplist) ** 2)]


def roberta2test(text, tries = 100):
    rightprob = robertaeval(text)
    #print("{} : {} \n -> avg. with length-penalty {}".format(text, str(rightprob[0]), rightprob[1]))
    #print("- "*40)

    tmptextscores = {}
    finalscore = 0
    for i in range(tries):
        tmptext = perturb.perturb(text)
        if tmptext not in tmptextscores:
            wrongprob = robertaeval(tmptext)
            #if wrongprob[1] > rightprob[1]:
                #print("{} : {} \n -> avg. with length-penalty {}".format(tmptext, str(wrongprob[0]), wrongprob[1]))
            tmptextscores[tmptext] = wrongprob[1]
        finalscore += (rightprob[1] - tmptextscores[tmptext])

        print("-"*i,end="\r")
    #print("total sum of (orig. score - perturbed score)  : {}\t(higher is better)".format(finalscore))
    print(text)
    return finalscore

evalresult = [["RoBERTa"]]

with open("testtext.json") as fp:
    textlist = json.load(fp)

tmplist = []

for eachdata in textlist:
    tmp2list = [eachdata[0]]
    tmp3list = []
    for righttext in eachdata[1]:
        tmp3list.append([righttext, [roberta2test(righttext)]])
    tmp2list.append(tmp3list)
    tmp3list = []
    for wrongtext in eachdata[2]:
        tmp3list.append([wrongtext, [roberta2test(wrongtext)]])
    tmp2list.append(tmp3list)
    tmplist.append(tmp2list)
evalresult.append(tmplist)

with open("jsondata.js", "w") as fp:
    json.dump(evalresult, fp, ensure_ascii = False, indent = 2)
