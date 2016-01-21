Author:
Rachel Rudinger
Johns Hopkins University
rudinger@jhu.edu

Nachos is a tool integrating a number of different methods for learning narrative chains as originally introduced in "Unsupervised Learning of Narrative Event Chains." (Chambers et al., 2008)

If you use this code, please cite its accompanying paper, "Learning to predict script events from domain-specific text" by Rudinger et al., 2015 with the following bibtex:

@InProceedings{rudinger-EtAl:2015:*SEM2015,
  author    = {Rudinger, Rachel  and  Demberg, Vera  and  Modi, Ashutosh  and  Van Durme, Benjamin  and  Pinkal, Manfred},
  title     = {Learning to predict script events from domain-specific text},
  booktitle = {Proceedings of the Fourth Joint Conference on Lexical and Computational Semantics},
  month     = {June},
  year      = {2015},
  address   = {Denver, Colorado},
  publisher = {Association for Computational Linguistics},
  pages     = {205--210},
  url       = {http://www.aclweb.org/anthology/S15-1024}
}

(This paper provides the mathematical details for the models implemented in Nachos, as well as back-references to the papers in which these models were introduced.)

Code Usage:

Nachos runs with Python 2.7 and has not been tested on later versions. It requires installation of the python package "dill" (for caching models), which can be installed with the pip package manager:

> pip install dill

The main nachos script is src/nachos.py.

To get info on all command-line arguments for nachos:

> cd src

> python nachos.py --help

Basic usage - To build a basic PMI narrative chains model and run a narrative cloze evaluation using the sample training and test data provided:

> python nachos.py

(Example) To learn an ordered pmi model using the skip-3 counting method (Jans et al., 2012) with a count threshold of 10 training on only the longest coref chains in each document:

> python nachos.py -model ordered_pmi -threshold 10 -skip 3 -coref longest

To cache a model:

> python nachos.py -model_out MODEL_FILENAME

To read the provided sample model instead of training one:

> python nachos.py -model_in ../models/sample_model.dill

Training data:

The file sample_data/file_list contains a list of the (gzipped) training files for nachos to process during training. Edit this file to point nachos at a different (user-specified) set of (gzipped) training files.

Narrative cloze test data:

The file sample_data/cloze_tests/sample_cloze contains a small number of sample narrative cloze tests which are used by default. To specify your own narrative cloze test file:

> python nachos.py -cloze_file CLOZE_FILE

The provided cloze file must be in the correct format. To generate your own narrative cloze files, use scripts/print_cloze_tests.py. (Details provided in script.)
