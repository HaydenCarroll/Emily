import spacy
from spellchecker import SpellChecker
from spacy import displacy
import FileSearch as fs
from spacy.language import Vocab
import subprocess
import numpy
from tqdm import tqdm
from spacy.matcher import PhraseMatcher
from spacy.pipeline import EntityRuler

import os


files = fs.FileSystem()
spell = SpellChecker()
print("loading dictionary please wait...")
nlp = spacy.load("en_core_web_lg")
print("Adding entity rules please wait...")
terms = files.get_file_terms()
ruler = EntityRuler(nlp, overwrite_ents=True)
patterns = []
for term in terms:
    pattern = []
    words = term.split(" ")
    for word in words:
        pattern.append({"LOWER": word})
    patterns.append({"label": "file", "pattern": pattern})
ruler.add_patterns(patterns)
nlp.add_pipe(ruler)


while True:
    print("input command")
    command = input()
    indoc = nlp(command)
    find = nlp("find")
    detected = "";
    file = "";
    # print([(ent.text, ent.label_) for ent in indoc.ents])
    # displacy.serve(indoc, style="dep") # used for debugging
    position = 0
    for token in indoc:
        position = position + 1
        if token.tag_ == "VB" or token.tag_ == "VBP":
            if find.similarity(token) > 0.7:
                #print("possible command", find.similarity(token), token.text)
                detected = token.lemma_
                remaining = ""
                for word in indoc[position:]:
                    remaining += word.text + " "
                remaining = remaining.strip()
                remaining_doc = nlp(remaining)
                # print([(ent.text, ent.label_) for ent in remaining_doc.ents])
                if len(remaining_doc.ents) > 0:
                    for ent in remaining_doc.ents:
                        if ent.label_ == "file":
                            file = ent.text
                            break
                else:
                    for child in token.children:
                        #print(child, child.dep)
                        if child.tag_ == "NN" or child.tag_ == "XX" or child.dep == 416:
                            #print("located noun " + child.text)
                            file = child.text


    if len(detected) < 2 or len(file) < 2:
        print("could not get name please try again")
        continue

    possible_mispelled_word = detected+"ing"
    corrected_word = spell.correction(possible_mispelled_word)
    final_output = corrected_word+" "+file

    print(final_output)

    subprocess.Popen(["open", "-R", files.find_file(file)])

