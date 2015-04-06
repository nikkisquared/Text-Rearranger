#!usr/bin/python

"""a program to re-write a long text file based on word topology"""

from __future__ import print_function

import random
import options


def tokenizer(f):
    """Iterator that yields every word from a given open file"""
    for line in f:
        for word in line.split(" "):
            yield word


def get_metadata(cmd, word):
    """Parse out metadata for a word, based on command settings"""

    if not cmd["compare_case"]:
        case = ""
    elif (word.istitle() or (word[0].isupper() and
            sum(1 for c in word if c.isupper()) == 1)):
        case = "title"
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
    """Return the point at which non-word punctuation ends"""
    letter = start
    while (letter < len(word) and letter >= 0 and not word[letter].isalnum()):
        letter += step
    return letter


def parse_punctuation(cmd, word):
    """
    Return the punctuation before the word, the stripped down word,
    and the punctuation after the word
    """
    puncBefore = ""
    puncAfter = ""

    if cmd["soft_truncate_newlines"] or cmd["hard_truncate_newlines"]:
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


def fill_dictionary(cmd, dictionary, filterList, source="source"):
    """
    Fill a dictionary sorted by case, leading letter, and length
    Each word is filtered by its' metadata, which depends on cmd arguments
    Will optionally filter the dictionary as it builds it
    Also returns the count of each word, and total word count
    """

    occurences = {}
    wordCount = 0
    for word in tokenizer(cmd[source]):

        _, word, _ = parse_punctuation(cmd, word)
        # source file should not be filtered except by request
        if (not word or cmd["filter_source"] and
                not check_filter(cmd, filterList, word)):
            continue
        case, letter, length = get_metadata(cmd, word)

        if not dictionary.get(case):
            dictionary[case] = {}
        if not dictionary[case].get(letter):
            dictionary[case][letter] = {}
        if not dictionary[case][letter].get(length):
            dictionary[case][letter][length] = []

        dictionary[case][letter][length].append(word)
        if not occurences.get(word):
            occurences[word] = 0
        occurences[word] += 1
        wordCount += 1

    return occurences, wordCount


def sort_dictionary(cmd, dictionary):
    """Sorts a given dictionary based on commands"""

    uniqueOnly = False
    shuffle = False

    if (cmd["equal_weighting"] or cmd["pure_mode"] and
            (cmd["filter_same"] or cmd["filter_different"])):
        uniqueOnly = True
    if cmd["usage_limited"] and not cmd["block_shuffle"]:
        shuffle = True

    for case in dictionary:
        for letter in dictionary[case]:
            for length in dictionary[case][letter]:
                wordList = dictionary[case][letter][length]
                if uniqueOnly:
                    wordList = list(set(wordList))
                # randomizes words pulled later
                elif shuffle:
                    random.shuffle(wordList)
                dictionary[case][letter][length] = wordList


def check_filter(cmd, filterList, word):
    """
    Check a word against a filter list and filter type
    Return true if word should be used, false otherwise
    """
    if cmd["compare_lower"]:
        word = word.lower()
    found = word in filterList
    if ((cmd["filter_same"] and not found or
        cmd["filter_different"] and found)):
        return False
    return True


def get_filter_list(cmd):
    """Return a formatted filter list of words to compare against"""
    filterList = set([])
    if not (cmd["filter_same"] or cmd["filter_different"]):
        return filterList
    for word in tokenizer(cmd["filter"]):
        _, word, _ = parse_punctuation(cmd, word)
        if cmd["compare_lower"]:
            word = word.lower()
        filterList.add(word)
    return filterList


def search_dictionary(dictionary, level, sort, wordData, indent=0, order=None):
    """Recursively enter each level of a dictionary to find all contents"""

    output = []
    newIndent = indent

    if not order:
        order = dictionary.keys()
        order = sorted(order)

    for section in order:
        if section not in dictionary:
            continue
        if section:
            output.append("%s%s %s" % (
                " " * indent, level[0], section))
            newIndent = indent + 2
        if isinstance(dictionary[section], dict):
            output += search_dictionary(dictionary[section], level[1:], 
                                        sort, wordData, newIndent)
        else:
            wordList = dictionary[section]
            wordList = list(set(wordList))
            if sort:
                wordList = sorted(wordList, key=str.lower)
            for word in wordList:
                line = "%s%s" % (" " * newIndent, word)
                if wordData.get(word):
                    line += " %s" % wordData[word]
                output.append(line)

    return output


def create_word_data(cmd, occurences, wordCount):
    """
    Creates formatted output for 
    """

    wordData = {}
    # percent values need to be float
    wordCount *= 1.0

    for word, count in occurences.items():

        data = "{"
        if cmd["frequency_count"]:
            data += "count: %d" % count
            if cmd["frequency_percent"]:
                data += ", "
        if cmd["frequency_percent"]:
            percent = "frequency: {:." + str(cmd["decimal_accuracy"]) + "%}"
            data += percent.format(count / wordCount)
        data = data.strip()
        data += "}"
        # ie if nothing was added
        if data == "{}":
            data = ""
        wordData[word] = data

    return wordData


def generate_analysis(cmd, dictionary, occurences, wordCount):
    """Generates an analysis of statistics for dictionary findings"""

    output = []
    wordData = create_word_data(cmd, occurences, wordCount)

    order = ["mixed", "upper", "first", "lower", ""]
    level = ["Case", "Letter", "Length"]
    sort = not cmd["block_inspection_sort"]
    output = search_dictionary(dictionary, level, sort, wordData, order=order)
    for line in output:
        cmd["output"].write(line + "\n")


def get_replacement_word(cmd, dictionary, filterList, word):
    """
    Try to get a suitable replacement word
    Return an empty string if no replacement can be found
    """

    case, letter, length = get_metadata(cmd, word)
    wordList = dictionary
    for layer in get_metadata(cmd, word):
        wordList = wordList.get(layer)
        if not wordList:
            return ""
    passedFilter = check_filter(cmd, filterList, word)

    if len(wordList) == 0 or (cmd["pure_mode"] and not passedFilter):
        return ""
    elif passedFilter and (cmd["pure_mode"] or cmd["keep_mode"]):
        return word
    elif cmd["equal_weighting"] or cmd["relative_usage"]:
        roll = random.randint(0, len(wordList) - 1)
        return wordList[roll]
    # falls back on limited usage
    else:
        # popping from the end means less memory usage
        return wordList.pop(-1)


def generate_text(cmd, dictionary, filterList):
    """Rearrange or filter the input text to create a new output"""

    output = []
    line = ""
    for word in tokenizer(cmd["input"]):

        if word == "\n":
            if not cmd["hard_truncate_newlines"]:
                line += "\n"
            continue
        if word == "":
            if not cmd["truncate_whitespace"]:
                line += " "
            continue

        puncBefore, word, puncAfter = parse_punctuation(cmd, word)

        line += puncBefore
        # trying to replace empty words breaks metadata
        if word:
            newWord = get_replacement_word(cmd, dictionary, filterList, word)
            line += newWord
        line += puncAfter
        if newWord and line[-1] != "\n" and not cmd["truncate_whitespace"]:
            line += " "
        else:
            # remove trailing spaces
            output.append(line.replace(" \n", "\n"))
            line = ""

    output.append(line)
    for line in output:
        cmd["output"].write(line)
    # ensures a single newline at the end of the output
    if not cmd["hard_truncate_newlines"]:
        cmd["output"].write("\n")


def main():
    """Handle each section of the program from here"""

    cmd = options.get_command()
    if cmd["random_seed"] != -1:
        random.seed(cmd["random_seed"])

    filterList = get_filter_list(cmd)
    dictionary = {}
    occurences, wordCount = fill_dictionary(cmd, dictionary, filterList)
    sort_dictionary(cmd, dictionary)

    if cmd["inspection_mode"]:
        generate_analysis(cmd, dictionary, occurences, wordCount)
    else:
        generate_text(cmd, dictionary, filterList)

    for f in ("input", "source", "output"):
        cmd[f].close()

main()