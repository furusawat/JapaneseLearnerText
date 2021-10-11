import json

textlist = []

tmplist = ["日本語の文法"]
with open("result.json") as fp:
    rightlist = json.load(fp)
tmp2list = []
for each in rightlist:
    tmp2list.append(each["sent"])
tmplist.append(tmp2list)
with open("result.json.origin") as fp:
    wronglist = json.load(fp)
tmp2list = []
for each in wronglist:
    tmp2list.append(each["sent"])
tmplist.append(tmp2list)
textlist.append(tmplist)

with open("testtext.json", "w") as fp:
    json.dump(textlist, fp, ensure_ascii = False, indent = 2)
