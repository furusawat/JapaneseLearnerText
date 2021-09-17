import requests
import re
import json
from bs4 import BeautifulSoup
import copy

mainlink = "https://hinoki-project.org/natane/document/list?page="

allresult = []

for alleach in range(1,16):
    print(mainlink + str(alleach))
    res = requests.get(mainlink + str(alleach))

    soup = BeautifulSoup(res.text, "html.parser")
    soup = soup.find("tbody")

    for each in soup.find_all("a"):
        print(each["href"])
        res2 = requests.get("https://hinoki-project.org" + each["href"])
        soup2 = BeautifulSoup(re.sub(r"[\n\r]", "", res2.text), "html.parser")

        soup3 = soup2.find("p")

        tmpcor = []
        trg = 0
        sent = ""
        tmpdic = {}
        for eachline in soup3.prettify().split("\n")[1:-2]:
            tmpline = eachline.strip()
            if trg > 0:
                trg -= 1
                if trg == 4:
                    tmpdic["from"] = tmpline
                    tmpdic["pos"] = len(sent)
                    sent += tmpline
                elif trg == 2:
                    tmpdic["to"] = tmpline[2:]
                elif trg == 0:
                    tmpcor.append(copy.deepcopy(tmpdic))

            elif tmpline.find("<span ") == 0:
                trg = 5
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

