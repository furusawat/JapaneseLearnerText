#pip install transformers
#pip install fugashi
#pip install ipadic

from transformers import AutoTokenizer, AutoModelForMaskedLM
#from transformers import T5Tokenizer, RobertaForMaskedLM
import torch
import json

from gensim.models import KeyedVectors

import random

tokenizer = AutoTokenizer.from_pretrained("cl-tohoku/bert-base-japanese")
model = AutoModelForMaskedLM.from_pretrained("cl-tohoku/bert-base-japanese")
#tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-roberta-base")
#tokenizer.do_lower_case = True
#model = RobertaForMaskedLM.from_pretrained("rinna/japanese-roberta-base")

vec = KeyedVectors(vector_size = next(model.parameters()).shape[1])

words = []

for eachtoken in range(next(model.parameters()).shape[0]):
    #words.append(tokenizer.decode(eachtoken))
    words.append(str(eachtoken))

vec.add_vectors(words, next(model.parameters()).tolist())

def berteval(orig_txt):

    tmplist = []
    
    txttmp = tokenizer.encode(orig_txt, return_tensors="pt")

    for eachtry in range(1, 10):

        txt = txttmp.clone()

        msktkn = random.sample(range(1, len(txttmp[0]) - 1), int((len(txttmp[0]) - 2) / 5 + 1))
        msktmp = []

        #orig_idx = int(txt[0][i])
        for msk in msktkn:
            #msktmp.append(tokenizer.decode(txt[0][msk]))
            msktmp.append(str(txt[0][msk].item()))
            txt[0][msk] = tokenizer.mask_token_id

        outs = model(txt)

        for j, msk in enumerate(msktkn):

            #pred_ids = outs[0][:, msk][0].tolist()

            score = torch.nn.functional.softmax(outs[0][:,msk][0], dim=0)

            preds = []
            for pred_id in range(len(score)):
                #preds.append(tokenizer.decode(pred_id))
                if score[pred_id] > 0.001:
                    preds.append(str(pred_id))

            #tmplist.append([tokenizer.decode(orig_idx), float(score), preds])

            for jj, repword in enumerate(vec.similar_by_word(msktmp[j], topn = 15)):
                if jj < 5 and random.randint(0,1) == 0:
                    continue
                if int(repword[0]) == tokenizer.unk_token_id:
                    continue
                if repword[0] not in preds:
                    #print(repword[0])
                    #print(tokenizer.encode(repword[0], return_tensors="pt"))
                    txt[0][msk] = int(repword[0])

        print(tokenizer.decode(txt[0]))

while True:
    txt = input(">>> ")
    if len(txt) < 1:
        continue
    berteval(txt)
