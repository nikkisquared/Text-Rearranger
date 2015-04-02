#!usr/bin/python

"""handles parsing program input and file opening"""

from __future__ import print_function

import sys
import os
import argparse

parser = argparse.ArgumentParser(description=(
        "Takes a text file to re-write using the contents of itself, or "
        "another file, then writes it back in a random order. Has various "
        "controls to filter output to be topologically similar."))

# applies optimal settings
parser.add_argument("-d", "--default", action="store_true",
                    help=("uses default (optimal) settings, identical to "
                            "running the program with -Clcnup"))

# case and leading letter sorting
parser.add_argument("-l", "--first-letter", action="store_true",
                    help=("requires first letter of a replacement word to be "
                        "the same (case-insensitive without -c)"))
parser.add_argument("-c", "--case-sensitive", action="store_true",
                    help="makes -f case-sensitive, does nothing without -f")
parser.add_argument("-C", "--compare-case", action="store_true",
                    help=("makes replacement words match case style, "
                        "which mostly implies and overpowers -c"))

# length comparison sorting (what else to add?)
parser.add_argument("-n", "--length-check", action="store_true",
                    help="requires length of a replacement word to be equal")

# algorithms for determining what words are rearranged with
parser.add_argument("-u", "--usage-limited", action="store_true",
                    help=("usage of each word is limited to the number of "
                        "occurrences in the original text"))
parser.add_argument("-r", "--relative-usage", action="store_true",
                    help=("word usage will be based on relative frequency, "
                        "but conflicts with and overrides -u, and also falls "
                        "back on this if none of -u, -r, or -e are called"))
parser.add_argument("-e", "--equal-weighting", action="store_true",
                    help=("forces equal weighting of every word, "
                        "but conflicts with and overrides -u and -r"))
parser.add_argument("-b", "--block-shuffle", action="store_true",
                    help=("replacement words will not be shuffled, "
                        "but only works with -u"))
parser.add_argument("-R", "--random-seed", type=int, default=-1,
                    help="seeds random with given number")

# punctuation sorting and handling
parser.add_argument("-p", "--preserve-punctuation", action="store_true",
                    help=("perfectly preserves all non-word punctuation if "
                        "defined, treats punctuation as letters otherwise"))
parser.add_argument("-t", "--truncate-newlines", action="store_true",
                    help="newlines at the end of lines are removed")

# input/output redirection
parser.add_argument("-i", "--input", type=str, default=sys.stdin,
                    help=("define an existing input file to re-arrange "
                        "instead of falling back on standard input"))
parser.add_argument("-s", "--source", type=str, default=None,
                    help=("define an existing source file to pull words from "
                        "for rearranging, but falls back on input"))
parser.add_argument("-f", "--filter", type=str, default=None,
                    help=("define an existing filter file to compare "
                        "against for selectively acting on words, and "
                        "is absolutely required for filter modes"))
parser.add_argument("-o", "--output", type=str, default=sys.stdout,
                    help=("define an output file instead of falling back on "
                        "standard output"))
parser.add_argument("-O", "--overwrite", action="store_true",
                    help="automatically overwrites the output file")

# inspection mode and output options
parser.add_argument("-I", "--inspection-mode", action="store_true",
                    help=("turns on inspection mode, which will "
                        "output how it arranges its text storage"))
parser.add_argument("-B", "--block-inspection-sort", action="store_true",
                    help="leaves inspection data order unsorted")

# filter mode, filters, filter organization
parser.add_argument("-P", "--pure-filter", action="store_true",
                    help="turns on pure filter mode, meaning no words will "
                        "be rearranged, but selectively filtered out")
parser.add_argument("-S", "--keep-same", action="store_true",
                    help="replaces/keeps only words found in source")
parser.add_argument("-D", "--keep-different", action="store_true",
                    help="replaces/keeps only words not found in source")


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


def get_command(validate=True):
    """
    Parse and updates CLI arguments into a dict
    Check input files and file settings
    Optionally check for warnings on other arguments
    """

    cmd = vars(parser.parse_args())

    defaults = ["first_letter", "case_sensitive", "compare_case",
                "length_check", "usage_limited", "preserve_punctuation"]
    if cmd["default"]:
        for arg in defaults:
            cmd[arg] = True

    if validate:
        validate_command(cmd)

    validate_files(cmd)
    for fType in ("input", "source", "filter"):
        if not isinstance(cmd[fType], file):
            cmd[fType] = open_file(fType, cmd[fType], cmd["output"])

    return cmd


def validate_files(cmd):
    """
    Check cmd for invalid or conflicting file input
    Exit on fatally unmanageable input
    """

    if not cmd["source"]:
        cmd["source"] = cmd["input"]
        print("NOTICE: source will be the same as input.")

    # [module] -F "..." (without -S or -D)
    if cmd["filter"]:
        if not (cmd["keep_same"] or cmd["keep_different"]):
            sys.exit("ERROR: You can't use a filter file without using a "
                    "filter, -S or -D.")
        elif cmd["filter"] == cmd["input"]:
            sys.exit("ERROR: filter and input files are the same.")
    # [module] -S or -D (without -F "...")
    elif not cmd["filter"] and (cmd["keep_same"] or cmd["keep_different"]):
        if cmd["source"] != cmd["input"]:
            cmd["filter"] = cmd["source"]
            print("NOTICE: filter file will use source file.")
        else:
            sys.exit("ERROR: You can't use a filter, -S or -D, without a "
                    "filter file, and it can't be source because it is "
                    "the same as input.")

    # check output file settings, and try to open it
    query = "%s already exists. Overwrite? Y/N\n"
    if cmd["output"] != sys.stdout:
        if os.path.isfile(cmd["output"]): 
            if cmd["overwrite"]:
                print("Automatically overwriting %s." % cmd["output"])
            elif not raw_input(query % cmd["output"]).startswith("Y"):
                sys.exit("Terminating. Rename your file or output parameter.")
        cmd["output"] = open(cmd["output"], 'w')


def validate_command(cmd):
    """
    Check cmd for invalid or conflicting input
    Print warnings for possibly confusing results
    """

    # [module] -c (without -l)
    if cmd["case_sensitive"] and not cmd["first_letter"]:
        print("NOTICE: using -c does nothing without -l.")

    # [module] -b (without -u)
    if cmd["block_shuffle"] and not cmd["usage_limited"]:
        print("NOTICE: using -b does nothing without -u.")

    # [module] -u -e, -r -e, or -u -r -e
    if cmd["equal_weighting"]:
        if cmd["usage_limited"] or cmd["relative_usage"]:
            print("WARNING: -e overrides -u and -r, but you used two of them.")
    # [module] -u -r
    elif cmd["usage_limited"] and cmd["relative_usage"]:
        print("WARNING: -r overrides -u, but you used both.")
    # [module] (without -u, -r, or -e, and not -I or -P)
    elif (not cmd["usage_limited"] and
            not (cmd["inspection_mode"] or cmd["pure_filter"])):
        print("WARNING: falling back on relative usage mode, since none of "
                "-u, -r, or -e were defined.")
        cmd["relative_usage"] = True

    # [module] -s source.txt -u
    if (cmd["source"] and cmd["usage_limited"] and
            cmd["input"] != cmd["source"]):
        print("WARNING: you are using a custom source with usage limiting "
                "on, so the output might get truncated.")

    # [module] -I -P
    if cmd["inspection_mode"] and cmd["pure_filter"]:
        print("WARNING: -P should not be used with -I, results undefined.")

    # [module] -s "..." -P
    if cmd["pure_filter"] and cmd["source"]:
        print("WARNING: You defined a source, but with -P the source will "
                "not be used for anything.")

    # [module] -S -D
    if cmd["keep_same"] and cmd["keep_different"]:
        print("WARNING: Filters -S and -D conflict and are opposites, "
                "but you used both. Neither will be used.")
        cmd["keep_same"] = False
        cmd["keep_different"] = False
        # sets this to false too just in case it's on
        cmd["pure_filter"] = False