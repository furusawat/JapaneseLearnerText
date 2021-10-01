import json
import gzip

freqdic = {}

with gzip.open("jawiki-20210920-cirrussearch-content.json.gz") as fp:
    #for cnt, line in enumerate(fp):
    #    if cnt > 10:
    #        break
    for line in fp:
        json_line = json.loads(line)
        if "index" not in json_line:
            for eachchar in json_line["text"]:
                if eachchar in freqdic:
                    freqdic[eachchar] += 1
                else:
                    freqdic[eachchar] = 1

freqdic = sorted(freqdic.items(), key = lambda x: x[1], reverse = True)

with open("freqresult.json","w") as fp:
    json.dump(freqdic, fp, ensure_ascii = False, indent = 2)
