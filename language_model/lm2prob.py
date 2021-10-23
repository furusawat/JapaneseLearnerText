from transformers import T5Tokenizer, RobertaForMaskedLM
from transformers import AutoModelForCausalLM
import torch
import json
import perturb
import copy
from gensim.models import KeyedVectors
import os
import pickle
import gensimword

device = "cuda:0" if torch.cuda.is_available() else "cpu"

roberta_tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-roberta-base")
roberta_tokenizer.do_lower_case = True

roberta_model = RobertaForMaskedLM.from_pretrained("rinna/japanese-roberta-base")
roberta_model = roberta_model.to(device)

print("== RoBERTa are loaded ==")

gpt2_tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-gpt2-medium")
gpt2_tokenizer.do_lower_case = True

gpt2_model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt2-medium")
gpt2_model = gpt2_model.to(device)

print("== GPT-2 are loaded ==")

roberta_worddic = gensimword.gensim_load(roberta_model, "./roberta_vecsim_data.pickle")
#gpt2_worddic = gensimword.gensim_load(gpt2_model, "./gpt2_vecsim_data.pickle")

class lm2prob_class():
    def __init__(self, textlist, num = 50, tries = 100, batchnum = 8):
        self.evalresult = [[]]
        self.textlist = textlist
        self.num = num
        self.tries = tries
        self.batchnum = batchnum

    def robertaeval(self, orig_txt):
        tmplist = []
        localbatch = len(orig_txt)
        txttmp = roberta_tokenizer(["[CLS]" + x for x in orig_txt], padding = True, return_tensors="pt").to(device)["input_ids"]
        for i in range(1, len(txttmp[0])):
            txt = copy.deepcopy(txttmp)

            orig_idx = [int(x[i]) for x in txt]

            for jj in range(localbatch):
                txt[jj][i] = roberta_tokenizer.mask_token_id

            posi_ids = list(range(0, txt.size(1)))
            posi_id_tensor = torch.LongTensor([posi_ids] * localbatch).to(device)

            with torch.no_grad():
                outs = roberta_model(input_ids = txt, position_ids = posi_id_tensor)

            score = [[0, 0, 0]] * localbatch
            for jj in range(localbatch):
                max_ids = outs[0][jj, i].topk(1).indices
                score[jj][0] = torch.nn.functional.softmax(outs[0][jj,i], dim=0)
                score[jj][0] = score[jj][0][orig_idx[jj]] / score[jj][0][max_ids[0]]
                if "RoBERTa" not in self.evalresult[0]:
                    self.evalresult[0].append("RoBERTa")

                score[jj][1] = torch.nn.functional.softmax(outs[0][jj,i], dim=0)
                score[jj][1] = torch.log(score[jj][1][orig_idx[jj]] / score[jj][1][max_ids[0]])
                if "RoBERTa (log)" not in self.evalresult[0]:
                    self.evalresult[0].append("RoBERTa (log)")

                tmpouts = outs[0][jj].index_select(1,
                        torch.LongTensor(list(roberta_worddic[orig_idx[jj]].keys())).to(device))
                max_ids = tmpouts[i].topk(1).indices
                score[jj][2] = torch.nn.functional.softmax(tmpouts[i], dim=0)
                score[jj][2] = (score[jj][2][roberta_worddic[orig_idx[jj]][orig_idx[jj]]]
                                / score[jj][2][max_ids[0]])
                if "RoBERTa (vec)" not in self.evalresult[0]:
                    self.evalresult[0].append("RoBERTa (vec)")

            tmplist.append(torch.Tensor(score))

        allscore = torch.Tensor([[0]*len(score[0])] * localbatch)
        for eachscore in tmplist:
            allscore = torch.add(allscore, eachscore)
        #return torch.divide(allscore, len(tmplist))
        return allscore

    def gpt2eval(self, orig_txt):
        tokens = gpt2_tokenizer(orig_txt, padding = True,
                    add_special_tokens=False, return_tensors="pt").to(device)["input_ids"]
        with torch.no_grad():
            loss = gpt2_model(tokens, labels = tokens)[1]
        outloss = []
        for i in range(len(loss)):
            outloss.append([sum(loss[i,[j for j in range(len(loss[0]))],tokens[i]])])
        if "GPT-2" not in self.evalresult[0]:
            self.evalresult[0].append("GPT-2")

        return torch.Tensor(outloss)

    def lmtest(self, text):
        roberta_rightprob = self.robertaeval([text])[0]
        gpt2_rightprob = self.gpt2eval([text])[0]

        finalscore = torch.Tensor([0]*(len(roberta_rightprob)+len(gpt2_rightprob)))
        for i in range(int(self.tries / self.batchnum)):
            tmptext = []
            for jj in range(self.batchnum):
                tmptext.append(perturb.perturb(text))

            roberta_wrongprob = self.robertaeval(tmptext)
            gpt2_wrongprob = self.gpt2eval(tmptext)
            for jj in range(self.batchnum):
                finalscore += torch.sub(torch.cat((roberta_rightprob, gpt2_rightprob)),
                                torch.cat((roberta_wrongprob[jj], gpt2_wrongprob[jj])))

            print("-"*i,end="\r")

        remainer = self.tries - int(self.tries / self.batchnum) * self.batchnum
        if remainer > 0:
            tmptext = []
            for jj in range(remainer):
                tmptext.append(perturb.perturb(text))

            roberta_wrongprob = self.robertaeval(tmptext)
            gpt2_wrongprob = self.gpt2eval(tmptext)
            for jj in range(remainer):
                finalscore += torch.sub(torch.cat((roberta_rightprob, gpt2_rightprob)),
                                torch.cat((roberta_wrongprob[jj], gpt2_wrongprob[jj])))

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

lm2eval = lm2prob_class(textlist = textlist)
lm2eval.mainloop()

with open("jsondata.js", "w") as fp:
    json.dump(lm2eval.evalresult, fp, ensure_ascii = False, indent = 2)
