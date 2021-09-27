#pip install transformers
#pip install fugashi
#pip install ipadic

from transformers import AutoTokenizer, AutoModelForMaskedLM
#from transformers import T5Tokenizer, RobertaForMaskedLM
import torch
import json

from gensim.models import KeyedVectors

tokenizer = AutoTokenizer.from_pretrained("cl-tohoku/bert-base-japanese")
model = AutoModelForMaskedLM.from_pretrained("cl-tohoku/bert-base-japanese")
#tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-roberta-base")
#tokenizer.do_lower_case = True
#model = RobertaForMaskedLM.from_pretrained("rinna/japanese-roberta-base")

vec = KeyedVectors(vector_size = next(model.parameters()).shape[1])

words = []

for eachtoken in range(next(model.parameters()).shape[0]):
    words.append(tokenizer.decode(eachtoken))

vec.add_vectors(words, next(model.parameters()).tolist())

#for i, eachtoken in enumerate(words):
#    if i % 100 == 99:
#        break
#    print("similar_by_word({})\n{}".format(eachtoken, vec.similar_by_word(eachtoken)))
print("similar_by_word({})\n{}".format("か ら", vec.similar_by_word("か ら")))
print("similar_by_word({})\n{}".format("よ り", vec.similar_by_word("よ り")))
print("similar_by_word({})\n{}".format("ま で", vec.similar_by_word("ま で")))
