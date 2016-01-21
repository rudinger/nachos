from model import Model

#e is the event to be scored against the chain, c, at insertion point, m
def score(M,e,c,m):
  logCx = M.logCx
  logCxy = M.logCxy
  Dxy = M.Dxy
  args = M.args
  total_key = M.total_key
  if not args.disc:
    if args.model == 'unordered_pmi':
      assert args.symmetric
      summands = [logCxy[unordered_pair(e,c_i)] for c_i in c]
      e_score = sum(summands) - len(c)*logCx[e]
    else:
      #insertion point matters for scoring in ordered versions
      assert args.model == 'ordered_pmi' or args.model == 'bigram'
      #if c is [a,b,c,d,e,f,g] and m is 3
      #then c_before is [a,b,c] and c_after is [d,e,f,g]
      c_before = c[0:m]
      c_after = c[m:]
      summands_before = [logCxy[(c_i,e)] for c_i in c_before]
      summands_after = [logCxy[(e,c_i)] for c_i in c_after]
      if args.model == 'ordered_pmi':
        e_score = sum(summands_before)+sum(summands_after)-len(c)*logCx[e]
      else:
        assert args.model == 'bigram'
        e_score = sum(summands_before)+sum(summands_after)-len(c_after)*logCx[e]
    return e_score
  else:
    assert args.disc
    if args.model == 'unordered_pmi':
      assert args.symmetric
      sum_total = 0
      for c_i in c:
        summand1 = logCxy[unordered_pair(e,c_i)]
        summand2 = (-1.0)*logCxy[total_key]
        summand3 = (-1.0)*logCx[c_i]
        summand4 = (-1.0)*logCx[e]
        summand5 = 2*logCx[total_key]
        sum_total += Dxy[unordered_pair(e,c_i)]*(summand1+summand2+summand3+summand4+summand5)
      e_score = sum_total
    else:
      #insertion point matters for scoring in ordered versions
      assert args.model == 'ordered_pmi' or args.model == 'bigram'
      #if c is [a,b,c,d,e,f,g] and m is 3
      #then c_before is [a,b,c] and c_after is [d,e,f,g]
      c_before = c[0:m]
      c_after = c[m:]
      summands_before = [logCxy[(c_i,e)] for c_i in c_before]
      summands_after = [logCxy[(e,c_i)] for c_i in c_after]
      if args.model == 'ordered_pmi':
        sum_total = 0
        for c_i in c_before:
          summand1 = logCxy[(c_i,e)]
          summand2 = (-1.0)*logCxy[total_key]
          summand3 = (-1.0)*logCx[c_i]
          summand4 = (-1.0)*logCx[e]
          summand5 = 2*logCx[total_key]
          sum_total += Dxy[(c_i,e)]*(summand1+summand2+summand3+summand4+summand5)
        for c_i in c_after:
          summand1 = logCxy[(e,c_i)]
          summand2 = (-1.0)*logCxy[total_key]
          summand3 = (-1.0)*logCx[c_i]
          summand4 = (-1.0)*logCx[e]
          summand5 = 2*logCx[total_key]
          sum_total += Dxy[(e,c_i)]*(summand1+summand2+summand3+summand4+summand5)
        e_score = sum_total
      else:
        #currently no discounting is implemented for bigram
        #because pmi discounting, Dxy[(x,y)] would be inappropriate for bigram probability
        assert args.model == 'bigram'
        e_score = sum(summands_before)+sum(summands_after)-len(c_after)*logCx[e]
    return e_score

#given solution, e_soln, rank computes the rank that solution would receive
#by score
#higher ranks are worse
#ties are resolved by averaging
#i.e. if e_soln is tied for rank 9 with four other candidates,
#return rank of 9+(4/2) = 11, since 11 will be the average rank
#of the five systems tied for rank 9,10,11,12,13.
#If e_soln has count below docmin, it is automatically tied for
#last place
def rank(M,e_soln,c,m):
  global total_key, DOCx, BAD_RANK, VOCAB
  total_key = M.total_key
  DOCx = M.DOCx
  BAD_RANK = M.bad_rank
  VOCAB = M.VOCAB
  args = M.args
  #initialize rank
  rank = 1
  #if e_soln is below docmin, it is tied for last place
  #with all other vocab items below docmin.
  #BAD_RANK is the average "tied for last place" rank
  #e.g. if 90-100 are tied for last place, BAD_RANK is 95
  if DOCx[e_soln] < args.docmin:
    #return BAD_RANK
    return M.bad_rank
  #compute score for correct solution
  e_soln_score = score(M,e_soln,c,m)
  #compute how many vocab items rank above the correct solution
  #for e in Cx:
  for e in VOCAB:
    if e == "be->nsubj":
      continue
    if e == total_key or e == e_soln:
      #don't count total_key or the solution itself
      #total_key is not part of the vocab
      #e_soln is already counted by initializing rank=1
      continue
    if DOCx[e] < args.docmin:
      #any item below docmin is already counted in BAD_RANK
      continue
    s = score(M,e,c,m)
    if s > e_soln_score:
      #increment rank by 1 for each item scored higher than the solution
      rank += 1
    elif s == e_soln_score:
      #increment rank by .5 for each item tied with the solution
      #this gives the average, as described above
      rank += 0.5
  return rank

#compute baseline ranking, according to frequency
#higher frequency == higher score
def rank_baseline(M,e_soln):
  #global Cx_baseline, total_key
  total_key = M.total_key
  Cx_baseline = M.Cx_baseline
  #intialize rank
  rank = 1
  e_soln_score = Cx_baseline[e_soln]
  #for e in Cx_baseline:
  for e in M.VOCAB:
    if e == total_key or e == e_soln or e == "be->nsubj":
      continue
    s = Cx_baseline[e]
    if s > e_soln_score:
      rank += 1
    elif s == e_soln_score:
      rank += .5
  return rank



