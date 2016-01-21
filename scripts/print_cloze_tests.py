#print_cloze_tests.py is a script to generate cloze tests for nachos
#usage:
#python print_cloze_tests.py FILENAME
#where FILENAME is a file that contains one space-separated chain per line.

#If a line in the input file has, for example, six events,
#then six corresponding cloze tests will be generated.

#output is printed to stdout

import sys
import string

assert len(sys.argv) == 2

fp = open(sys.argv[1], "r")

#for x in sys.stdin:
for x in fp:
  x = x.strip()
  if x.startswith("#"):
    continue
  if x.startswith("<"):
    continue
  if x == "":
    continue
  if x.isspace():
    continue
  seq = x.split()
  L = len(seq)
  if L == 0:
    continue
  print "<DOCNAME>\n"
  print "<CHAIN> len:"+str(L)
  for (w, i) in zip(seq, range(L)):
    print "<TEST>"
    #remove answer from chain
    test = seq[0:i]+seq[i+1:]
    print "<ANSWER> "+w
    assert w == seq[i]
    print "<INSERT_INDEX> "+str(i)
    print "<CLOZE> "+string.join(test)
