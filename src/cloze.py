import numpy
import model
import score
import sys

from collections import defaultdict

def pad(s):
  return s.ljust(15)

#parses a single test file
#returns a list of triples, where each triple is a cloze test in the following form
#(answer, test_chain, insert_index), e.g.
#('say->nsubj', ['go->nsubj','eat->nsubj','serve->iobj'], 2)
def parse_test_file(M, test_filename):
  args = M.args
  cloze_tests = []
  tf = open(test_filename, 'r')
  answer = None
  insert_index = None
  test_chain = None
  for line in tf:
    if line.startswith("###"):
      continue
    if not line: #i.e. line is empty
      continue
    if line.startswith("<CHAIN>"):
      continue
    if line.startswith("<TEST>"):
      continue
    if line.startswith("<ANSWER>"):
      answer = line[9:].strip()
      continue
    if line.startswith("<INSERT_INDEX>"):
      insert_index = int(line[15:].strip())
      continue
    if line.startswith("<CLOZE>"):
      test_chain = line[8:].strip()
      test_chain = test_chain.split()
      assert not answer == None
      assert not insert_index == None
      assert not test_chain == None
      #modify or skip cloze tests when -subjobj option is selected
      if args.subjobj:
        #remove events from chain that don't have nsubj or dobj ending
        test_chain = filter(lambda x: x.endswith('->nsubj') or x.endswith('->dobj'), test_chain)
        #skip cloze test if the answer is malformed, or the rest of the chain is empty
        if not (answer.endswith('->nsubj') or answer.endswith('->dobj')) or len(test_chain)==0:
          (answer, test_chain, insert_index) = (None, None, None)
          continue
      cloze_tests.append((answer, test_chain, insert_index))
      #reset cloze test components
      (answer, test_chain, insert_index) = (None, None, None)
      continue
  tf.close()
  return cloze_tests

def run_cloze_tests(M, cloze_tests):
  H = defaultdict(list)
  H_baseline = defaultdict(list)
  for (answer, test_chain, insert_index) in cloze_tests:
    sys.stderr.write('.')
    r = score.rank(M,answer,test_chain,insert_index)
    r_baseline = score.rank_baseline(M,answer)
    if len(test_chain) >= 10:
      H[10].append(r)
      H_baseline[10].append(r_baseline)
    else:
      H[len(test_chain)].append(r)
      H_baseline[len(test_chain)].append(r_baseline)
  return (H, H_baseline)

def print_histogram(H,H_baseline):
  H_sorted = sorted([(x,H[x]) for x in H])
  H_baseline_sorted = sorted([(x,H_baseline[x]) for x in H_baseline])
  #print "len\t\tavgrnk\t\tavgrnk_b\t\tmrr\t\tmrr_b\t\trec50\t\trec50_b\t\tN"
  print pad("len")+pad("avgrnk")+pad("avgrnk_b")+pad("mrr")+pad("mrr_b")+pad("rec50")+pad("rec50_b")+pad("N")
  for ((length, row), (length_b, row_b)) in zip(H_sorted,H_baseline_sorted):
    avg_rank = 1.0*sum(row)/len(row)
    avg_rank_b = 1.0*sum(row_b)/len(row_b)
    mrr = 1.0*sum([1.0/x for x in row])/len(row)
    mrr_b = 1.0*sum([1.0/x for x in row_b])/len(row_b)
    rec50 = 1.0*sum([1 for x in row if x <= 50])/len(row)
    rec50_b = 1.0*sum([1 for x in row_b if x <= 50])/len(row_b)
    assert length <= 10
    if length == 10:
      str_length = "10+"
    else:
      str_length = str(length)
    #print str_length+'\t\t'+str("%.2f" % avg_rank)+'\t\t'+str("%.2f" % avg_rank_b)\
    #+'\t\t\t'+str("%.3f" % mrr)+'\t\t'+str("%.3f" % mrr_b)\
    #+'\t\t'+str("%.2f" % rec50)+'\t\t'+str("%.2f" % rec50_b)+'\t\t'+str(len(row))
    print pad(str_length)+pad(str("%.2f" % avg_rank))+pad(str("%.2f" % avg_rank_b))\
    +pad(str("%.3f" % mrr))+pad(str("%.3f" % mrr_b))\
    +pad(str("%.2f" % rec50))+pad(str("%.2f" % rec50_b))+pad(str(len(row)))
  #print average performance over all chains
  N = 0
  avg_rank_tot = 0
  avg_rank_b_tot = 0
  mrr_tot = 0
  mrr_b_tot = 0
  rec50_tot = 0
  rec50_b_tot = 0
  allx = []
  allx_b = []
  for ((length, row), (length_b, row_b)) in zip(H_sorted,H_baseline_sorted):
    N += len(row)
    avg_rank_tot += sum(row)
    avg_rank_b_tot += sum(row_b)
    mrr_tot += sum([1.0/x for x in row])
    mrr_b_tot += sum([1.0/x for x in row_b])
    rec50_tot += sum([1 for x in row if x <= 50])
    rec50_b_tot += sum([1 for x in row_b if x <= 50])
    allx += row
    allx_b += row_b
  avg_rank_all = 1.0*avg_rank_tot/N
  avg_rank_b_all = 1.0*avg_rank_b_tot/N
  mrr_all = 1.0*mrr_tot/N
  mrr_b_all = 1.0*mrr_b_tot/N
  rec50_all = 1.0*rec50_tot/N
  rec50_b_all = 1.0*rec50_b_tot/N
  #determine how many metrics we've beaten the baseline on
  wins = 0
  if avg_rank_all < avg_rank_b_all:
    wins += 1
  if mrr_all > mrr_b_all:
    wins += 1
  if rec50_all > rec50_b_all:
    wins += 1
  #print "ALL"+'\t\t'+str("%.2f" % avg_rank_all)+'\t\t'+str("%.2f" % avg_rank_b_all)\
  #  +'\t\t\t'+str("%.3f" % mrr_all)+'\t\t'+str("%.3f" % mrr_b_all)\
  #  +'\t\t'+str("%.2f" % rec50_all)+'\t\t'+str("%.2f" % rec50_b_all)+'\t\t'+str(N)#+'\twins='+str(wins)
  print pad("ALL")+pad(str("%.2f" % avg_rank_all))+pad(str("%.2f" % avg_rank_b_all))\
    +pad(str("%.3f" % mrr_all))+pad(str("%.3f" % mrr_b_all))\
    +pad(str("%.2f" % rec50_all))+pad(str("%.2f" % rec50_b_all))+pad(str(N))