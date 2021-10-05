from transformers import T5Tokenizer, RobertaForMaskedLM
import torch
import numpy as np
import json
import perturb
import copy

device = "cuda:0" if torch.cuda.is_available() else "cpu"

tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-roberta-base")
tokenizer.do_lower_case = True

model = RobertaForMaskedLM.from_pretrained("rinna/japanese-roberta-base")
model = model.to(device)

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

        max_ids = outs[0][0, i].topk(1).indices
        score = torch.nn.functional.softmax(outs[0][0,i], dim=0)
        score = score[orig_idx] / score[max_ids[0]]

        tmplist.append(float(score))

    allscore = 0
    for eachscore in tmplist:
        allscore += eachscore

    return [tmplist, allscore/len(tmplist)]


def roberta2test(text, tries = 100):
    rightprob = robertaeval(text)
    print("{} : {} -> avg. {}".format(text, str(rightprob[0]), rightprob[1]))
    print("*"*40)

    lowernum = 0
    for i in range(tries):
        tmptext = perturb.perturb(text)
        wrongprob = robertaeval(tmptext)
        if wrongprob[1] > rightprob[1]:
            print("{} : {} \n -> avg. {}".format(tmptext, str(wrongprob[0]), wrongprob[1]))
            lowernum += 1

    print("*"*40)
    print("# of successful perturbation : {}\t: lower is better".format(lowernum))


for i in range(len(rightlist)):
    roberta2test(rightlist[i]["sent"])
    print("-"*80)
    roberta2test(wronglist[i]["sent"])
    print("-"*80)
    print("-"*80)
    print("-"*80)
