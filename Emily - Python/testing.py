import spacy
from spacy.pipeline import Tagger
from spellchecker import SpellChecker
from spacy import displacy
from spacy.matcher import PhraseMatcher
import FileSearch as fs
import time
from tqdm import tqdm

import os

files = fs.FileSystem()
spell = SpellChecker()
print("loading spelling please wait...")
st = time.time()
words = files.get_file_word_spellings()
print("Time to get word spellings", time.time()-st)
st = time.time()
# spell.word_frequency.load_words(words)
for word in tqdm(words):
    # if word in spell.word_frequency.items():
    #     continue
    # print(word)
    spell.word_frequency.add(word)
print("Time to add word spellings", time.time()-st)

print("loading dictionary please wait...")
nlp = spacy.load("en_core_web_lg")
while True:
    print("input command")
    command = input()
    command_word_list = spell.split_words(command)
    for w in command_word_list:
        print(w, spell.word_probability(w))
    break
    indoc = nlp(command)
    find = nlp("find")
    detected = "";
    file = "";
    file_matcher = PhraseMatcher(nlp.vocab)
    displacy.serve(indoc, style="dep") # used for debugging
    for token in indoc:
        if token.tag_ == "VB":
            if find.similarity(token) > 0.7:
                #print("possible command", find.similarity(token), token.text)
                detected = token.lemma_
                for child in token.children:
                    print(child, child.dep)
                    if child.tag_ == "NN" or child.tag_ == "XX" or child.dep == 416:
                        #print("located noun " + child.text)
                        file = child.text


    possible_mispelled_word = detected+"ing"
    corrected_word = spell.correction(possible_mispelled_word)
    final_output = corrected_word+" "+file

    print(final_output)