import glob
import os
from bs4 import BeautifulSoup

import re
import json
import copy

allresult = []

for fn in glob.glob("tensaku_xml/*.xml"):
    print(fn)
    with open(fn) as fp:
        soup = BeautifulSoup(re.sub(r"[\*＊]","",fp.read()), "xml")

    for tag in soup.find_all("title"):
        tag.decompose()

    soup3 = soup.find(["comp", "essay"])

    tmpreg = {}
    trgreg = ""

    tmpcor = []
    trg = 0
    trgname = ""
    sent = ""
    tmpdic = {}
    for eachline in soup3.prettify().split("\n")[1:-2]:
        tmpline = eachline.strip()
        if trg > 0:
            trg -= 1
            if trgname == "rep":
                if trg == 1:
                    if tmpline.find("<") == 0:
                        tmpdic["from"] = ""
                        tmpdic["pos"] = len(sent)
                        tmpcor.append(copy.deepcopy(tmpdic))
                        trg = 0
                        continue
                    tmpdic["from"] = tmpline
                    tmpdic["pos"] = len(sent)
                    sent += tmpline
                    if trgreg != "":
                        tmpreg[trgreg] = tmpline
                        trgreg = ""
                elif trg == 0:
                    tmpcor.append(copy.deepcopy(tmpdic))

        elif tmpline.find("<put ") == 0:
            tmpdic["from"] = ""
            tmpdic["pos"] = len(sent)
            tmpdic["to"] = re.search(r"value=\"(.*?)\"",tmpline).group(1)
            tmpcor.append(copy.deepcopy(tmpdic))
        elif tmpline.find("<rep ") == 0:
            trg = 2
            tmpdic["to"] = re.search(r"value=\"(.*?)\"",tmpline).group(1)
            trgname = "rep"
        elif tmpline.find("<del>") == 0:
            trg = 2
            tmpdic["to"] = ""
            trgname = "rep"
        elif tmpline.find("<doubt ") == 0:
            trg = 2
            tmpvalue = re.search(r"value=\"(.*?)\"",tmpline)
            if tmpvalue == None:
                tmpdic["to"] = ""
            else:
                tmpdic["to"] = tmpvalue.group(1)[1:]
            trgname = "rep"
        elif tmpline.find("<better ") == 0 or tmpline.find("<correct ") == 0:
            if tmpline[-2:] == "/>":
                tmpdic["from"] = ""
                tmpdic["pos"] = len(sent)
                tmpvalue = re.search(r"value=\"(.*?)\"",tmpline)
                if tmpvalue == None:
                    continue
                else:
                    tmpdic["to"] = tmpvalue.group(1)
                tmpcor.append(copy.deepcopy(tmpdic))
            else:
                trg = 2
                tmpvalue = re.search(r"value=\"(.*?)\"",tmpline)
                if tmpvalue == None:
                    trgreg = re.search(r"comment=\"(.*?)\"",tmpline).group(1)
                    tmpdic["to"] = ""
                else:
                    tmpdic["to"] = tmpvalue.group(1)
                trgname = "rep"
        elif tmpline.find("<unclear ") == 0:
            trg = 2
            tmpdic["to"] = re.search(r"comment=\"(.*?)\"",tmpline).group(1)
            trgname = "rep"
        elif tmpline.find("<") == 0:
            continue
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
                if eachcor["to"] in tmpreg:
                    eachcor["to"] = tmpreg[eachcor["to"]]
                alldic["cor"].append(copy.deepcopy(eachcor))
                eachcor["pos"] = None

        allresult.append(copy.deepcopy(alldic))

with open("result.json","w") as fp:
    json.dump(allresult, fp, ensure_ascii = False, indent = 2)

