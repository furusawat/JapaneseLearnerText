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
import math
import gensimword

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

roberta_worddic = gensimword.gensim_load(roberta_model, "./roberta_vecsim_data.pickle")
#gpt2_worddic = gensimword.gensim_load(gpt2_model, "./gpt2_vecsim_data.pickle")

class lm2prob_class():
    def __init__(self, textlist, num = 50, tries = 100):
        self.evalresult = [[]]
        self.textlist = textlist
        self.num = num
        self.tries = tries

    def robertaeval(self, orig_txt):
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

            score = [None, None, None]
            max_ids = outs[0][0, i].topk(1).indices
            score[0] = torch.nn.functional.softmax(outs[0][0,i], dim=0)
            score[0] = score[0][orig_idx] / score[0][max_ids[0]]
            if "RoBERTa" not in self.evalresult[0]:
                self.evalresult[0].append("RoBERTa")

            score[1] = torch.nn.functional.softmax(outs[0][0,i], dim=0)
            score[1] = math.log(score[1][orig_idx] / score[1][max_ids[0]])
            if "RoBERTa (log)" not in self.evalresult[0]:
                self.evalresult[0].append("RoBERTa (log)")

            tmpouts = outs[0].index_select(2, torch.LongTensor(list(roberta_worddic[orig_idx].keys())).to(device))
            max_ids = tmpouts[0, i].topk(1).indices
            score[2] = torch.nn.functional.softmax(tmpouts[0,i], dim=0)
            score[2] = score[2][roberta_worddic[orig_idx][orig_idx]] / score[2][max_ids[0]]
            if "RoBERTa (vec)" not in self.evalresult[0]:
                self.evalresult[0].append("RoBERTa (vec)")

            tmplist.append(score)

        allscore = [0]*len(score)
        for eachscore in tmplist:
            allscore = np.add(allscore, eachscore)
        return np.divide(allscore, len(tmplist))

    def gpt2eval(self, orig_txt):
        tokens = gpt2_tokenizer.encode(orig_txt, add_special_tokens=False, return_tensors="pt").to(device)
        loss = gpt2_model(tokens, labels = tokens)[0]
        if "GPT-2" not in self.evalresult[0]:
            self.evalresult[0].append("GPT-2")

        return [np.exp(loss.cpu().detach().numpy())]

    def lmtest(self, text):
        roberta_rightprob = self.robertaeval(text)
        gpt2_rightprob = self.gpt2eval(text)

        tmptextscores = {}
        finalscore = [0]*(len(roberta_rightprob)+len(gpt2_rightprob))
        for i in range(self.tries):
            tmptext = perturb.perturb(text)
            if tmptext not in tmptextscores:
                roberta_wrongprob = self.robertaeval(tmptext)
                gpt2_wrongprob = self.gpt2eval(tmptext)
                tmptextscores[tmptext] = [*roberta_wrongprob, *gpt2_wrongprob]
            finalscore += np.subtract([*roberta_rightprob, *gpt2_rightprob], tmptextscores[tmptext])

            print("-"*i,end="\r")
        print(text)
        return [float(x) for x in finalscore]

    def mainloop(self):
        tmplist = []
        for eachdata in self.textlist:
            tmp2list = [eachdata[0]]
            tmp3list = []
            for righttext in eachdata[1][:self.num]:
                tmp3list.append([righttext, self.lmtest(righttext)])
            tmp2list.append(tmp3list)
            tmp3list = []
            for wrongtext in eachdata[2][:self.num]:
                tmp3list.append([wrongtext, self.lmtest(wrongtext)])
            tmp2list.append(tmp3list)
            tmplist.append(tmp2list)
        self.evalresult.append(tmplist)

with open("testtext.json") as fp:
    textlist = json.load(fp)

lm2eval = lm2prob_class(textlist = textlist, num = 2)
lm2eval.mainloop()

with open("jsondata.js", "w") as fp:
    json.dump(lm2eval.evalresult, fp, ensure_ascii = False, indent = 2)
