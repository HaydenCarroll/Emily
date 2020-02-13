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
from shutil import copyfile
from shutil import move
import os
import getpass
import datetime
import pyttsx3

emily = pyttsx3.init()
voices = emily.getProperty('voices')
emily.setProperty('voice', voices[10].id)
emily.setProperty('rate', 172)
print("loading dictionary please wait...")
nlp = spacy.load("en_core_web_lg")
files = fs.FileSystem()
spell = SpellChecker()


def start():
    print("Adding entity rules please wait...")
    file_terms = files.get_file_terms()
    dir_terms = files.get_dir_terms()
    ruler = EntityRuler(nlp, overwrite_ents=True)
    # list of words reserved for commands
    reserved_words = ["find", "copy", "open", "move"]
    _patterns = get_file_patterns(file_terms, reserved_words)
    [_patterns.append(pattern) for pattern in get_dir_patterns(dir_terms, reserved_words)]
    ruler.add_patterns(_patterns)
    nlp.add_pipe(ruler)
    main()


def main():
    current_time = datetime.datetime.now().hour
    greeting_phrase = ""
    if 5 < current_time < 10:
        greeting_phrase = "Good morning"
    elif 10 < current_time < 14:
        greeting_phrase = "Good afternoon"
    elif 14 < current_time < 19:
        greeting_phrase = "Good evening"
    else:
        greeting_phrase = "Good evening"
    emily.say(greeting_phrase + " Hayden, how may I assist you?")
    emily.runAndWait()
    while True:
        print("input command")
        command = input()
        indoc = nlp(command)
        find_command = nlp("find")
        open_command = nlp("open")
        copy_command = nlp("copy")
        move_command = nlp("move")
        quit_command = nlp("goodbye")
        detected = ""
        file = ""
        destination = ""
        action = ""
        # print([(ent.text, ent.label_) for ent in indoc.ents])
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
            elif copy_command.similarity(token) > 0.7:
                toup = copy(token, indoc, position)
                detected = toup[0]
                file = toup[1]
                destination = toup[2]
                action = "copy"
                break
            elif move_command.similarity(token) > 0.7:
                toup = copy(token, indoc, position)
                detected = toup[0]
                file = toup[1]
                destination = toup[2]
                action = "move"
                break
            elif quit_command.similarity(token) > 0.7:
                current_time = datetime.datetime.now().hour
                exit_phrase = ""
                if 5 < current_time < 10:
                    exit_phrase = "have a great morning!"
                elif 10 < current_time < 14:
                    exit_phrase = "have a great afternoon!"
                elif 14 < current_time < 19:
                    exit_phrase = "have a great evening!"
                else:
                    print("Goodnight", getpass.getuser(), "!")
                    emily.say("Goodnight Hayden")
                    exit(0)
                # print("Goodbye", getpass.getuser(), exit_phrase)
                emily.say("Goodbye Hayden,"+exit_phrase)
                emily.runAndWait()
                exit(0)

        if len(detected) < 2:
            print("could not get command please try again")
            emily.say("could not get command please try again")
            emily.runAndWait()
            continue
        elif len(file) < 2:
            print("could not get file name please try again")
            emily.say("could not get file name please try again")
            emily.runAndWait()
            continue

        possible_misspelled_word = detected+"ing"
        corrected_word = spell.correction(possible_misspelled_word)
        final_output = ""
        if action == "find" or action == "open":
            final_output = corrected_word+" "+file
        elif action == "move" or action == "copy":
            if len(destination) < 1:
                print("could not get destination please try again")
                emily.say("could not get destination please try again")
                emily.runAndWait()
                continue
            final_output = corrected_word+" "+file+" to "+destination


        if action == "find":
            subprocess.Popen(["open", "-R", files.find_file(file)])
        elif action == "open":
            subprocess.Popen(["open", files.find_file(file)])
        elif action == "copy":
            src = files.find_file(file)
            dst = files.find_dir(destination) + os.sep + fs.trimToBackslash(src)
            copyfile(src, dst)
        elif action == "move":
            src = files.find_file(file)
            dst = files.find_dir(destination) + os.sep + fs.trimToBackslash(src)
            move(src, dst)
        emily.say(final_output)
        emily.runAndWait()
        print(final_output)


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
                # print("located noun " + child.text)
                file = child.text
    return [detected, file]


def copy(token, indoc, position):
    # print("possible command", find.similarity(token), token.text)
    detected = token.lemma_
    file = ""
    remaining = ""
    _dir = ""
    sub_position = 0
    for word in indoc[position:]:
        remaining += word.text + " "
    remaining = remaining.strip()
    remaining_doc = nlp(remaining)
    # print([(ent.text, ent.label_) for ent in remaining_doc.ents])
    if len(remaining_doc.ents) > 0:
        for ent in remaining_doc.ents:
            if ent.label_ == "file":
                file = ent.text
                returned_dir = get_dir_text(remaining[remaining.find(file)+len(file)+1:])
                if returned_dir != "none":
                    _dir = returned_dir
                break
    else:
        for child in token.children:
            # print(child, child.dep)
            if child.tag_ == "NN" or child.tag_ == "XX" or child.dep == 416:
                # print("located noun " + child.text)
                file = child.text
                returned_dir = get_dir_text(remaining[remaining.find(file) + len(file) + 1:])
                if returned_dir != "none":
                    _dir = returned_dir
    return [detected, file, _dir]


def get_dir_text(remaining):
    _dir = ""
    beg = ""
    rem_doc = nlp(remaining)
    for token in rem_doc:
        if token.pos_ == "ADP":
            # print("head", token.head.text)
            beg = token.head.text
    if len(beg) < 1:
        return "none"
    starting_position = remaining.find(beg)
    remaining = remaining[starting_position:]
    # print("remaining", remaining)
    rem_doc = nlp(remaining)
    if len(rem_doc.ents) > 0:
        for ent in rem_doc.ents:
            if ent.label_ == "file":
                _dir = ent.text
                break
    else:
        for child in token.children:
            # print(child, child.dep)
            if child.tag_ == "NN" or child.tag_ == "XX" or child.dep == 416:
                # print("located noun " + child.text)
                _dir = child.text
    if len(_dir) < 1:
        _dir = rem_doc[0]
    # print("directory is", _dir)
    return str(_dir)


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
        patterns.append({"label": "file", "pattern": pattern})
    return patterns


start()
