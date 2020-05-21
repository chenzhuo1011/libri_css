#!/bin/bash

PYTHON=python

curdir=`dirname $0`
curdir=`realpath $curdir`
# args
prep_script=$curdir/../python/gen_asrinput_raw_utterance.py
libricss_path=$EXPROOT/data
script_path=$curdir/../scripts
decode_path=$libricss_path/baseline/utterance

$PYTHON $prep_script --input_path $libricss_path/monaural/utterances --tool_path $script_path --decode_path $decode_path

