# Support for class based n-gram language models in Riva (WFST Decoder)
Language models are used in speech recognition tasks to help disambiguate 
which word is more likely to occur given it is preceded by a sequence of words.
Conventional n-gram models, model the probability of a word occurring given it 
is preceded by a sequence of (n-1) words.

However, in many domains, there is a likelihood of a having a 
sequence of words that may be similar in nature. 

Consider for example the phrases *"I would like to fly from New York to Seattle"*
and *"I would like to fly from London to Paris"*, the probabilities of these two 
sentences are generally only dependent on how often people fly between these  
places. Otherwise, the probabilities of occurrence of these two sentences in a
domain involving booking of flights is equally probable.

This then requires support for building ngram models that consider word classes.
Word classes can also be considered as entities or entity types (as in NER), but 
are more generic in nature.


# WFST Decoding
Support for word classes with ngrams is not trivial. One alternative could be to 
generate using BNF grammars all possible such sequences. However, this could
easily increase the size of the LM and could still cause issues with multi-word 
word classes. 

An alternative approach is to use Weighted-finite state transducers (WFSTs). 
WFSTs as used in speech recognition consists of three main components:

* Grammar WFST (`G.fst`) - A grammar WFST encodes word sequences in a 
language/domain. In general this is basically a language model represented as
a weighted finite state acceptor.
* Lexicon WFST (`L.fst`) - A lexicon WFST encodes the mapping between a sequence
of tokens (phonemes/BPE/WPE or other CTC units) to the corresponding word.
* Token WFST (`T.fst`) - The token WFST maps a sequence of frame-level CTC labels
to a single lexicon unit (phonemes/BPE/WPE or other CTC units).

These three WFSTs are composed together with other operations to form `TLG.fst`.
The sequence of operations are `T ◦ min ( det ( L ◦ G ) )` where
*  `◦` refers to the composition operation
* `min` refers to minimization
* `det` refers to determinization

For more information,  see 
["Speech Recognition with Weighted Finite-State Transducers"](http://www.cs.nyu.edu/~mohri/pub/hbka.pdf) 
by Mohri, Pereira and Riley (in Springer Handbook on SpeechProcessing and Speech Communication, 2008).


## Supporting Class Language models in the WFST framework
Support for class language models in the WFST framework can be summarized as 
modifying `G.fst` to support paths in the acceptor that refers to word classes.
This requires that
* The lexicon has all entries from both the language model and the entries in
each of word classes. This is important as otherwise the words in the word 
classes will not be recognized.
* The n-gram model should have the relevant phrases build from word class grammars.
For example in the above example the word class grammar would 
be *"I would like to fly from **#entity:city** to **#entity:city**"* 
with **#entity:city**
being the label for the word class corresponding to cities with airports. 
This can be achieved in the following two ways:
    - Build the language model from text containing standard text as well as
  word class labels
    - n-gram LM interpolation/mixing of two LMs, one from standard text and other 
  from domain specific grammars.

The latter option provides for better weighting between in-domain and out of 
domain LMs. 
Please refer to the tutorial ["How To Train, Evaluate, and Fine-Tune an n-gram Language Model"](https://github.com/nvidia-riva/tutorials/blob/main/asr-python-advanced-nemo-ngram-training-and-finetuning.ipynb) 
for LM model interpolation using kenlm. 
Alternatively [SRILM](http://www.speech.sri.com/projects/srilm/) (license required) can also be used here

The process for supporting word classes in the WFST framework basically involves
replacement of the arcs representing the class labels, with FSTs created from 
the entities present in the word classes. Given a `G.fst` containing 
word class labels (`#entity:<class>`), and the files (filenames `<class>.txt`) 
containing the list of entities for the class. The list of entities  is not 
restricted to words and could be phrases

For example, in the above example `cities.txt` would contain at the very least the 
following
```shell
$> cat city.txt
london
new york
paris
seattle
```

## Process to create the `TLG.fst` supporting word classes
Checkout the `class_lm` branch from https://github.com/anand-nv/riva-asrlib-decoder/tree/class_lm. 
All the below scripts are available in `src/riva/decoder/scripts/prepare_TLG_fst` path.

* Generate the lexicon, list of Tokens/units and list of entities from the 
arpa file. This is accomplished using `lexicon_from_arpa.py` script. 
The syntax for the command is as follows:

`lexicon_from_arpa.py --asr_model <path_to_nemo_model> --lm_path <path_to_arpa_file> --grammars <path_to_folder_containing_grammars> <units_txt_path:output> <lexicon_path:output> <classlabels_path:output>`

This generates the list of units(tokens), the lexicon and the list of word 
classes (to be used as disambiguation symbols) 

* Generate the FSTs, `T.fst`, `L.fst` and `G.fst`, extend and compose to 
form `TLG.fst`

`mkgraph_ctc_classlm.sh --units <units_txt_path> --extra_word_disamb <classlabels_path> <lexicon_path>  <path_to_arpa_file> <lang_folder_path:output>`

When run successfully, the above command will generate a graph folder in
`<lang_folder_path>` with the name `graph_CTC_<lm_name>` which contains
all the files relevant for decoding with WFST


## Evaluation
The `evaluate_nemo_wfst.py` script can help evaluate the WFST decoder before 
being used in the Riva service maker build. This would be useful to 
debug any issues with `TLG.fst`

The script can be run as follows
`./evaluate_nemo_wfst.py <model_path> <graph_path> <path_containing_audio_files> <results_txt_file:output>`

## Deploying in Riva
The generated `TLG.fst` can be used with the Kaldi decoder in Riva. To build the Riva ASR service using the generated
`TLG.fst`, run:

```shell
# Syntax: riva-build <task-name> output-dir-for-rmir/model.rmir:key dir-for-riva/model.riva:key
! docker run --rm --gpus 0 -v $MODEL_LOC:/data $RIVA_SM_CONTAINER -- \
    riva-build speech_recognition \
        /data/rmir/asr_offline_conformer_ctc.rmir:$KEY \
        /data/$MODEL_NAME:$KEY \
        --offline \
        --name=asr_offline_conformer_wfst_pipeline \
        --ms_per_timestep=40 \
        --chunk_size=4.8 \
        --left_padding_size=1.6 \
        --right_padding_size=1.6 \
        --nn.fp16_needs_obey_precision_pass \
        --featurizer.use_utterance_norm_params=False \
        --featurizer.precalc_norm_time_steps=0 \
        --featurizer.precalc_norm_params=False \
        --featurizer.max_batch_size=512 \
        --featurizer.max_execution_batch_size=512 \
        --decoder_type=kaldi \
        --decoding_language_model_fst=/data/graph/TLG.fst \
        --decoding_language_model_words=/data/graph/words.txt \
        --kaldi_decoder.asr_model_delay=5 \
        --kaldi_decoder.default_beam=17.0 \
        --kaldi_decoder.max_active=7000 \
        --kaldi_decoder.determinize_lattice=true \
        --kaldi_decoder.max_batch_size=1  \
        --language_code=en-US \
        --wfst_tokenizer_model=<far_tokenizer_file> \
        --wfst_verbalizer_model=<far_verbalizer_file> \
        --speech_hints_model=<far_speech_hints_file>
```




