import json
import regex

hiradic = []
katadic = []
kanjidic = []

with open("freqresult.json") as fp:
    json_list = json.load(fp)

for eachchar in json_list:
    tmp = regex.match(r"\p{Script=Hiragana}", eachchar[0])
    if tmp:
        hiradic.append(eachchar)
        continue

    tmp = regex.match(r"\p{Script=Katakana}", eachchar[0])
    if tmp:
        katadic.append(eachchar)
        continue

    tmp = regex.match(r"\p{Script=Han}", eachchar[0])
    if tmp:
        kanjidic.append(eachchar)
        continue

hiradic = sorted(hiradic, key = lambda x: x[1], reverse = True)
katadic = sorted(katadic, key = lambda x: x[1], reverse = True)
kanjidic = sorted(kanjidic, key = lambda x: x[1], reverse = True)

with open("hirafreq.json","w") as fp:
    json.dump(hiradic, fp, ensure_ascii = False, indent = 2)

with open("katafreq.json","w") as fp:
    json.dump(katadic, fp, ensure_ascii = False, indent = 2)

with open("kanjifreq.json","w") as fp:
    json.dump(kanjidic, fp, ensure_ascii = False, indent = 2)
