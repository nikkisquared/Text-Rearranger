#!usr/bin/python

# handles parsing program inputs

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
                            "running the program with -Cfclup"))

# flags for fine tuning how the program works

parser.add_argument("-f", "--first-letter", action="store_true",
                    help=("requires first letter of a replacement word to be "
                        "the same (case-insensitive without -c)"))
parser.add_argument("-c", "--case-sensitive", action="store_true",
                    help="makes -f case-sensitive, does nothing without -f")
parser.add_argument("-C", "--compare-case", action="store_true",
                    help=("makes replacement words match case style, "
                        "which mostly implies and overpowers -c"))

parser.add_argument("-l", "--length-check", action="store_true",
                    help="requires length of a replacement word to be equal")

parser.add_argument("-u", "--usage-limited", action="store_true",
                    help=("usage of each word is limited to the number of "
                        "occurrences in the original text"))
parser.add_argument("-B", "--block-shuffle", action="store_true",
                    help=("replacement words will not be shuffled, "
                        "but only works with -u"))
parser.add_argument("-r", "--relative-usage", action="store_true",
                    help=("word usage will be based on relative frequency, "
                        "but conflicts with and overrides -u, and also falls "
                        "back on this if none of -u, -r, or -e are called"))
parser.add_argument("-e", "--equal-weighting", action="store_true",
                    help=("forces equal weighting of every word, "
                        "but conflicts with and overrides -u and -r"))

parser.add_argument("-p", "--preserve-punctuation", action="store_true",
                    help=("perfectly preserves all non-word punctuation if "
                        "defined, treats punctuation as letters otherwise"))
parser.add_argument("-t", "--truncate-newlines", action="store_true",
                    help="newlines at the end of lines are removed")

parser.add_argument("-R", "--random-seed", type=int, default=-1,
                    help="seeds random with given number")

# input/output redirection
parser.add_argument("-i", "--input", type=str, default=sys.stdin,
                    help=("define an existing input file to re-arrange "
                        "instead of falling back on standard input"))
parser.add_argument("-s", "--source", type=str, default=None,
                    help=("define an existing source file "
                        "to pull words from for rearranging"))
parser.add_argument("-o", "--output", type=str, default=sys.stdout,
                    help=("define an output file instead of falling back on "
                        "standard output"))
parser.add_argument("-O", "--overwrite", action="store_true",
                    help="automatically overwrites the output file")

# radically different use modes
parser.add_argument("-F", "--filter-mode", action="store_true",
                    help="turns on filter mode only, meaning no words will "
                        "be rearranged, to focus on special cases")
parser.add_argument("-S", "--keep-same", action="store_true",
                    help="replaces/keeps only words found in source")
parser.add_argument("-D", "--keep-different", action="store_true",
                    help="replaces/keeps only words not found in source")


def get_command(validate=True):
    """
    Parses and updates CLI arguments into a dict
    If wanted or not defined, it calls the validation function
    """

    cmd = vars(parser.parse_args())

    defaults = ["first_letter", "case_sensitive", "compare_case",
                "length_check", "usage_limited", "preserve_punctuation"]
    if cmd["default"]:
        for arg in defaults:
            cmd[arg] = True

    if validate:
        validate_command(cmd)

    # tries to open input and source files, if defined
    for fName in ("input", "source"):
        if not isinstance(cmd[fName], file):
            cmd[fName] = open_file(fName, cmd[fName], cmd["output"])

    return cmd


def open_file(fType, fName, comparison):
    """
    Tries to open a given file
    Exits the program with a message on a critical error
    Returns an open file stream otherwise
    """

    if not os.path.isfile(fName):
        sys.exit("ERROR: %s file \"%s\" does not exist." % (fType, fName))
    elif fName == comparison:
        sys.exit("ERROR: output and %s are both the same file \"%s\"." % (
            fType, comparison))
    else:
        return open(fName, 'r')


def validate_command(cmd):
    """
    Checks cmd for invalid or conflicting input
    May stop the program at specific points if user chooses to
    Prints warnings for possibly confusing results
    """

    # [module] -S -D
    if cmd["keep_same"] and cmd["keep_different"]:
        sys.exit("ERROR: Filter modes -S and -D conflict, but you used both.")

    if cmd["source"] == None:
        if cmd["keep_same"] or cmd["keep_different"]:
            sys.exit("ERROR: You can't use a filter mode, -S or -D, without "
                "a unique source file.")
        cmd["source"] = cmd["input"]

    query = "%s already exists. Overwrite? Y/N\n"
    if cmd["output"] != sys.stdout:
        if os.path.isfile(cmd["output"]): 
            if cmd["overwrite"]:
                print "Automatically overwriting %s." % cmd["output"]
            elif not raw_input(query % cmd["output"]).startswith("Y"):
                sys.exit("Terminating. Rename your file or output parameter.")
        cmd["output"] = open(cmd["output"], 'w')

    # [module] -s source.txt -u
    if cmd["input"] != cmd["source"] and cmd["usage_limited"]:
        print ("WARNING: you are using a custom source with usage limiting "
                "on, so the output might get truncated.")

    # [module] -c
    if cmd["case_sensitive"] and not cmd["first_letter"]:
        print "WARNING: using -c does nothing without -f."
    # [module] -B (without -u)
    if cmd["block_shuffle"] and not cmd["usage_limited"]:
        print "WARNING: using -B without -u does nothing."
    # [module] (-u -e), (-r -e), or (-u -r -e)
    if cmd["equal_weighting"]:
        if cmd["usage_limited"] or cmd["relative_usage"]:
            print "WARNING: -e overrides -u and -r, but you used two of them."
    # [module] -u -r
    elif cmd["usage_limited"] and cmd["relative_usage"]:
        print "WARNING: -r overrides -u, but you used both."
    # [module] (without -u, -r, or -e) one of them needs to be a fall back
    elif not cmd["usage_limited"]:
        cmd["relative_usage"] = True