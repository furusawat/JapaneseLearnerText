import json
import re

textlist = []

tmplist = ["日本語の文法"]
with open("dump/result.json") as fp:
    rightlist = json.load(fp)
tmp2list = []
for each in rightlist:
    tmp2list.append(each["sent"])
tmplist.append(tmp2list)
with open("dump/result.json.origin") as fp:
    wronglist = json.load(fp)
tmp2list = []
for each in wronglist:
    tmp2list.append(each["sent"])
tmplist.append(tmp2list)
textlist.append(tmplist)

def extbitext(name, path):
    tmplist = [name]
    with open(path) as fp:
        icjslist = json.load(fp)
    tmprightlist = []
    tmpwronglist = []
    for eachsent in icjslist:
        difflen = 0
        wrongsent = eachsent["sent"]
        if eachsent["cor"] != []:
            rightsent = wrongsent[:eachsent["cor"][0]["pos"]]
            for i in range(len(eachsent["cor"]) - 1):
                tmpsent = re.sub(r"\((.*)\|.*\)", r"\1", eachsent["cor"][i]["to"])
                tmpsent = re.sub(r"[φø]", "", tmpsent)
                rightsent += re.sub(r"[｜【\|].*", "", tmpsent)
                rightsent += wrongsent[eachsent["cor"][i]["pos"] + len(eachsent["cor"][i]["from"]):
                        eachsent["cor"][i + 1]["pos"]]
                difflen += len(eachsent["cor"][i]["from"])
            tmpsent = re.sub(r"\((.*)\|.*\)", r"\1", eachsent["cor"][-1]["to"])
            tmpsent = re.sub(r"[φø]", "", tmpsent)
            rightsent += re.sub(r"[｜【\|].*", "", tmpsent)
            rightsent += wrongsent[eachsent["cor"][-1]["pos"] + len(eachsent["cor"][-1]["from"]):]
            difflen += len(eachsent["cor"][-1]["from"])
            if difflen < len(wrongsent) / 2:
                tmprightlist.append(rightsent)
                tmpwronglist.append(wrongsent)
    tmplist.append(tmprightlist)
    tmplist.append(tmpwronglist)
    return tmplist

tmplist = extbitext("国際日本語学習者作文コーパス", "../icjs/result.json")
textlist.append(tmplist)
tmplist = extbitext("学習者作文コーパス「なたね」", "../natane/result.json")
textlist.append(tmplist)

with open("testtext.json", "w") as fp:
    json.dump(textlist, fp, ensure_ascii = False, indent = 2)
