#!/bin/bash
PYTHON=python

curdir=`dirname $0`
curdir=`realpath $curdir`
# args
prep_script=$curdir/../python/gen_asrinput_raw_utterance.py
libricss_path=$EXPROOT/data
script_path=$curdir/../scripts
decode_path=$libricss_path/separated_evaluation/utterance

# echo "$prep_script --data_path $libricss_path --tool_path $script_path --asr_path $asr_path"

$PYTHON $prep_script --input_path $libricss_path/separation_result/utterance_separation --tool_path $script_path --decode_path $decode_path --experiment_setup separated
