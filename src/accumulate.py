from model import Model
import utils

#given a list of chains from a single document, gather counts from that doc
#M is an instance of model.Model
def process_doc_chains(M, doc_chains):
  #Cx, Cxy are total unigram and bigram counts over gigaword (subsection), respectively
  #DOCx, DOCxy are total document frequencies over gigaword for unigrams and bigrams, respectively
  DOCx_found = False
  DOCxy_found = False
  Cx_found = False
  Cxy_found = False

  total_key = M.total_key
  args = M.args
  Cx = M.Cx
  Cxy = M.Cxy
  DOCx = M.DOCx
  DOCxy = M.DOCxy
  Cx_baseline = M.Cx_baseline

  docset_x = set()
  docset_xy = set()

  #if only looking at nsubj and dobj dependencies (as in skipgram paper)
  if args.subjobj:
    doc_chains = map(lambda z:[x for x in z if x.endswith('->nsubj') or x.endswith('->dobj')], doc_chains)


  for seq in doc_chains:
    for vdep in seq:
      Cx_baseline[vdep] += 1

  #filter for long or longest chains if option is enabled
  if args.coref == 'longest':
    #only retain the longest coref chain(s)
    doc_chains = [chain for chain in doc_chains if len(chain) == len(max(doc_chains,key=lambda x:len(x)))]
  elif args.coref == 'long':
    #select all chains with five or more events
    doc_chains = [chain for chain in doc_chains if len(chain) >= 5]
  else:
    assert args.coref == 'all'
    #all coref chains are included in counting

  for seq in doc_chains:

    #update DOCx (i.e. unigram document frequencies)
    if not DOCx_found:
      for vdep in seq:
        if not vdep in docset_x:
          DOCx[vdep] += 1
          docset_x.add(vdep)

    #make unigram updates to Cx, DOCx separately if using naive counts
    #naive: a a b a c => Cx[a] = 3
    if args.naive_uni:
      if not Cx_found:
        for vdep in seq:
          #increment total count for vdep
          if not Cx_found:
            Cx[vdep] += 1
            Cx[total_key] += 1

    #make bigram updates to Cxy, DOCxy
    #also make updates to Cx, DOCx if marginalizing/non-naive counts
    #non-naive: a a b a c => Cx[a] = 12 = Cxy[a,*]+Cxy[*,a]
    if (not Cxy_found) or (not DOCxy_found) or (not args.naive_uni and not Cx_found):
      vdep_pairs = utils.generate_pairs(seq,M.args)
      for vdep_pair in vdep_pairs:
        if not args.naive_uni:
          if not Cx_found:
            Cx[vdep_pair[0]] += 1
            Cx[vdep_pair[1]] += 1
            Cx[total_key] += 2
        #increment total count for vdep_pair
        if not Cxy_found:
          Cxy[vdep_pair] += 1
          Cxy[total_key] += 1
        #increment doc count for vdep_pair
        if (not vdep_pair in docset_xy) and (not DOCxy_found):
          DOCxy[vdep_pair] += 1
          docset_xy.add(vdep_pair)
