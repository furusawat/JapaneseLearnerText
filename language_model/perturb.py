import numpy
import json

hiradic = {}
katadic = {}
kanjidic = {}
nihongodic = {}

with open("dump/hirafreq.json") as fp:
    hiradic = json.load(fp)
with open("dump/katafreq.json") as fp:
    katadic = json.load(fp)
with open("dump/kanjifreq.json") as fp:
    kanjidic = json.load(fp)
with open("dump/nihongofreq.json") as fp:
    nihongodic = json.load(fp)

def perturb_main(text, dic, num):
    posi = []
    weight = []
    for i in range(len(text)):
        if text[i] in dic:
            posi.append(i)
            weight.append(dic[text[i]])
    if posi == []:
        return text

    choice = numpy.random.randint(0, 3)
    if choice == 0:
        tmpposi = []
        tmpweight = [0] * (len(text) + 1)
        for jj, eachposi in enumerate(posi):
            tmpposi.append(eachposi)
            tmpposi.append(eachposi + 1)
            tmpweight[eachposi] += weight[jj]
            tmpweight[eachposi + 1] += weight[jj]
        tmpposi = list(set(tmpposi))
        tmpweight = [ii for ii in tmpweight if ii != 0]
        position = numpy.random.choice(tmpposi, p = tmpweight / numpy.array(tmpweight).sum(), replace = False, size = num)
        for ps in position:
            pb = numpy.array(list(dic.values()))
            text = text[:ps] + numpy.random.choice(list(dic.keys()), p = pb / pb.sum())[0] + text[ps:]
    elif choice == 1:
        position = numpy.random.choice(posi, p = weight / numpy.array(weight).sum(), replace = False, size = num)
        for ps in position:
            text = text[:ps] + text[ps + 1:]
    elif choice == 2:
        position = numpy.random.choice(posi, p = weight / numpy.array(weight).sum(), replace = False, size = num)
        extext = [ii for n, ii in enumerate(text) if n in position]
        tmpdic = {k:v for k,v in dic.items() if k not in extext}
        for ps in position:
            pb = numpy.array(list(tmpdic.values()))
            text = text[:ps] + numpy.random.choice(list(tmpdic.keys()), p = pb / pb.sum())[0] + text[ps + 1:]

    return text

def perturb(text, hiragana = False, katakana = False, kanji = False, nihongo = True, num = 1):
    useddic = {}
    if hiragana:
        useddic.update(hiradic)
    if katakana:
        useddic.update(katadic)
    if kanji:
        useddic.update(kanji)
    if nihongo:
        useddic.update(nihongo)

    result = perturb_main(text, useddic, num)

    return result
