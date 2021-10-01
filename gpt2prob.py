from transformers import T5Tokenizer, AutoModelForCausalLM
import numpy as np
import json

tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-gpt2-medium")
tokenizer.do_lower_case = True

model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt2-medium")

with open("result.json") as fp:
    rightlist = json.load(fp)

with open("result.json.origin") as fp:
    wronglist = json.load(fp)

for i in range(len(rightlist)):
    tokens = tokenizer.encode(rightlist[i]["sent"], add_special_tokens=False, return_tensors="pt")
    loss = model(tokens, labels = tokens)[0]
    rightprob = np.exp(loss.cpu().detach().numpy())
    print("{} : {}".format(rightlist[i]["sent"], rightprob))

    tokens = tokenizer.encode(wronglist[i]["sent"], add_special_tokens=False, return_tensors="pt")
    loss = model(tokens, labels = tokens)[0]
    wrongprob = np.exp(loss.cpu().detach().numpy())
    print("{} : {}".format(wronglist[i]["sent"], wrongprob))
    print("{} must be lower than {} : {}".format(rightprob, wrongprob, "yes" if rightprob < wrongprob else "no"))
    print()
