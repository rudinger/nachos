from collections import Counter
from collections import defaultdict
import utils

class Model:
  def __init__(self, args):
    self.total_key = "<TOTAL>" #
    self.args = args
    self.Cx = Counter() # unigram counts
    #self.Cx_total = 0

    self.Cxy = Counter() # bigram counts
    #self.Cxy_total = 0

    self.DOCx = Counter() # document counts
    self.DOCxy = Counter() # document bigram counts
    self.Cx_baseline = Counter() # simple unigram counts for the baseline

    self.Dxy = None # discount table for PMI models
    self.PMI = None # holds actual pmi scores; not explicitly necessary for cloze

    self.VOCAB = None #
    #set discount factor; default is 0.9; used only in bigram probability model
    assert 0 < args.discount_factor and args.discount_factor <= 1
    self.discount_factor = args.discount_factor

    #do something about log tables

  #subtract off discount_factor from each value in C greater than 0
  #discount factor should be a value between 0 and 1, non-inclusive
  def apply_abs_discount(self, C, discount_factor):
    assert self.args.model == "bigram"
    total_key = "<TOTAL>"
    for x in C:
      if x == total_key:
        continue
        #is this the right thing to do?
        #do i need to subtract more off from here?
      else:
        if C[x] > 0:
          C[x] -= discount_factor
          C[total_key] -= discount_factor

  #given a table of individual counts, Cx[x] and pairs counts, Cxy[(x,y)]
  #compute the pmi discount factor (Pantel & Ravichandran, 2004)
  #Dxy[(x,y)] = (Cxy[(x,y)]/(Cx[(x,y)]+1))*(min(Cx[x],Cx[y])/(min(Cx[x],Cx[y])+1))
  #where Cx and Cxy are individual and pair counts, respectively
  def compute_discount(self):
    Cx = self.Cx
    Cxy = self.Cxy
    total_key = self.total_key
    Dxy = defaultdict(float)
    for key in Cxy:
      if key == total_key:
        continue
      else:
        left = 1.0*Cxy[key]/(Cxy[key]+1)
        x,y = key
        m = min(Cx[x],Cx[y])
        right = 1.0*m/(m+1)
        Dxy[key] = left*right
    self.Dxy = Dxy

  #one of two discounting techniques to be applied if yesdisc flag is on
  def apply_discount(self):
    if self.args.disc:
      if self.args.model == "bigram":
        self.apply_abs_discount(self.Cx, self.discount_factor)
        self.apply_abs_discount(self.Cxy, self.discount_factor)
      elif self.args.model == "ordered_pmi" or self.args.model == "unordered_pmi":
        self.compute_discount()


  def compute_logtables(self):
    self.logCx = utils.compute_logtable(self.Cx)
    self.logCxy = utils.compute_logtable(self.Cxy)

  def compute_PMI(self):
    # should only be computed for pmi models
    if self.args.model == "ordered_pmi" or self.args.model == "unordered_pmi":
      total_key = self.total_key
      #self.PMI = defaultdict(lambda: 0.0)
      self.PMI = Counter()
      for key in self.Cxy:
        if key == total_key:
          continue
        if self.Cxy[key] == 0:
          self.PMI[key] = 0
        else:
          self.PMI[key] = self.logCxy[key] - self.logCxy[total_key] - self.logCx[key[0]] - self.logCx[key[1]] + 2*self.logCx[total_key]

  def set_vocab(self):
    #Establish a shared vocabulary for testing
    self.VOCAB = set(self.Cx_baseline.keys())

  def apply_threshold(self):
    if self.args.threshold > 1:
      for xy in self.Cxy:
        if self.Cxy[xy] < self.args.threshold:
          self.Cxy[xy] = 0

  #if an event is below docmin threshold, it will automatically tie for last place
  #this function computes the average rank of any event that "ties for last place"
  def set_bad_rank(self):
    Cx = self.Cx
    DOCx = self.DOCx
    #global DOCx
    V = len(Cx) - 1
    N_below_docmin = 0
    for x in Cx:
      if x == self.total_key:
        continue
      else:
        if DOCx[x] < self.args.docmin:
          N_below_docmin += 1
    #return 1 + V - ((N_below_docmin+1) / 2.0)
    self.bad_rank = 1 + V - ((N_below_docmin+1) / 2.0)
