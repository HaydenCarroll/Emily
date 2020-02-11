import os
import sys
import time
import getpass
from pyjarowinkler import distance
from tqdm import tqdm
from multiprocessing.dummy import Pool as ThreadPool


class FileSystem:
    file_list = []
    current_os = None

    def __init__(self):
        dir_path = None
        if sys.platform == "darwin":
            dir_path = "/Users/" + getpass.getuser()
            self.current_os = "OSX"
        elif sys.platform == "linux" or sys.platform == "linux2":
            dir_path = root_path() + "\\" +getpass.getuser()
            self.current_os = "linux"
        elif sys.platform == "win32":
            dir_path = root_path() + "\\Users\\" + getpass.getuser()
            self.current_os = "windows"
        else:
            print("Sorry this operating system is not supported")
            exit(1)
        print("Current OS:", self.current_os, "Current user:", getpass.getuser())
        start_time = time.time()
        print("Gathering files please wait...")
        if self.current_os == "OSX":
            self.file_list = get_all_files_mac(dir_path)
        elif self.current_os == "linux":
            self.file_list = get_all_files_linux(dir_path)
        elif self.current_os == "windows":
            self.file_list = get_all_files_win(dir_path)
        else:
            print("Error retrieving files")
            exit(2)
        print("total time ", time.time() - start_time)
        print("total number of files found", len(self.file_list))

    def get_files(self):
        return self.file_list

    def get_file_terms(self):
        file_terms = []
        for f in self.file_list:
            trimmed = trimToBackslash(f)
            final_term = remove_extensions(trimmed)
            file_terms.append(final_term)
        return file_terms

    def get_file_word_spellings(self):
        words = []
        for f in tqdm(self.file_list):
            trimmed = trimToBackslash(f)
            extensions_removed = remove_extensions(trimmed)
            split_names = extensions_removed.split(" ")
            for s in split_names:
                if len(s) > 15 or len(s) < 3:
                    continue
                if s == " ":
                    continue
                if str(s).isnumeric():
                    continue
                if s in words:
                    continue
                words.append(s)
                # print("adding", s)
        return words

    def find_file(self, file_to_find):
        ranked_files = []
        hasRefinedList = False
        refinedList = []
        file_to_find_no_extention = remove_extensions(file_to_find).lower()
        # for exact matches
        for f in self.file_list:
            trimmed = trimToBackslash(f).lower()
            final_file_name = remove_extensions(trimmed).lower()
            if file_to_find_no_extention == final_file_name:
                # prioritizing app matches on osx
                if self.current_os == "OSX":
                    if trimmed.endswith(".app"):
                        sa = [f, 2]
                        refinedList.append(sa)
                        continue
                dist = distance.get_jaro_distance(file_to_find, trimmed,
                                                    winkler=True, scaling=0.1)
                if dist < 0.7:
                    continue
                sa = [f, dist]
                # sa = [f, 1.0]
                refinedList.append(sa)
                hasRefinedList = True
        if hasRefinedList:
            ranked_files = refinedList
        else:
            for f in self.file_list:
                trimmed = trimToBackslash(f)
                # prioritizing app matches on osx
                if self.current_os == "OSX":
                    if trimmed.endswith(".app"):
                        sa = [f, 2]
                        refinedList.append(sa)
                        continue
                # sa = {f, jaro_winkler_score(file_to_find, trimToBackslash(f)) + ""}

                dist = distance.get_jaro_distance(file_to_find, trimmed,
                                                  winkler=True, scaling=0.1)
                if dist < 0.7:
                    continue
                sa = [f, dist]
                ranked_files.append(sa)
        ranked_files.sort(key=sortSecond, reverse=True)
        count = 0
        # for toup in ranked_files:
        #     print(toup[0],toup[1])
        topFile = ranked_files[0][0]
        topFileSet = False

        for k in ranked_files:
            if count >= 50 or topFileSet:
                break
            if not topFileSet:
                is_correct = requestCorrect(k[0])
                if is_correct:
                    topFile = k[0]
                    topFileSet = True
                    continue
            #print(k[0], "Score:", k[1])
            count = count + 1

        #print("Top file:", topFile)
        return topFile


def root_path():
    return os.path.abspath(os.sep)


def get_sys_exec_root_or_drive():
    path = sys.executable
    while os.path.split(path)[1]:
        path = os.path.split(path)[0]
    return path


# gets files from Program Files, Program Files (x86), and from <current drive>\<current user>
def get_all_files_win(dir_path):
    file_list = []
    pf86 = root_path()+"\\Program Files (x86)"
    pf = root_path()+"\\Program Files"

    for root, dirs, files in os.walk(pf86):
        for file in files:
            file_list.append(os.path.join(root, file))

    for root, dirs, files in os.walk(pf):
        for file in files:
            file_list.append(os.path.join(root, file))

    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


# Gets files from Applications and from user files
def get_all_files_mac(dir_path):
    file_list = []

    for dir in next(os.walk("/Applications"))[1]:
        file_list.append("/Applications/"+dir)
    for root, dirs, files in os.walk(dir_path):
        for dir in dirs:
            if dir.endswith(".app"):
                file_list.append(os.path.join(root, dir))
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


# gets files from /home/<current user>
def get_all_files_linux(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def jaro_winkler_score(aString1, aString2):
    return 1.0 - proximity(aString1, aString2)

mWeightThreshold = 0.7
mNumChars = 2
def proximity(aString1, aString2):
    lLen1 = len(aString1)
    lLen2 = len(aString2)
    if lLen1 == 0:
        if lLen2 == 0:
            return 1.0
        else:
            return 0.0

    lSearchRange = max(0, max(lLen1, lLen2) / 2 - 1)

    # default initialized to false
    lMatched1 = []
    lMatched2 = []

    lNumCommon = 0
    for i in range(lLen1):
        lStart = max(0, i - lSearchRange)
        lEnd = int(min(i + lSearchRange + 1, lLen2))
        print(str(lStart))
        print(str(lEnd))
        for j in range(lStart, lEnd, 1):
            if lMatched2[j]:
                continue
            if aString1[i] != aString2[j]:
                continue
            lMatched1[i] = True
            lMatched2[j] = True
            lNumCommon = lNumCommon + 1
            break

    if lNumCommon == 0:
        return 0.0

    lNumHalfTransposed = 0
    k = 0
    for i in range(lLen1):
        if not lMatched1[i]:
            continue
        while not lMatched2[k]:
            k = k + 1
        if aString1[i] != aString2[k]:
            lNumHalfTransposed = lNumHalfTransposed + 1
        k = k + 1

    lNumTransposed = lNumHalfTransposed / 2;


    lNumCommonD = lNumCommon;
    lWeight = (lNumCommonD / lLen1 + lNumCommonD / lLen2 +
               (lNumCommon - lNumTransposed) / lNumCommonD) / 3.0

    if lWeight <= mWeightThreshold:
        return lWeight
    lMax = min(mNumChars, min(len(aString1)), len(aString2))
    lPos = 0;
    while lPos < lMax and aString1[lPos] == aString2[lPos]:
        lPos = lPos + 1
    if lPos == 0:
        return lWeight
    return lWeight + 0.1 * lPos * (1.0 - lWeight)


def trimToBackslash(s):
    strings = s.split(os.sep)
    if len(strings) < 2:
        return s
    return strings[-1]


def sortSecond(val):
    return val[1]


def requestCorrect(var):
    print("is this the file you want?", var, "[y/n]")
    response = input()
    if response == 'y':
        return True
    if response == 'n':
        return False
    else:
        print("incorrect format returning false")
        return False


def remove_extensions(var):
    split_var = var.split('.')
    return split_var[0]
