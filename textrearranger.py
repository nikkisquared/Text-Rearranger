#!usr/bin/python

# a program to re-write a long text file based on word topology

import random
import options


def tokenizer(f):
    """Iterator that yields every word from a given open file"""
    for line in f:
        for word in line.split(" "):
            yield word


def get_metadata(cmd, word):
    """Parses out metadata for a word, based on command settings"""

    if not cmd["compare_case"]:
        case = ""
    elif word.istitle():
        case = "first"
    elif word.islower():
        case = "lower"
    elif word.isupper():
        case = "upper"
    else:
        case = "mixed"

    if cmd["first_letter"] and len(word) >= 1:
        letter = word[0]
        if not cmd["case_sensitive"]:
            letter = letter.lower()
    else:
        letter = ""

    if cmd["length_check"]:
        length = len(word)
    else:
        length = 0

    return case, letter, length


def get_punctuation_point(word, start, step):
    """Returns the point at which non-word punctuation ends"""
    letter = start
    while (letter < len(word) and letter >= 0 and not word[letter].isalnum()):
        letter += step
    return letter


def parse_punctuation(cmd, word):
    """
    Returns the punctuation before the word, the stripped down word,
    and the punctuation after the word
    """
    puncBefore = ""
    puncAfter = ""

    if cmd["truncate_newlines"]:
        word = word.strip()
    if cmd["preserve_punctuation"]:
        cutoff = get_punctuation_point(word, 0, 1)
        puncBefore = word[:cutoff]
        word = word[cutoff:]

        cutoff = get_punctuation_point(word, len(word) - 1, -1)
        # the last letter is the default target
        cutoff += 1
        puncAfter = word[cutoff:]
        word = word[:cutoff]
    # split newlines from word
    elif word:
        if word[-1] == "\n":
            word = word[:-1]
            puncAfter = "\n"

    return puncBefore, word, puncAfter

def build_dictionary(cmd):
    """
    Builds a dictionary sorted by case, leading letter, and length
    Each word is filtered by its' metadata, which depends on cmd arguments
    """

    dictionary = {}

    for word in tokenizer(cmd["source"]):

        _, word, _ = parse_punctuation(cmd, word)
        # sometimes there will only be punctuation
        if not word:
            continue
        case, letter, length = get_metadata(cmd, word)

        if not dictionary.get(case):
            dictionary[case] = {}
        if not dictionary[case].get(letter):
            dictionary[case][letter] = {}
        if not dictionary[case][letter].get(length):
            dictionary[case][letter][length] = []

        dictionary[case][letter][length].append(word)

    return dictionary


def shuffle_dictionary(cmd, dictionary):
    """Shuffles a given dictionary based on commands"""

    for case in dictionary:
        for letter in dictionary[case]:
            for length in dictionary[case][letter]:
                wordList = dictionary[case][letter][length]
                if (cmd["equal_weighting"] or cmd["filter_mode"] and
                    (cmd["keep_same"] or cmd["keep_different"])):
                    wordList = list(set(wordList))
                # randomizes words pulled
                elif cmd["usage_limited"] and not cmd["block_shuffle"]:
                    random.shuffle(wordList)
                dictionary[case][letter][length] = wordList


def get_replacement_word(cmd, dictionary, word):
    """
    Tries to get a suitable replacement word, and return it
    Returns an empty string if no replacement can be found
    """

    case, letter, length = get_metadata(cmd, word)
    wordList = dictionary
    for layer in get_metadata(cmd, word):
        wordList = wordList.get(layer)
        if not wordList:
            return ""
    found = word in wordList

    if (len(wordList) == 0 or 
        cmd["keep_same"] and not found or
        cmd["keep_different"] and found):
        return ""
    elif cmd["filter_mode"] and (cmd["keep_same"] or cmd["keep_different"]):
        return word
    elif cmd["equal_weighting"] or cmd["relative_usage"]:
        roll = random.randint(0, len(wordList) - 1)
        return wordList[roll]
    # falls back on limited usage
    else:
        return wordList.pop(-1)


def generate_text(cmd, dictionary):
    """Fits back together the input text"""

    output = []
    line = ""
    for word in tokenizer(cmd["input"]):

        if word == "\n":
            line += "\n"
            continue
        if word == "":
            line += " "
            continue

        puncBefore, word, puncAfter = parse_punctuation(cmd, word)

        line += puncBefore
        # trying to replace empty words breaks metadata
        if word:
            newWord = get_replacement_word(cmd, dictionary, word)
            line += newWord
        line += puncAfter
        if newWord and line and line[-1] != "\n":
            line += " "
        else:
            output.append(line)
            line = ""

    output.append(line + "\n")
    for line in output:
        cmd["output"].write(line)


def print_dictionary(dictionary):
    """Prints every layered word in the dictionary"""

    for case in dictionary:
        print "combing through case \"%s\"" % case
        for letter in dictionary[case]:
            print "  combing through letter \"%s\"" % letter
            for length in dictionary[case][letter]:
                print "    combing through length %s" % length
                for word in dictionary[case][letter][length]:
                    print "      %s" % word


def main():
    """Handles each section of the program from here"""

    cmd = options.get_command()
    if cmd["random_seed"] != -1:
        random.seed(cmd["seed"])

    dictionary = build_dictionary(cmd)
    shuffle_dictionary(cmd, dictionary)
    # print_dictionary(dictionary)
    generate_text(cmd, dictionary)
    for f in ("input", "source", "output"):
        cmd[f].close()

main()