import json

htmlfile = """<!DOCTYPE html><html lang='ja'><head>
<meta charset='utf-8'><title>visualized</title></head><body>"""

with open("evalresult.json") as fp:
    evallist = json.load(fp)

for eachsent in evallist:
    for eachchar in eachsent:
        htmlfile += "<char style='color:RGB({},0,0)'>{}</char>".format(255 - eachchar[1] * 255, eachchar[0])
    htmlfile += "<br/>"

htmlfile += "</body></html>"

with open("visualized.html", "w") as fp:
    fp.write(htmlfile)
