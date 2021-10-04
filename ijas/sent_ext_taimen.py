import glob
import json

paths = glob.glob(r"./*/*/*.txt")

allresult = []

for each in paths:
    result = {"tag":[],
            "sent":[]}
    with open(each, encoding = "utf-16-le") as fp:
        for line in fp:
            sent = line.replace("\ufeff","").split()
            result["tag"].append(sent[0])
            result["sent"].append(sent[1])
    allresult.append(result)

with open("result.json","w") as fp:
        json.dump(allresult, fp, ensure_ascii = False, indent = 2)
