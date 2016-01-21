import readers
import score
import utils
import accumulate
import topk
import cloze

from model import *

import sys
import argparse
import dill

if __name__ == "__main__":

  #parse command line arguments. Run program with -h option to print out helpful usage tips.
  parser = argparse.ArgumentParser(description=\
    "Nachos: a tool for building Narrative Chains.\nAuthor: Rachel Rudinger, January 2015.")

  #set options for reading in from or writing out to model object
  parser.add_argument('-model_in', action='store', dest='model_in', type=str, default=None,
    help="Optionally specify location of model file to read in.")
  parser.add_argument('-model_out', action='store', dest='model_out', type=str, default=None,
    help="Optionally specify filename to write model to. (Can later be read in with -model_in option.)")

  #set various thresholding parameters
  parser.add_argument('-docmin', action='store', dest='docmin', type=int, default=1,
    help="The minimum number of documents verb/verb-pair must appear in. Default is 1.")
  parser.add_argument('-threshold', action='store', dest='threshold', type=int,
    default=1, help="The minimum number of total appearances each verb/verb-pair must have. Default is 1.")

  #set options for how to count bigrams
  parser.add_argument('-sym', action='store_true', dest='symmetric', default=False,\
    help="Option to compute symmetric pmi. Default is asymmetric/ordered.")
  parser.add_argument('-skip', action='store', dest='skip', type=int, choices=(-1,0,1,2,3,4,5), default=-1,\
    help="Size of skipgram. Default is -1, i.e. skip up to entire length of chain.")
  parser.add_argument('-naive_uni', action='store_true', dest='naive_uni',default=False,\
    help="If selected, the naive_uni option counts C[x] as individual counts, \
    rather than as a marginalization over C[x,y].")
  parser.add_argument('-so', action='store_true', dest='subjobj', default=False,\
    help="Filter out all events that are not either nsubj or dobj dependencies.")
  parser.add_argument('-coref', action='store', dest='coref', choices={'all','long','longest'},\
    default='all', help="Specifies which coref chains to count over: all, long, or longest.")

  #select predictive model
  parser.add_argument('-model', action='store', dest='model', choices={'ordered_pmi','unordered_pmi','bigram'},\
    default='ordered_pmi', help="Select predictive model for narrative cloze evaluation. If -sym flag selected, \
    then unordered_pmi model must be specified.")

  #option to suppress discounting
  parser.add_argument('-nodisc', action='store_false', dest='disc', default=True,
    help="By default discounting is performed on all models. Use -nodisc option to \
    suppress use of discounting.")

  #option to specify discount factor in absolute discounting
  parser.add_argument('-discfactor', action='store', dest='discount_factor', type=float, default=0.9,\
    help="Specify discount factor for absolute discounting (for use with bigram only).")

  #specify location of cloze tests
  parser.add_argument('-cloze_file', action='store', dest='cloze_file', type=str, default="../sample_data/cloze_tests/sample_cloze",\
    help="Provide name of file with cloze tests in cloze test format.")

  #specify location of training data (name of file containing list of training files)
  parser.add_argument('-file_list', action='store', dest='file_list', default='../sample_data/file_list',\
    help="Name of file containing list of names of (gzipped) files containing training data.\
    Default is \"file_list\".")

  #parameters for generating top-k tables
  parser.add_argument('-v', action='store', dest='v', default=5000, type=int, help="Vocabulary size for\
    building top-k table, i.e. how many rows in the v-by-k table. Default of 5,000.")
  parser.add_argument('-k', action='store', dest='k', default=10, type=int, help="The k in \"top-k\" table.\
    Default is 50.")

  #parse arguments
  args = parser.parse_args(sys.argv[1:])

  #if pre-built model is specified, read it in and don't build a new model
  if args.model_in:
    sys.stderr.write("Loading model file...\n")
    model_in_fp = open(args.model_in, "r")
    M = dill.load(model_in_fp)
    model_in_fp.close()

  #if no pre-built model is specified, build a new model based on command-line args
  else:

    #verify flags are logically consistent
    if args.symmetric and not args.model == 'unordered_pmi':
      sys.stderr.write("Inconsistent flags. Whenever -sym flag is enabled, -model unordered_pmi must also be enabled.\n")
      sys.exit(-1)
    if not args.symmetric and (args.model == 'unordered_pmi'):
      sys.stderr.write("Inconsistent flags. If -model unordered_pmi flag is selected, then -sym flag must also be set.\n")
      sys.exit(-1)

    #establish filename componenents for saving output
    sys.stderr.write("Pre-processing...\n")
    sym = "sym" if args.symmetric else "asym"
    skipval = "skipall" if args.skip==-1 else "skip"+str(args.skip)
    uni = "naiv" if args.naive_uni else "marg"
    so = "sodep" if args.subjobj else "alldep"
    coref = "c_"+args.coref

    #initialize Model
    M = Model(args)

    #process data from files containing extracted chains
    sys.stderr.write("Gathering counts...\n")
    readers.read_file_list(M, M.args.file_list)

    #count post-processing
    sys.stderr.write("\nPost-processing counts...\n")
    M.set_vocab()
    M.apply_threshold()
    M.apply_discount() #method checks that yesdisc flag is on
    M.compute_logtables()
    M.compute_PMI() #checks that a pmi model is selected; does nothing for bigram
    M.set_bad_rank() #sets default rank for events below count threshold

  #save model to file if model_out specified
  if args.model_out:
    sys.stderr.write("Writing to model file...\n")
    model_out_fp = open(args.model_out, "w")
    dill.dump(M, model_out_fp)
    model_out_fp.close()

  #sample code for generating top-k tables:
  #topk_fname = topk.create_table_fname(M.args)
  #fp_pickle = open(topk_fname+".pickle","w")
  #fp_hr = open(topk_fname+".hr","w")
  #fp_json = open(topk_fname+".json","w")
  #topk.build_topk_table(M, fp_pickle, fp_hr, fp_json)

  #Cloze evaluation
  sys.stderr.write("Running cloze tests...\n")
  #read in cloze test file
  cloze_tests = cloze.parse_test_file(M, args.cloze_file)
  #run cloze tests
  (H, H_baseline) = cloze.run_cloze_tests(M, cloze_tests)
  #compute and print aggregate scores (avgrnk, MRR, rec@50, etc)
  sys.stderr.write('\n')
  cloze.print_histogram(H,H_baseline)
