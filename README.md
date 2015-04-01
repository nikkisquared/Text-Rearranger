Text Rearranger
===============

Text Rearranger is a program that randomly redistributes the contents of a stream of text based on a couple key characteristics: the case of the word, the first letter, and the length. It includes a wide array of command line options to let users fine tune what algorithms they want to run, as well as give a lot of room for different uses. Requires Python 2.

Usage
=====

The easiest way to get started with it is running it on a single text file. I recommend using a http://www.gutenberg.org/wiki/Main_Page book from Project Gutenberg. Put it in the same folder as Text Rearranger, and run  
python textrearranger.py -i [name].txt -o output.txt -d  
-i and -o redirect input and output, and -d uses the default, optimal settings. Open up output.txt to see what happened! You can run the same input again to get a new result.

After that, you can run  
python textrearranger.py --help  
to get a breakdown of what all the options are and do to dig deeper. Start with the settings -d automatically uses. Settings that are highly related to each other will be listed right next to each other.

API
===

	-h, --help            show this help message and exit  
	-d, --default         uses default (optimal) settings, identical to running
	                      the program with -Cfclup
	-f, --first-letter    requires first letter of a replacement word to be the
	                      same (case-insensitive without -c
	-c, --case-sensitive  makes -f case-sensitive, does nothing without -f
	-C, --compare-case    makes replacement words match case style, which mostly
	                      implies and overpowers -c
	-l, --length-check    requires length of a replacement word to be equal
	-u, --usage-limited   usage of each word is limited to the number of
	                      occurrences in the original text
	-B, --block-shuffle   replacement words will not be shuffled, but only works
	                      with -u
	-r, --relative-usage  word usage will be based on relative frequency, but
	                      conflicts with and overrides -u, and also falls back
	                      on this if none of -u, -r, or -e are called
	-e, --equal-weighting
	                      forces equal weighting of every word, but conflicts
	                      with and overrides -u and -r
	-p, --preserve-punctuation
	                      perfectly preserves all non-word punctuation if
	                      defined, treats punctuation as letters otherwise
	-t, --truncate-newlines
	                      newlines at the end of lines are removed
	-R RANDOM_SEED, --random-seed RANDOM_SEED
	                      seeds random with given number
	-i INPUT, --input INPUT
	                      define an existing input file to re-arrange instead of
	                      falling back on standard input
	-s SOURCE, --source SOURCE
	                      define an existing source file to pull words from for
	                      rearranging
	-o OUTPUT, --output OUTPUT
	                      define an output file instead of falling back on
	                      standard output
	-O, --overwrite       automatically overwrites the output file
	-F, --filter-mode     turns on filter mode only, meaning no words will be
	                      rearranged, to focus on special cases
	-S, --keep-same       replaces/keeps only words found in source
	-D, --keep-different  replaces/keeps only words not found in source