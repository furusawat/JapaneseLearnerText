#pip install transformers
#pip install fugashi
#pip install ipadic

#from transformers import AutoTokenizer, AutoModelForMaskedLM
from transformers import T5Tokenizer, RobertaForMaskedLM
import torch
import json

#tokenizer = AutoTokenizer.from_pretrained("cl-tohoku/bert-base-japanese")
#model = AutoModelForMaskedLM.from_pretrained("cl-tohoku/bert-base-japanese")
tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-roberta-base")
tokenizer.do_lower_case = True
model = RobertaForMaskedLM.from_pretrained("rinna/japanese-roberta-base")

def berteval(orig_txt):

    tmplist = []
    
    txttmp = tokenizer.encode(orig_txt, return_tensors="pt")

    for i in range(1, len(txttmp[0]) - 1):

        txt = txttmp.clone()

        orig_idx = int(txt[0][i])
        txt[0][i] = tokenizer.mask_token_id

        outs = model(txt)

        pred_ids = outs[0][:, i][0].topk(5).indices.tolist()

        score = torch.nn.functional.softmax(outs[0][:,i][0], dim=0)
        score = score[orig_idx] / score[pred_ids[0]]

        preds = []
        for pred_id in pred_ids:
            preds.append(tokenizer.decode(pred_id))

        tmplist.append([tokenizer.decode(orig_idx), float(score), preds])

    return tmplist

import copy

def robertaeval(orig_txt):

    tmplist = []

    txttmp = tokenizer.tokenize("[CLS]" + orig_txt)

    for i in range(1, len(txttmp) - 1):

        txt = copy.deepcopy(txttmp)

        orig_idx = tokenizer.convert_tokens_to_ids([txt[i]])[0]
        txt[i] = tokenizer.mask_token

        txt_ids = tokenizer.convert_tokens_to_ids(txt)
        txt_tensor = torch.LongTensor([txt_ids])

        posi_ids = list(range(0, txt_tensor.size(1)))
        posi_id_tensor = torch.LongTensor([posi_ids])

        with torch.no_grad():
            outs = model(input_ids = txt_tensor, position_ids = posi_id_tensor)
            pred_ids = outs[0][0, i].topk(5).indices

        score = torch.nn.functional.softmax(outs[0][0,i], dim=0)
        score = score[orig_idx] / score[pred_ids[0]]

        preds = []
        for pred_id in pred_ids:
            preds.append(tokenizer.convert_ids_to_tokens([pred_id.item()])[0])

        tmplist.append([tokenizer.convert_ids_to_tokens([orig_idx])[0], float(score), preds])

    return tmplist


with open("result.json") as fp:
    sentlist = json.load(fp)

evalresultlist = []

for eachsent in sentlist:
    print(eachsent["sent"])
    #evalresultlist.append(berteval(eachsent["sent"]))
    evalresultlist.append(robertaeval(eachsent["sent"]))

with open("evalresult.json", "w") as fp:
    json.dump(evalresultlist, fp, ensure_ascii = False, indent = 2)
