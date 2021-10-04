from transformers import T5Tokenizer, AutoModelForCausalLM
import torch
import numpy as np
import json
import perturb

device = "cuda:0" if torch.cuda.is_available() else "cpu"

tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-gpt2-medium")
tokenizer.do_lower_case = True

model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt2-medium")
model = model.to(device)

with open("result.json") as fp:
    rightlist = json.load(fp)

with open("result.json.origin") as fp:
    wronglist = json.load(fp)

def gpt2test(text, tries = 100):
    tokens = tokenizer.encode(text, add_special_tokens=False, return_tensors="pt").to(device)
    loss = model(tokens, labels = tokens)[0]
    rightprob = np.exp(loss.cpu().detach().numpy())

    lowernum = 0
    for i in range(tries):
        tmptext = perturb.perturb(text)
        tokens = tokenizer.encode(tmptext, add_special_tokens=False, return_tensors="pt").to(device)
        loss = model(tokens, labels = tokens)[0]
        if np.exp(loss.cpu().detach().numpy()) < rightprob:
            print(tmptext)
            lowernum += 1

    return lowernum


for i in range(len(rightlist)):
    print("{} : {}".format(rightlist[i]["sent"], gpt2test(rightlist[i]["sent"])))
    print("{} : {}".format(wronglist[i]["sent"], gpt2test(wronglist[i]["sent"])))
    print()
