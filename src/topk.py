from model import Model
import Queue
import utils
import string
import sys
import pickle
import json

def get_topk_generic(items, k, score_func):
  pq = Queue.PriorityQueue(maxsize=k)
  for i in xrange(k):
    assert not pq.full()
    pq.put(float("-inf"))
  worst = pq.get()
  for x in items:
    s = score_func(x)
    if (s, x) > worst:
      assert not pq.full()
      pq.put((s, x))
      worst = pq.get()
  while worst == float("-inf"):
    assert not pq.empty()
    sys.stderr.write(";")
    worst = pq.get()
  L = [worst]
  #pop items off queue
  while not pq.empty():
    next = pq.get()
    try:
      next[1]
    except TypeError:
      sys.stderr.write("Errant item: "+str(next)+"\n")
    if not next == float("-inf"):
      L.append(next)
  L.reverse()
  return L

def vocab_hist(M, sizes):
  VOCAB, Cx = M.VOCAB, M.Cx
  for s in sizes:
    count = sum(Cx[x] >= s for x in VOCAB)
    sys.stderr.write(str(s)+": "+str(count)+"\n")
  sys.stderr.write("total: "+str(len(VOCAB))+"\n")

#v is length of table (# seeds); k is width (# top scoring matches per)
#fp_pickle is file pointer for dumping pickled table
#fp_hr is file pointer for human readable printout of the table
def build_topk_table(M, fp_pickle, fp_hr, fp_json):
  assert M.args.model == "unordered_pmi" or M.args.model == "ordered_pmi"
  v = M.args.v
  k = M.args.k
  Cx, total_key, DOCx = M.Cx, M.total_key, M.DOCx
  TABLE = {}
  print "Computing clusters for top-k vocab, k = ", k
  vocab_list = list(DOCx)
  try:
    vocab_list.remove(total_key)
  except ValueError:
    sys.stderr.write("total_key not found in list.\n")
  if v > len(vocab_list):
    sys.stderr.write("Table size (v) too large for vocabulary; setting v = vocab size.")
    v = len(vocab_list)
  sys.stderr.write("About to print vocab historgram.\n")
  vocab_hist(M, [10,100,1000])
  sys.stderr.write("Computing vocab_list_top10K\n")
  vocab_list_topv = get_topk_generic(vocab_list, v, lambda x: DOCx[x])
  sys.stderr.write("Mapping vocab_list_top10K to x[1]\n")
  vocab_list_topv = [x[1] for x in vocab_list_topv]
  sys.stderr.write("Done computing vocab_list_top10K\n")
  i = 0
  for word_i in vocab_list_topv:
    i += 1
    sys.stderr.write(str(i)+": "+word_i+"\n")
    print str(i), word_i+' :'
    topk_i = get_topk_generic(vocab_list_topv, k, lambda y: M.PMI[utils.pair(word_i,y,M.args)])
    topk_i = [x for x in topk_i if x[0] > 0]
    sys.stderr.write(word_i+'\n')
    TABLE[word_i] = map(lambda x: (x[1],x[0]), topk_i)
    line = map(lambda x: x[0]+' '+"%.2f"%x[1], TABLE[word_i])
    str_line = word_i+': '+string.join(line, ', ')+'\n'
    fp_hr.write(str_line)
  assert len(TABLE) <= v
  pickle.dump(TABLE, fp_pickle)
  json.dump(TABLE, fp_json)

def create_table_fname(args):
  v = args.v
  k = args.k
  f_docmin = "D"+str(args.docmin)
  f_thresh = "T"+str(args.threshold)
  f_model = args.model
  f_disc = "disc" if args.disc else "nodisc"
  f_so = "so" if args.subjobj else "noso"
  f_v = "V"+str(v)
  f_k = "K"+str(k)
  fname_prefix = ""
  fname_suffix = f_model+'.'+f_disc+'.'+f_docmin+'.'+f_thresh+'.'+f_so+'.'+f_v+'.'+f_k
  fname = fname_prefix+fname_suffix
  return fname
