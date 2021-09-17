import requests
import re
import json
from bs4 import BeautifulSoup
import copy

with open("japanese_corpus.txt") as fp:
    dumptxt = json.load(fp)

corpusid = []
for eachdump in dumptxt:
    corpusid.append(re.search(r"pt='([0-9]+?)'", eachdump["Preview"]).group(1))

corpusid = sorted(set(corpusid))

mainlink = "https://corpus.icjs.jp/corpus_ja/getCorpus.php?corpusId="

allresult = []

for alleach in corpusid:
    print(mainlink + str(alleach))
    res = requests.get(mainlink + str(alleach))

    soup = BeautifulSoup(res.text, "html.parser")

    soup3 = soup.find_all("div", style="line-height:2;")[1]

    tmpcor = []
    trg = 0
    sent = ""
    tmpdic = {}
    for eachline in soup3.prettify().split("\n")[4:-2]:
        tmpline = eachline.strip()
        if trg > 0:
            trg -= 1
            if trg == 11:
                if tmpline == "</em>":
                    tmpdic["from"] = ""
                    tmpdic["pos"] = len(sent)
                    trg -= 1
                    continue
                tmpdic["from"] = tmpline
                tmpdic["pos"] = len(sent)
                sent += tmpline
            elif trg == 7:
                if tmpline == "</em>":
                    tmpdic["to"] = ""
                    trg -= 1
                    continue
                tmpdic["to"] = tmpline
            elif trg == 0:
                tmpcor.append(copy.deepcopy(tmpdic))

        elif tmpline.find("<span ") == 0:
            trg = 13
        else:
            sent += tmpline

    for eachsent in [e+"。" for e in sent.split("。") if e]:
        alldic = {"cor" : []}
        alldic["sent"] = eachsent
        for eachcor in tmpcor:
            if eachcor["pos"] == None:
                continue
            elif eachcor["pos"] - len(eachsent) >= 0:
                eachcor["pos"] -= len(eachsent)
            else:
                alldic["cor"].append(copy.deepcopy(eachcor))
                eachcor["pos"] = None

        allresult.append(copy.deepcopy(alldic))

with open("result.json","w") as fp:
    json.dump(allresult, fp, ensure_ascii = False, indent = 2)

