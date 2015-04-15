Text Rearranger
===============

Text Rearranger is a program that randomly redistributes the contents of a stream of text based on a couple key characteristics: the case of the word, the first letter, and the length. It includes a wide array of command line options to let users fine tune what algorithms they want to run, as well as give a lot of room for different uses. Requires Python 2. Also available on PyPi at https://pypi.python.org/pypi/text-rearranger/1.0.

Install
=======
Either download from GitHub, or `pip install text_rearranger`.

Usage
=====

The easiest way to get started with it is running it on a single text file. I recommend using a http://www.gutenberg.org/wiki/Main_Page book from Project Gutenberg. Put it in the same folder as Text Rearranger, and run  
`python textrearranger.py -i [name].txt -o output.txt -d`  
`-i` and `-o` redirect input and output, and `-d` uses the default, optimal settings. Open up output.txt to see what happened! You can run the same input again to get a new result. After that, you can run  
`python textrearranger.py --help`  
to get a breakdown of what all the options are and do to dig deeper. Start with the settings -d automatically uses. Settings that are highly related to each other will be listed right next to each other.

API
===

	-h, --help            show this help message and exit
	-w {0,1,2,3}, --warning-level {0,1,2,3}
						  set level of warnings (defaults to 2): 0 - show none 1
						  - show only warnings 2 - show warnings and notices 3 -
						  show notices only
	-E, --explode-on-warning

						  program will now crash on warnings
	-d, --default         uses default (optimal) settings, identical to running
						  the program with -Clcnupg

	-C, --compare-case    makes replacement words match case style, which mostly
						  implies and overpowers -c
	-l, --first-letter    requires first letter of a replacement word to be the
						  same (case-insensitive without -c)
	-c, --case-sensitive  makes -f case-sensitive, does nothing without -f
	-n, --length-check    requires length of a replacement word to be equal
	-L, --compare-lower   filter file comparisons ignore case

	-u, --limited-usage   usage of each word is limited to the number of
						  occurrences in the original text
	-r, --relative-usage  word usage will be based on relative frequency, but
						  overrides -u, and also falls back on this if none of
						  -u, -r, -e, -a, or -M are used
	-e, --equal-weighting
						  forces equal weighting of every word, but overrides -u
						  and -r
	-M, --map-words       maps each word to a unique replacement, and replaces
						  every instance with that instead of pure re-arranging,
						  and overrides -u, -r, and -e
	-a, --alphabetical-sort
						  sorts internal storage alphabetically

	-U, --force-limited-usage
						  force limited usage with any non -u setting
	-b, --block-shuffle   replacement words will not be shuffled, but only works
						  with -u
	-g, --get-different   tries to get different words for replacement
	-G GET_ATTEMPTS, --get-attempts GET_ATTEMPTS
						  specify number of times to try to get different
						  replacements, defaults to 10, and can exponentially
						  increase computing time
	-H, --halt-rearranger
						  halts rearranger from running, so text can only be
						  manipulated by non-arrangement based ways, such as
						  using word maps
	-J, --jabberwocky     jabberwockies words
	-j JABBERWOCKY_CHANCE, --jabberwocky-chance JABBERWOCKY_CHANCE
						  increase the chance of a word being jabberwockied
	-R RANDOM_SEED, --random-seed RANDOM_SEED
						  seeds random with given number

	-p, --preserve-punctuation
						  perfectly preserves all non-word punctuation if
						  defined, treats punctuation as letters otherwise
	-v, --void-outer      delete punctuation outside words
	-V, --void-inner      delete punctuation inside words
	-k KICK_CHANCE, --kick-chance KICK_CHANCE
						  chance that a word will randomly get a newline
	-t, --soft-truncate-newlines
						  newlines at the end of lines are removed
	-T, --hard-truncate-newlines
						  all newlines are removed completely
	-N, --truncate-multiple-newlines
						  multiple newlines will be truncated to single lines
	-W, --truncate-whitespace
						  all whitespace between words will be removed

	-i INPUT, --input INPUT
						  define an existing input file to re-arrange instead of
						  falling back on standard input
	-s SOURCE, --source SOURCE
						  define an existing source file to pull words from for
						  rearranging, but defaults to input if undefined
	-f FILTER, --filter FILTER
						  define an existing filter file to compare against for
						  selectively acting on words, and is only required for
						  filter modes
	-m WORD_MAP, --word-map WORD_MAP
						  define a pre-written word map file arranged where each
						  line is a word to replace followed by a space and the
						  word or phrase to replace all instances of the word
						  with, "cat dogs rule" replaces all instances of "cat"
						  with "dogs rule"
	-o OUTPUT, --output OUTPUT
						  define an output file instead of falling back on
						  standard output
	-O, --overwrite       automatically overwrites the output file

	-I, --inspection-mode
						  turns on inspection mode, which will output how it
						  arranges its text storage
	-B, --block-inspection-sort
						  leaves inspection data order unsorted
	-q, --frequency-count
						  displays number of occurences of word
	-Q, --frequency-percent
						  displays overall percent frequency of word
	-A DECIMAL_ACCURACY, --decimal-accuracy DECIMAL_ACCURACY
						  defines number of decimals to use for -Q, defaults to
						  2
	-x COUNT_MINIMUM, --count-minimum COUNT_MINIMUM
						  define minimum number of occurences for word
						  information to be displayed
	-y COUNT_MAXIMUM, --count-maximum COUNT_MAXIMUM
						  define maximum number of occurences for word
						  information to be displayed
	-X PERCENT_MINIMUM, --percent-minimum PERCENT_MINIMUM
						  define minimum frequency percent for word infoto be
						  displayed, with an ideal max of 100%
	-Y PERCENT_MAXIMUM, --percent-maximum PERCENT_MAXIMUM
						  define maximum frequency percent for word infoto be
						  displayed, with an ideal max of 100%

	-K, --keep-mode       turns on keep filter mode, which keeps words not
						  matching the filter, and rearranges others
	-P, --pure-mode       turns on pure filter mode, meaning no words will be
						  rearranged, but selectively filtered out
	-S, --filter-same     keeps/filters only words found in source
	-D, --filter-different
						  keeps/filters only words not found in source
	-F, --filter-source   filters the source files' internal storage

	-Z, --slow-output     slows output to print one line per interval, defaults
						  to 1 second
	-z SLOW_SPEED, --slow-speed SLOW_SPEED
						  change the wait interval for -z