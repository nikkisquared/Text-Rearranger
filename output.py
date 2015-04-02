


def search_dictionary(dictionary, level, sort, indent=0, order=None):
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
                                        sort, newIndent)
        else:
            wordList = dictionary[section]
            wordList = list(set(wordList))
            if sort:
                wordList = sorted(wordList, key=str.lower)
            for word in wordList:
                output.append("%s%s" % (" " * newIndent, word))

    return output


def generate_analysis(cmd, dictionary):
    """Generates an analysis of statistics for dictionary findings"""

    output = []

    order = ["mixed", "upper", "first", "lower", ""]
    level = ["Case", "Letter", "Length"]
    sort = not cmd["block_inspection_sort"]
    output = search_dictionary(dictionary, level, sort, order=order)
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

    if len(wordList) == 0 or not check_filter(cmd, filterList, word):
        return ""
    elif cmd["pure_filter"]:
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
            line += "\n"
            continue
        if word == "":
            line += " "
            continue

        puncBefore, word, puncAfter = parse_punctuation(cmd, word)

        line += puncBefore
        # trying to replace empty words breaks metadata
        if word:
            newWord = get_replacement_word(cmd, dictionary, filterList, word)
            line += newWord
        line += puncAfter
        if newWord and line[-1] != "\n":
            line += " "
        else:
            # remove trailing spaces
            output.append(line.replace(" \n", "\n"))
            line = ""

    output.append(line + "\n")
    for line in output:
        cmd["output"].write(line)