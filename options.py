#!usr/bin/python

"""Handle parsing program input and file opening"""

from __future__ import print_function

import sys
import os
import argparse

parser = argparse.ArgumentParser(description=
    "Takes a text file to re-write using the contents of itself, or "
    "another file, then writes it back in a random order. Has various "
    "controls to filter output to be topologically similar.")

# settings for running the program
parser.add_argument("-w", "--warning-level", type=int,
                    choices=[0, 1, 2, 3], default=2,
                    help="set level of warnings (defaults to 2):\n"
                    "0 - show none\n1 - show only warnings\n"
                    "2 - show warnings and notices\n3 - show notices only")
parser.add_argument("-E", "--explode-on-warning", action="store_true",
                    help="program will now crash on warnings")
parser.add_argument("-d", "--default", action="store_true",
                    help="uses default (optimal) settings, identical to "
                            "running the program with -Clcnupg")
parser.add_argument("-z", "--slow-output", action="store_true",
                    help="slows output to print one line per interval, "
                        "defaults to 1 second")
parser.add_argument("-Z", "--slow-speed", type=float, default=1.0,
                    help="change the wait interval for -z")

# layers to sort words on
parser.add_argument("-C", "--compare-case", action="store_true",
                    help="makes replacement words match case style, "
                        "which mostly implies and overpowers -c")
parser.add_argument("-l", "--first-letter", action="store_true",
                    help="requires first letter of a replacement word to be "
                        "the same (case-insensitive without -c)")
parser.add_argument("-c", "--case-sensitive", action="store_true",
                    help="makes -f case-sensitive, does nothing without -f")
parser.add_argument("-n", "--length-check", action="store_true",
                    help="requires length of a replacement word to be equal")
parser.add_argument("-L", "--compare-lower", action="store_true",
                    help="filter file comparisons ignore case")

# algorithms for determining word re-arrangement
parser.add_argument("-u", "--limited-usage", action="store_true",
                    help="usage of each word is limited to the number of "
                        "occurrences in the original text")
parser.add_argument("-r", "--relative-usage", action="store_true",
                    help="word usage will be based on relative frequency, "
                        "but overrides -u, and also falls back on this if "
                        "none of -u, -r, -e, -a, or -M are used")
parser.add_argument("-e", "--equal-weighting", action="store_true",
                    help="forces equal weighting of every word, "
                        "but overrides -u and -r")
parser.add_argument("-M", "--map-words", action="store_true",
                    help="maps each word to a unique replacement, and "
                        "replaces every instance with that instead of "
                        "pure re-arranging, and overrides -u, -r, and -e")
parser.add_argument("-a", "--alphabetical-sort", action="store_true",
                    help="sorts internal storage alphabetically")

# add-ons to algorithsm
parser.add_argument("-U", "--force-limited-usage", action="store_true",
                    help="force limited usage with any non -u setting")
parser.add_argument("-b", "--block-shuffle", action="store_true",
                    help="replacement words will not be shuffled, "
                        "but only works with -u")
parser.add_argument("-g", "--get-different", action="store_true",
                    help="tries to get different words for replacement")
parser.add_argument("-G", "--get-attempts", type=int, default=10,
                    help="specify number of times to try to get different "
                        "replacements, defaults to 10, and can "
                        "exponentially increase computing time")
parser.add_argument("-H", "--halt-rearranger", action="store_true",
                    help="halts rearranger from running, so text can only "
                        "be manipulated by non-arrangement based ways, "
                        "such as using word maps")
parser.add_argument("-J", "--jabberwocky", action="store_true",
                    help="jabberwockies words")
parser.add_argument("-j", "--jabberwocky-chance", type=int, default=25,
                    help="increase the chance of a word being jabberwockied")
parser.add_argument("-R", "--random-seed", type=int, default=-1,
                    help="seeds random with given number")

# punctuation sorting and whitespace handling
parser.add_argument("-p", "--preserve-punctuation", action="store_true",
                    help="perfectly preserves all non-word punctuation if "
                        "defined, treats punctuation as letters otherwise")
parser.add_argument("-v", "--void-outer", action="store_true",
                    help="delete punctuation outside words")
parser.add_argument("-V", "--void-inner", action="store_true",
                    help="delete punctuation inside words")
parser.add_argument("-k", "--kick-chance", type=int, default=0,
                    help="chance that a word will randomly get a newline")
parser.add_argument("-t", "--soft-truncate-newlines", action="store_true",
                    help="newlines at the end of lines are removed")
parser.add_argument("-T", "--hard-truncate-newlines", action="store_true",
                    help="all newlines are removed completely")
parser.add_argument("-N", "--truncate-multiple-newlines", action="store_true",
                    help="multiple newlines will be truncated to single lines")
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
parser.add_argument("-m", "--word-map", type=str, default=None,
                    help="define a pre-written word map file arranged where "
                        "each line is a word to replace followed by a space "
                        "and the word or phrase to replace all instances of "
                        "the word with, \"cat dogs rule\" replaces all "
                        "instances of \"cat\" with \"dogs rule\"")
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
parser.add_argument("-x", "--count-minimum", type=int, default=0,
                    help="define minimum number of occurences for word "
                        "information to be displayed")
parser.add_argument("-y", "--count-maximum", type=int, default=sys.maxint,
                    help="define maximum number of occurences for word "
                        "information to be displayed")
parser.add_argument("-X", "--percent-minimum", type=float, default=0,
                    help="define minimum frequency percent for word info"
                        "to be displayed, with an ideal max of 100%")
parser.add_argument("-Y", "--percent-maximum", type=float,
                    default=float("inf"),
                    help="define maximum frequency percent for word info"
                        "to be displayed, with an ideal max of 100%")

# filter mode, filters, filter organization
parser.add_argument("-K", "--keep-mode", action="store_true",
                    help="turns on keep filter mode, which keeps words not "
                        "matching the filter, and rearranges others")
parser.add_argument("-P", "--pure-mode", action="store_true",
                    help="turns on pure filter mode, meaning no words will "
                        "be rearranged, but selectively filtered out")
parser.add_argument("-S", "--filter-same", action="store_true",
                    help="keeps/filters only words found in source")
parser.add_argument("-D", "--filter-different", action="store_true",
                    help="keeps/filters only words not found in source")
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

    defaults = ["compare_case", "first_letter", "case_sensitive",
                "length_check", "limited_usage", "preserve_punctuation"]
    if cmd["default"]:
        for arg in defaults:
            cmd[arg] = True

    msgs = validate_command(cmd)
    print_msgs(cmd, msgs)
    msgs = validate_files(cmd)
    print_msgs(cmd, msgs)

    for fType in ("input", "source", "filter", "word_map"):
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

    # -f "..." (without -S or -D)
    if cmd["filter"]:
        if not (cmd["filter_same"] or cmd["filter_different"]):
            msgs.append("WARNING: A filter file does nothing without using "
                        "a filter, -S or -D.")
        elif cmd["filter"] == cmd["input"]:
            sys.exit("ERROR: filter and input files are the same.")
    # -S or -D (without -f "...")
    elif not cmd["filter"] and (cmd["filter_same"] or cmd["filter_different"]):
        if cmd["source"] != cmd["input"]:
            cmd["filter"] = cmd["source"]
            msgs.append("NOTICE: filter file will be the source file.")
        else:
            sys.exit("ERROR: You can't use a filter, -S or -D, without a "
                    "filter file, and it can't be source as it is the "
                    "same as input.")

    if cmd["word_map"]:
        # -m -M
        if cmd["map_words"]:
            msgs.append("NOTICE: Word map will be initialized with %s." % 
                cmd["word_map"])
        # -m (without -M)
        else:
            msgs.append("NOTICE: Using given word map file %s." % 
                cmd["word_map"])

    # check output file settings, and try to open it
    if cmd["output"] != sys.stdout:
        if os.path.isfile(cmd["output"]): 
            query = "%s already exists. Overwrite? Y/N\n"
            # -o "..." -O
            if cmd["overwrite"]:
                msgs.append("NOTICE: Automatically overwriting %s." % 
                    cmd["output"])
            elif not raw_input(query % cmd["output"]).startswith("Y"):
                sys.exit("Terminating. Rename your file or output parameter.")
        cmd["output"] = open(cmd["output"], 'w')
    # -O (without -o "...")
    elif cmd["overwrite"]:
        msgs.append("NOTICE: -O does nothing without specifying an output "
                    "file with -o.")

    return msgs


def validate_command(cmd):
    """
    Check cmd for invalid or conflicting input
    Return notices and warnings on
    """
    msgs = []

    # -E -w (0 or 3)
    if cmd["explode_on_warning"] and (cmd["warning_level"] in (0, 3)):
        msgs.append("WARNING: Program set to crash on warnings, but warnings "
                    "have been hidden. Only one option should be set.")
    # -Z [x] (without -z)
    if cmd["slow_speed"] != 1.0 and not cmd["slow_output"]:
        msgs.append("NOTICE: Defining -Z does nothing without calling -z.")

    # -c (without -l)
    if cmd["case_sensitive"] and not cmd["first_letter"]:
        msgs.append("NOTICE: Using -c does nothing without -l.")
    if cmd["compare_lower"]:
        # -C -L
        if cmd["compare_case"]:
            msgs.append("NOTICE: -C does nothing with -L on.")
        # -l -c -L
        if cmd["case_sensitive"] and cmd["first_letter"]:
            msgs.append("NOTICE: -c does nothing with -L on.")

    # -M -u, -M -r, -M -e, or any combination
    if (cmd["map_words"] and (cmd["limited_usage"] or 
            cmd["relative_usage"] or cmd["equal_weighting"])):
        msgs.append("WARNING: -M overrides -u, -r, and -e, but you used "
                    "two of them.")
    # -u -e, -r -e, or -u -r -e
    elif (cmd["equal_weighting"] and 
            (cmd["limited_usage"] or cmd["relative_usage"])):
        msgs.append("WARNING: -e overrides both -u and -r, but you used two "
                    "of them.")
    # -u -r
    elif cmd["limited_usage"] and cmd["relative_usage"]:
        msgs.append("WARNING: -r overrides -u, but you used both.")
    # (without -u, -r, -e, -M, or -a, and not -I, -P, or -K)
    elif (not (cmd["limited_usage"] or cmd["relative_usage"] or 
            cmd["equal_weighting"] or cmd["map_words"] or
            cmd["alphabetical_sort"]) and
            not (cmd["inspection_mode"] or cmd["pure_mode"] or
            cmd["keep_mode"])):
        msgs.append("NOTICE: Falling back on relative usage mode, since "
                    "none of -u, -r, -e, -M, or -a were used.")
        cmd["relative_usage"] = True


    if cmd["force_limited_usage"]:
        # -u -U
        if cmd["limited_usage"]:
            msgs.append("NOTICE: -U is implied by -u, but you used both.")
        # -U
        else:
            msgs.append("NOTICE: Because of -U, output may be truncated.")
    # -b (without -u)
    if cmd["block_shuffle"] and not cmd["limited_usage"]:
        msgs.append("NOTICE: Using -b does nothing without -u.")

    # -M -g
    if cmd["map_words"] and cmd["get_different"]:
        msgs.append("NOTICE: -g is implied by -M, but you used both.")
    # -G (without -M or -g)
    if (cmd["get_attempts"] != 10 and
            not (cmd["map_words"] or cmd["get_different"])):
        msgs.append("NOTICE: -G does nothing without -g or -M.")
    # -H
    if cmd["halt_rearranger"]:
        msgs.append("NOTICE: No text will be re-arranged since you called -H.")
    # -j [x] (without -J)
    if cmd["jabberwocky_chance"] != 25 and not cmd["jabberwocky"]:
        msgs.append("NOTICE: Defining -j without -J does nothing.")
    # -j [x] (where x < 1)
    elif cmd["jabberwocky_chance"] < 1:
        msgs.append("WARNING: 0 or negative values for -j block -J.")
    # -j [x] (where x > 100)
    elif cmd["jabberwocky_chance"] > 100:
        msgs.append("NOTICE: Defining -j over 100%% does nothing different.")

    # -p -v
    if (cmd["preserve_punctuation"] and cmd["void_outer"]):
        msgs.append("NOTICE: You used -p and -v, but -v overrides -p.")
    # -k [x] (where x < 0)
    if cmd["kick-chance"] < 0:
        msgs.append("NOTICE: You defined -k less than 0, so it does nothing.")
    # -k [x] (where x > 100)
    elif cmd["kick-chance"] > 100:
        msgs.append("NOTICE: Defining -k greater than 100 does nothing.")
    if cmd["hard_truncate_newlines"]:
        # -k [x] -T
        if cmd["kick-chance"]:
            msgs.append("WARNING: You used both -T and -k, but -T overrides "
                        "-k and stops it from doing anything.")
        # -t -T
        if cmd["soft_truncate_newlines"]:
            msgs.append("NOTICE: You used both -t and -T, but -T implies -t.")
        # -N -T
        if cmd["truncate_multiple_newlines"]:
            msgs.append("NOTICE: You used both -N and -T, but -T implies -N.")

    # -s source.txt -u
    if (cmd["source"] and cmd["source"] != cmd["input"] and
        (cmd["limited_usage"] or cmd["force_limited_usage"])):
        msgs.append("WARNING: You are using a custom source with usage "
                    "limiting on, so the output might be truncated.")

    # -B (without -I)
    if cmd["block_inspection_sort"] and not cmd["inspection_mode"]:
        msgs.append("NOTICE: -B does nothing without -I.")
    # -q or -Q (without -I)
    if (not cmd["inspection_mode"] and
            (cmd["frequency_count"] or cmd["frequency_percent"])):
        msgs.append("NOTICE: -q and -Q do nothing without -I.")
    # -A [x] (without -Q)
    if cmd["decimal_accuracy"] != 2 and not cmd["frequency_percent"]:
        msgs.append("NOTICE: -A does nothing without calling -Q.")
    # -I -S or -D (without -F)
    if (cmd["inspection_mode"] and not cmd["filter_source"] and
            (cmd["filter_same"] or cmd["filter_different"])):
        msgs.append("WARNING: -I with -S or -D requires the -F flag. It has "
                    "been automatically set.")
        cmd["filter_source"] = True
    # -x, -y, -X, or -Y (without -I)
    if (not cmd["inspection_mode"] and (cmd["count_minimum"] != 0 or
            cmd["count_maximum"] != sys.maxint or
            cmd["percent_minimum"] != 0 or
            cmd["percent_maximum"] != float("inf"))):
        msgs.append("NOTICE: You defined one or more of -x, -y, -X, and -Y "
                    "without calling -I, so they do nothing.")
    # -x [x] or -y [x] (where x is < 0)
    if cmd["count_minimum"] < 0 or cmd["count_maximum"] < 0:
        msgs.append("WARNING: You defined -x and/or -y lower than 0, "
                "meaning they will do nothing.")
    # -x [a] -y [b] (where b < a)
    if cmd["count_maximum"] < cmd["count_minimum"]:
        msgs.append("WARNING: You defined -y lower than -x, meaning those "
                    "settings will do nothing.")
    # -X [x] or -Y [x] (where x is < 0)
    if cmd["percent_minimum"] < 0 or cmd["percent_maximum"] < 0:
        msgs.append("WARNING: You defined -Y lower than -X, meaning those "
                    "settings will do nothing.")
    # -X [x] (where x is >100)
    if cmd["percent_minimum"] > 100:
        msgs.append("WARNING: -X was defined with a value higher than 100%%, "
                    "meaning nothing will show up for inspection.")
    # -X [a] -Y [b] (where b < a)
    elif cmd["percent_maximum"] < cmd["percent_minimum"]:
        msgs.append("WARNING: You defined -Y lower than -X, meaning nothing "
                    "will be output.")

    # -s "..." -P (without -F)
    if cmd["pure_mode"] and cmd["source"] and not cmd["filter_source"]:
        msgs.append("NOTICE: You defined a source, but with -P the source "
                    "will not be used for anything.")

    # -I -P
    if cmd["inspection_mode"] and cmd["pure_mode"]:
        msgs.append("WARNING: -P should not be used with -I. Results are "
                    "undefined and may be undesired.")
    # -K -P
    elif cmd["keep_mode"] and cmd["pure_mode"]:
        msgs.append("WARNING: Filter modes -K and -P are oppositional, "
                    "but you used both. Results are undefined.")
    # -I -K
    elif cmd["inspection_mode"] and cmd["keep_mode"]:
        msgs.append("WARNING: -K should not be used with -I. Results are "
                    "undefined and may be undesired.")

    # -S -D
    if cmd["filter_same"] and cmd["filter_different"]:
        msgs.append("WARNING: Filters -S and -D are oppositional, "
                    "but you used both. Results are undefined.")
    # -S -D (without -I, -K, or -P)
    if ((cmd["filter_same"] or cmd["filter_different"]) and
            not (cmd["inspection_mode"] or cmd["keep_mode"] or
            cmd["pure_mode"])):
        print(cmd["keep_mode"])
        msgs.append("WARNING: You called a filter, -S or -D, but without "
                    "using a filter mode, -I, -K, or -S. Falling back on -K.")
        cmd["keep_mode"] = True

    return msgs