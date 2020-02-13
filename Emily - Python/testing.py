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


print("loading dictionary please wait...")
nlp = spacy.load("en_core_web_lg")
files = fs.FileSystem()
spell = SpellChecker()


def start():
    print("Adding entity rules please wait...")
    file_terms = files.get_file_terms()
    dir_terms = files.get_dir_terms()
    vector_data = {}
    for term in dir_terms:
        words = term.split(" ")
        for word in words:
            data = {word: numpy.random.uniform(-1, 1, (300,))}
            vector_data.update(data)

    vocab = nlp.vocab
    for word, vector in vector_data.items():
        vocab.set_vector(word, vector)
    ruler = EntityRuler(nlp, overwrite_ents=True)
    # list of words reserved for commands
    reserved_words = ["find", "copy", "open", "move"]
    _patterns = get_patterns(file_terms, dir_terms, reserved_words)
    # _patterns = get_file_patterns(file_terms, reserved_words)
    # _patterns = get_dir_patterns(dir_terms, reserved_words)
    ruler.add_patterns(_patterns)
    nlp.add_pipe(ruler)
    main()


def main():
    while True:
        print("input command")
        command = input()
        indoc = nlp(command)
        find_command = nlp("find")
        open_command = nlp("open")
        move_command = nlp("move")
        detected = "";
        file = "";
        action = ""
        print([(ent.text, ent.label_, ent.ent_id_) for ent in indoc.ents])
        # displacy.serve(indoc, style="dep") # used for debugging
        position = 0
        for token in indoc:
            position = position + 1
            #if token.tag_ == "VB" or token.tag_ == "VBP":
            if find_command.similarity(token) > 0.7:
                toup = find(token, indoc, position)
                detected = toup[0]
                file = toup[1]
                action = "find"
                break
            elif open_command.similarity(token) > 0.7:
                toup = find(token, indoc, position)
                detected = toup[0]
                file = toup[1]
                action = "open"
                break
            elif move_command.similarity(token) > 0.7:
                print()

        if len(detected) < 2:
            print("could not get command please try again")
            continue
        elif len(file) < 2:
            print("could not get file name please try again")

        possible_misspelled_word = detected+"ing"
        corrected_word = spell.correction(possible_misspelled_word)
        final_output = corrected_word+" "+file

        print(final_output)
        # if action == "find":
        #     subprocess.Popen(["open", "-R", files.find_file(file)])
        # elif action == "open":
        #     subprocess.Popen(["open", files.find_file(file)])


def find(token, indoc, position):
    # print("possible command", find.similarity(token), token.text)
    detected = token.lemma_
    file = ""
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
            # print(child, child.dep)
            if child.tag_ == "NN" or child.tag_ == "XX" or child.dep == 416:
                print("located noun " + child.text)
                for dir in files.get_dir_terms():
                    words = dir.split(" ")
                    for word in words:
                        s = nlp(word).similarity(nlp(child.text))
                        if s > 0.9:
                            print(word)
                file = child.text
    return [detected, file]


def copy():
    return


def move():
    return


def get_patterns(file_terms, dir_terms, reserved_words):
    patterns = []
    for term in file_terms:
        pattern = []
        words = term.split(" ")
        for word in words:
            # if the word is a reserved word then add as a command
            if word.lower() in reserved_words:
                patterns.append({"label": "command", "pattern": [{"LOWER": word}]})
            # else add as a file
            else:
                pattern.append({"LOWER": word})
        # make sure that empty pattern isn't added
        if len(pattern) < 1:
            continue
        patterns.append({"label": "file", "pattern": pattern})
    for term in dir_terms:
        pattern = []
        words = term.split(" ")
        for word in words:
            # if the word is a reserved word then add as a command
            if word.lower() in reserved_words:
                patterns.append({"label": "command", "pattern": [{"LOWER": word}]})
            # else add as a file
            else:
                if word.lower() == "saad":
                    print(str(words))
                pattern.append({"LOWER": word})
        # make sure that empty pattern isn't added
        if len(pattern) < 1:
            continue
        patterns.append({"label": "file", "pattern": pattern})
    return patterns


def get_file_patterns(file_terms, reserved_words):
    patterns = []
    for term in file_terms:
        pattern = []
        words = term.split(" ")
        for word in words:
            # if the word is a reserved word then add as a command
            if word.lower() in reserved_words:
                patterns.append({"label": "command", "pattern": [{"LOWER": word}]})
            # else add as a file
            else:
                pattern.append({"LOWER": word})
        # make sure that empty pattern isn't added
        if len(pattern) < 1:
            continue
        patterns.append({"label": "file", "pattern": pattern})
    return patterns


def get_dir_patterns(dir_terms, reserved_words):
    patterns = []
    for term in dir_terms:
        pattern = []
        words = term.split(" ")
        for word in words:
            # if the word is a reserved word then add as a command
            if word.lower() in reserved_words:
                patterns.append({"label": "command", "pattern": [{"LOWER": word}]})
            # else add as a file
            else:
                pattern.append({"LOWER": word})
        # make sure that empty pattern isn't added
        if len(pattern) < 1:
            continue
        patterns.append({"label": "direct", "pattern": pattern})
    return patterns


start()
