import math
from collections import defaultdict

#input: [4,3,2,1]
#output: [(3, 4), (2, 4), (1, 4), (2, 3), (1, 3), (1, 2)]
#return upper triangle (w/out diag) of cross-prod; tuples sorted
def generate_pairs(v, args):
  #global args
  result = []
  n = len(v)
  for (x,i) in zip(v,range(n)):
    #determine how far out to count
    #if args.skip == -1:
    if args.skip == -1:
      end = n
    else:
      end = i+1+(args.skip+1)
    if args.symmetric:
      result += [unordered_pair(x,y) for y in v[i+1:end]]
    else:
      result += [(x,y) for y in v[i+1:end]]
  return result

#simple utility to print any table of counts
def print_table(C):
  total_key = "<TOTAL>"
  for x in C:
    if not x == total_key:
      print str(x)+"\t\t"+str(C[x])
  if total_key in C:
    print str(total_key)+"\t\t"+str(C[total_key])

#given a table of counts, compute a corresponding table of log-counts
def compute_logtable(C):
  #logC = defaultdict(float)
  logC = defaultdict(lambda: math.log(.001))
  for key in C:
    logC[key] = math.log(C[key]+.001)
  return logC

#map an ordered pair to its corresponding unordered pair (set)
#by lexicographic sorting
def unordered_pair(x,y):
  return tuple(sorted([x,y]))

def pair(x,y,args):
  if args.symmetric:
    return unordered_pair(x,y)
  else:
    return (x,y)
