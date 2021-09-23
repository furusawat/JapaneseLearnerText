#pip install transformers
#pip install fugashi
#pip install ipadic

from transformers import AutoTokenizer, AutoModelForMaskedLM
import torch
import json

tokenizer = AutoTokenizer.from_pretrained("cl-tohoku/bert-base-japanese-char")
model = AutoModelForMaskedLM.from_pretrained("cl-tohoku/bert-base-japanese-char")

def berteval(orig_txt):

    tmplist = []
    
    for i in range(len(orig_txt)):

        txt = tokenizer.encode(orig_txt, return_tensors="pt")
        txt[0][i + 1] = tokenizer.mask_token_id

        outs = model(txt)

        orig_idx = tokenizer.encode(orig_txt[i])[1]

        pred_ids = outs[0][:, i + 1][0].topk(5).indices.tolist()

        score = torch.nn.functional.softmax(outs[0][:,i + 1][0], dim=0)
        score = score[orig_idx] / score[pred_ids[0]]

        preds = []
        for pred_id in pred_ids:
            preds.append(tokenizer.decode(pred_id))

        tmplist.append([orig_txt[i], float(score), preds])

    return tmplist

with open("result.json") as fp:
    sentlist = json.load(fp)

evalresultlist = []

for eachsent in sentlist:
    print(eachsent["sent"])
    evalresultlist.append(berteval(eachsent["sent"]))

with open("evalresult.json", "w") as fp:
    json.dump(evalresultlist, fp, ensure_ascii = False, indent = 2)
