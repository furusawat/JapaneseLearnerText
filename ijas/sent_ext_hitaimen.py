import glob
import json
import re

paths = glob.glob(r"./*/*/*.txt")

allresult = []

for each in paths:
    result = {"tag":[],
            "sent":[]}
    with open(each, encoding = "cp932") as fp:
        result["tag"] = re.sub(r"[/_]",r"-",each[2:])
        for line in fp:
            if line.find("-----") != -1 or line.strip() == "":
                continue
            if line.find("。") == -1:
                result["sent"].append(line.strip())
                continue
            sent = [e + "。" for e in line[:-1].split("。") if e]
            for eachsent in sent:
                result["sent"].append(eachsent.strip())
    allresult.append(result)

with open("result.json","w") as fp:
        json.dump(allresult, fp, ensure_ascii = False, indent = 2)
