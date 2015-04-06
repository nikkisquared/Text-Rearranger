#!usr/bin/python

"""handles parsing program input and file opening"""

from __future__ import print_function

import sys
import os
import argparse

parser = argparse.ArgumentParser(description=
    "Takes a text file to re-write using the contents of itself, or "
    "another file, then writes it back in a random order. Has various "
    "controls to filter output to be topologically similar.")

# supress warnings and notices
parser.add_argument("-w", "--warning-level", type=int,
                    choices=[0, 1, 2, 3], default=2,
                    help="set level of warnings (defaults to 2):\n"
                    "0 - show none\n1 - show only warnings\n"
                    "2 - show warnings and notices\n3 - show notices only")
parser.add_argument("-E", "--explode-on-warning", action="store_true",
                    help="program will now crash on warnings")

# applies optimal settings
parser.add_argument("-d", "--default", action="store_true",
                    help="uses default (optimal) settings, identical to "
                            "running the program with -Clcnup")

# case and leading letter sorting
parser.add_argument("-C", "--compare-case", action="store_true",
                    help="makes replacement words match case style, "
                        "which mostly implies and overpowers -c")
parser.add_argument("-l", "--first-letter", action="store_true",
                    help="requires first letter of a replacement word to be "
                        "the same (case-insensitive without -c)")
parser.add_argument("-c", "--case-sensitive", action="store_true",
                    help="makes -f case-sensitive, does nothing without -f")

# length comparison sorting (what else to add?)
parser.add_argument("-n", "--length-check", action="store_true",
                    help="requires length of a replacement word to be equal")

# algorithms for determining what words are rearranged with
parser.add_argument("-u", "--usage-limited", action="store_true",
                    help="usage of each word is limited to the number of "
                        "occurrences in the original text")
parser.add_argument("-b", "--block-shuffle", action="store_true",
                    help="replacement words will not be shuffled, "
                        "but only works with -u")
parser.add_argument("-r", "--relative-usage", action="store_true",
                    help="word usage will be based on relative frequency, "
                        "but conflicts with and overrides -u, and also falls "
                        "back on this if none of -u, -r, or -e are used")
parser.add_argument("-e", "--equal-weighting", action="store_true",
                    help="forces equal weighting of every word, "
                        "but conflicts with and overrides -u and -r")
parser.add_argument("-m", "--map-words", action="store_true",
                    help="WIP")
parser.add_argument("-R", "--random-seed", type=int, default=-1,
                    help="seeds random with given number")

# punctuation sorting and whitespace handling
parser.add_argument("-p", "--preserve-punctuation", action="store_true",
                    help="perfectly preserves all non-word punctuation if "
                        "defined, treats punctuation as letters otherwise")
parser.add_argument("-t", "--soft-truncate-newlines", action="store_true",
                    help="newlines at the end of lines are removed")
parser.add_argument("-T", "--hard-truncate-newlines", action="store_true",
                    help="all newlines are removed completely")
parser.add_argument("-W", "--truncate-whitespace", action="store_true",
                    help="all whitespace between words will be removed")

# input/output redirection
parser.add_argument("-i", "--input", type=str, default=sys.stdin,
                    help="define an existing input file to re-arrange "
                        "instead of falling back on standard input")
parser.add_argument("-s", "--source", type=str, default=None,
                    help="define an existing source file to pull words from "
                        "for rearranging, but defaults to input if undefined")
parser.add_argument("-f", "--filter", type=str, default=None,
                    help="define an existing filter file to compare "
                        "against for selectively acting on words, and "
                        "is only required for filter modes")
parser.add_argument("-o", "--output", type=str, default=sys.stdout,
                    help="define an output file instead of falling back on "
                        "standard output")
parser.add_argument("-O", "--overwrite", action="store_true",
                    help="automatically overwrites the output file")

# inspection mode and output options
parser.add_argument("-I", "--inspection-mode", action="store_true",
                    help="turns on inspection mode, which will "
                        "output how it arranges its text storage")
parser.add_argument("-B", "--block-inspection-sort", action="store_true",
                    help="leaves inspection data order unsorted")
parser.add_argument("-q", "--frequency-count", action="store_true",
                    help="displays number of occurences of word")
parser.add_argument("-Q", "--frequency-percent", action="store_true",
                    help="displays overall percent frequency of word")
parser.add_argument("-A", "--decimal-accuracy", type=int, default=2,
                    help="defines number of decimals to use for -Q, "
                        "defaults to 2")

# filter mode, filters, filter organization
parser.add_argument("-K", "--keep-mode", action="store_true",
                    help="turns on keep filter mode, which keeps words not "
                        "matching the filter, and rearranges others")
parser.add_argument("-P", "--pure-mode", action="store_true",
                    help="turns on pure filter mode, meaning no words will "
                        "be rearranged, but selectively filtered out")
parser.add_argument("-S", "--filter-same", action="store_true",
                    help="rearranges/filters only words found in source")
parser.add_argument("-D", "--filter-different", action="store_true",
                    help="rearranges/filters only words not found in source")
parser.add_argument("-L", "--compare-lower", action="store_true",
                    help="filter file comparisons ignore case")
parser.add_argument("-F", "--filter-source", action="store_true",
                    help="filters the source files' internal storage")


def print_msgs(cmd, msgs):
    """
    Selectively prints warnings and notices
    Can crash on warnings if user desires
    """
    for m in msgs:
        if "NOTICE" in m and cmd["warning_level"] in (0, 1):
            continue
        elif "WARNING" in m:
            if cmd["explode_on_warning"]:
                print(m)
                sys.exit("Program set to crash on WARNING.")
            elif cmd["warning_level"] in (0, 3):
                continue
        print(m)


def open_file(fType, fName, comparison):
    """
    Open a file stream and return a pointer to it
    Exit the program with a message on a critical error
    """
    if not fName:
        return fName
    elif not os.path.isfile(fName):
        sys.exit("ERROR: %s file \"%s\" does not exist." % (fType, fName))
    elif fName == comparison:
        sys.exit("ERROR: output and %s are both the same file \"%s\"." % (
            fType, comparison))
    else:
        return open(fName, 'r')


def get_command():
    """
    Parse and updates CLI arguments and return a dict of them
    Check input files and file settings
    """

    cmd = vars(parser.parse_args())

    defaults = ["first_letter", "case_sensitive", "compare_case",
                "length_check", "usage_limited", "preserve_punctuation"]
    if cmd["default"]:
        for arg in defaults:
            cmd[arg] = True

    msgs = validate_command(cmd)
    print_msgs(cmd, msgs)
    msgs = validate_files(cmd)
    print_msgs(cmd, msgs)

    for fType in ("input", "source", "filter"):
        if not isinstance(cmd[fType], file):
            cmd[fType] = open_file(fType, cmd[fType], cmd["output"])

    return cmd


def validate_files(cmd):
    """
    Check cmd for invalid or conflicting file input
    Return notices and warnings
    Exit on fatally unmanageable input
    """
    msgs = []

    if not cmd["source"]:
        cmd["source"] = cmd["input"]
        msgs.append("NOTICE: source will be the same as input.")

    # [module] -f"..." (without -S or -D)
    if cmd["filter"]:
        if not (cmd["filter_same"] or cmd["filter_different"]):
            msgs.append("WARNING: A filter file does nothing without using "
                        "a filter, -S or -D.")
        elif cmd["filter"] == cmd["input"]:
            sys.exit("ERROR: filter and input files are the same.")
    # [module] -S or -D (without -f "...")
    elif not cmd["filter"] and (cmd["filter_same"] or cmd["filter_different"]):
        if cmd["source"] != cmd["input"]:
            cmd["filter"] = cmd["source"]
            msgs.append("NOTICE: filter file will be the source file.")
        else:
            sys.exit("ERROR: You can't use a filter, -S or -D, without a "
                    "filter file, and it can't be source as it is the "
                    "same as input.")

    # check output file settings, and try to open it
    query = "%s already exists. Overwrite? Y/N\n"
    if cmd["output"] != sys.stdout:
        if os.path.isfile(cmd["output"]): 
            if cmd["overwrite"]:
                msgs.append("NOTICE: Automatically overwriting %s." % 
                    cmd["output"])
            elif not raw_input(query % cmd["output"]).startswith("Y"):
                sys.exit("Terminating. Rename your file or output parameter.")
        cmd["output"] = open(cmd["output"], 'w')

    return msgs


def validate_command(cmd):
    """
    Check cmd for invalid or conflicting input
    Return notices and warnings on
    """
    msg = []

    # [module] -E -w (0 or 3)
    if cmd["explode_on_warning"] and (cmd["warning_level"] in (0, 3)):
        msg.append("WARNING: Program set to crash on warnings, but warnings "
                    "have been hidden. Only one option should be set.")

    # [module] -c (without -l)
    if cmd["case_sensitive"] and not cmd["first_letter"]:
        msg.append("NOTICE: Using -c does nothing without -l.")

    # [module] -b (without -u)
    if cmd["block_shuffle"] and not cmd["usage_limited"]:
        msg.append("NOTICE: Using -b does nothing without -u.")

    # [module] -u -e, -r -e, or -u -r -e
    if cmd["equal_weighting"]:
        if cmd["usage_limited"] or cmd["relative_usage"]:
            msg.append("WARNING: -e overrides -u and -r, but you used two "
                    "of them.")
    # [module] -u -r
    elif cmd["usage_limited"] and cmd["relative_usage"]:
        msg.append("WARNING: -r overrides -u, but you used both.")
    # [module] (without -u, -r, or -e, and not -I or -P)
    elif (not cmd["usage_limited"] and
            not (cmd["inspection_mode"] or cmd["pure_mode"])):
        msg.append("NOTICE: Falling back on relative usage mode, since "
                    "none of -u, -r, or -e were used.")
        cmd["relative_usage"] = True

    # [module] -t -T
    if cmd["soft_truncate_newlines"] and cmd["hard_truncate_newlines"]:
        msg.append("NOTICE: You used both -t and -T, but -T implies -t.")

    # [module] -s source.txt -u
    if (cmd["source"] and cmd["usage_limited"] and
            cmd["input"] != cmd["source"]):
        msg.append("WARNING: You are using a custom source with usage "
                    "limiting on, so the output might be truncated.")

    # [module] -B (without -I)
    if cmd["block_inspection_sort"] and not cmd["inspection_mode"]:
        msg.append("NOTICE: -B does nothing without -I.")
    # [module] -q or -Q (without -I)
    if (not cmd["inspection_mode"] and
            (cmd["frequency_count"] or cmd["frequency_percent"])):
        msg.append("NOTICE: -q and -Q do nothing without -I.")
    # [module] -A [x] (without -Q)
    if cmd["decimal_accuracy"] != 2 and not cmd["frequency_percent"]:
        msg.append("NOTICE: -A effects only -Q, but you didn't call it.")
    # [module] -I -S or -D (without -F)
    if (cmd["inspection_mode"] and not cmd["filter_source"] and
            (cmd["filter_same"] or cmd["filter_different"])):
        msg.append("NOTICE: -I with -S or -D requires the -F flag, so "
                    "it will be set for you.")
        cmd["filter_source"] = True

    # [module] -s "..." -P
    if cmd["pure_mode"] and cmd["source"]:
        msg.append("WARNING: You defined a source, but with -P the source "
                    "will not be used for anything.")
    # [module] -I -P
    if cmd["inspection_mode"] and cmd["pure_mode"]:
        msg.append("WARNING: -P should not be used with -I. Results are "
                    "undefined and may be undesired.")
    # [module] -K -P
    if cmd["keep_mode"] and cmd["pure_mode"]:
        msg.append("WARNING: Filter modes -K and -P are oppositional, "
                    "but you used both. Results are undefined.")
    # [module] -S -D
    if cmd["filter_same"] and cmd["filter_different"]:
        msg.append("WARNING: Filters -S and -D are oppositional, "
                    "but you used both. Results are undefined.")
    # [module] -P -F
    if cmd["filter_source"] and cmd["pure_mode"]:
        msg.append("NOTICE: -F does nothing in -P mode.")

    return msg