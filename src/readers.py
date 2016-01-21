from model import Model
import accumulate

import gzip
import sys

#takes a file(name) containing a list of the (gzipped) files to process and processes them
def read_file_list(M, fname, prefix=""):
  fp = open(fname, "r")
  for line in fp:
    name = line.strip()
    if len(prefix) > 0 and not prefix.endswith("/"):
      prefix = prefix+"/"
    sys.stderr.write("Currently processing: "+prefix+name+'\n')
    read_chain_file(M, prefix+name)
  fp.close()

#iterate through file, processing chains one document at a time
def read_chain_file(M, fname):

  doc_chains = [] #list of chains in the current document

  with gzip.open(fname) as f:
    for line in f:
      if line.startswith('###'):
        continue
      elif line.startswith('<DOCNAME>'):
        #new document, reinitialize the vocab sets for each doc
        sys.stderr.write(".")
        if not doc_chains == []:
          accumulate.process_doc_chains(M, doc_chains) #have reached end of doc; ready for processing
        doc_chains = [] #reset doc_chains for new document
        continue
      else:
        seq = line.split()
        doc_chains.append(seq)
  if doc_chains:
    accumulate.process_doc_chains(M, doc_chains)
