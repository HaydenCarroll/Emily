import spacy
from spacy.pipeline import Tagger
from spellchecker import SpellChecker
from spacy import displacy
import FileSearch as fs
from subprocess import call
import subprocess

import os


files = fs.FileSystem()
spell = SpellChecker()
print("loading dictionary please wait")
nlp = spacy.load("en_core_web_lg")
while True:
    print("input command")
    command = input()
    indoc = nlp(command)
    find = nlp("find")
    detected = "";
    file = "";
    displacy.serve(indoc, style="dep")
    # for token in indoc:
    #     print(token.text, token.dep_, token.head.text, token.head.pos_,
    #           [child for child in token.children])
    for token in indoc:
        if token.tag_ == "VB":
            if find.similarity(token) > 0.7:
                #print("possible command", find.similarity(token), token.text)
                detected = token.lemma_
                for child in token.children:
                    #print(child, child.dep)
                    if child.tag_ == "NN" or child.tag_ == "XX" or child.dep == 416:
                        #print("located noun " + child.text)
                        file = child.text


    possible_mispelled_word = detected+"ing"
    corrected_word = spell.correction(possible_mispelled_word)
    final_output = corrected_word+" "+file

    print(final_output)

    subprocess.Popen(["open", "-R", files.find_file(file)])

