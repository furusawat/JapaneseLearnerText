import json
import regex

hiradic = {}
katadic = {}
kanjidic = {}

with open("freqresult.json") as fp:
    json_list = json.load(fp)

topnum = json_list[0][1]

for eachchar in json_list:
    if eachchar[1] < topnum / 10000:
        break
    tmp = regex.match(r"\p{Script=Hiragana}", eachchar[0])
    if tmp:
        hiradic[eachchar[0]] = eachchar[1]
        continue

    tmp = regex.match(r"\p{Script=Katakana}", eachchar[0])
    if tmp:
        katadic[eachchar[0]] = eachchar[1]
        continue

    tmp = regex.match(r"\p{Script=Han}", eachchar[0])
    if tmp:
        kanjidic[eachchar[0]] = eachchar[1]
        continue

with open("hirafreq.json","w") as fp:
    json.dump(hiradic, fp, ensure_ascii = False, indent = 2)

with open("katafreq.json","w") as fp:
    json.dump(katadic, fp, ensure_ascii = False, indent = 2)

with open("kanjifreq.json","w") as fp:
    json.dump(kanjidic, fp, ensure_ascii = False, indent = 2)
