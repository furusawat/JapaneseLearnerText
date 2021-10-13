from transformers import T5Tokenizer, RobertaForMaskedLM
from transformers import AutoModelForCausalLM
import torch
import numpy as np
import json
import perturb
import copy
from gensim.models import KeyedVectors
import os
import pickle

device = "cuda:0" if torch.cuda.is_available() else "cpu"

roberta_tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-roberta-base")
roberta_tokenizer.do_lower_case = True

roberta_model = RobertaForMaskedLM.from_pretrained("rinna/japanese-roberta-base")
roberta_model = roberta_model.to(device)

gpt2_tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-gpt2-medium")
gpt2_tokenizer.do_lower_case = True

gpt2_model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt2-medium")
gpt2_model = gpt2_model.to(device)

print("== models are loaded ==")

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

roberta_worddic = gensim_load(roberta_model, "./roberta_vecsim_data.pickle")
#gpt2_worddic = gensim_load(gpt2_model, "./gpt2_vecsim_data.pickle")

def robertaeval(orig_txt, veclimit = False):
    tmplist = []
    txttmp = roberta_tokenizer.tokenize("[CLS]" + orig_txt)
    for i in range(1, len(txttmp)):
        txt = copy.deepcopy(txttmp)

        orig_idx = roberta_tokenizer.convert_tokens_to_ids([txt[i]])[0]

        txt[i] = roberta_tokenizer.mask_token
        txt_ids = roberta_tokenizer.convert_tokens_to_ids(txt)
        txt_tensor = torch.LongTensor([txt_ids]).to(device)

        posi_ids = list(range(0, txt_tensor.size(1)))
        posi_id_tensor = torch.LongTensor([posi_ids]).to(device)

        with torch.no_grad():
            outs = roberta_model(input_ids = txt_tensor, position_ids = posi_id_tensor)

        if veclimit:
            outs = outs[0].index_select(2, torch.LongTensor(list(roberta_worddic[orig_idx].keys())).to(device))
            max_ids = outs[0, i].topk(1).indices
            score = torch.nn.functional.softmax(outs[0,i], dim=0)
            score = score[roberta_worddic[orig_idx][orig_idx]] / score[max_ids[0]]
        else:
            max_ids = outs[0][0, i].topk(1).indices
            score = torch.nn.functional.softmax(outs[0][0,i], dim=0)
            score = score[orig_idx] / score[max_ids[0]]

        tmplist.append(float(score))

    allscore = 0
    for eachscore in tmplist:
        allscore += eachscore

    return [tmplist, allscore/ (len(tmplist) ** 2)]


def roberta2test(text, tries = 100, veclimit = False):
    rightprob = robertaeval(text, veclimit)

    tmptextscores = {}
    finalscore = 0
    for i in range(tries):
        tmptext = perturb.perturb(text)
        if tmptext not in tmptextscores:
            wrongprob = robertaeval(tmptext, veclimit)
            tmptextscores[tmptext] = wrongprob[1]
        finalscore += (rightprob[1] - tmptextscores[tmptext])

        print("-"*i,end="\r")
    print(text)
    return finalscore

def gpt2test(text, tries = 100):
    tokens = gpt2_tokenizer.encode(text, add_special_tokens=False, return_tensors="pt").to(device)
    loss = gpt2_model(tokens, labels = tokens)[0]
    rightprob = np.exp(loss.cpu().detach().numpy())

    tmptextscores = {}
    finalscore = 0
    for i in range(tries):
        tmptext = perturb.perturb(text)
        if tmptext not in tmptextscores:
            tokens = gpt2_tokenizer.encode(tmptext, add_special_tokens=False, return_tensors="pt").to(device)
            loss = gpt2_model(tokens, labels = tokens)[0]
            wrongprob = np.exp(loss.cpu().detach().numpy())
            tmptextscores[tmptext] = wrongprob
        finalscore += (rightprob - tmptextscores[tmptext])

        print("*"*i,end="\r")
    print(text)
    return finalscore

evalresult = [["RoBERTa", "RoBERTa (word vector limitation)", "GPT2"]]

with open("testtext.json") as fp:
    textlist = json.load(fp)

tmplist = []

for eachdata in textlist:
    tmp2list = [eachdata[0]]
    tmp3list = []
    for righttext in eachdata[1]:
        tmp3list.append([righttext,
            [roberta2test(righttext), roberta2test(righttext, veclimit = True), gpt2test(righttext)]])
    tmp2list.append(tmp3list)
    tmp3list = []
    for wrongtext in eachdata[2]:
        tmp3list.append([wrongtext,
            [roberta2test(wrongtext), roberta2test(wrongtext, veclimit = True), gpt2test(wrongtext)]])
    tmp2list.append(tmp3list)
    tmplist.append(tmp2list)
evalresult.append(tmplist)

with open("jsondata.js", "w") as fp:
    json.dump(evalresult, fp, ensure_ascii = False, indent = 2)