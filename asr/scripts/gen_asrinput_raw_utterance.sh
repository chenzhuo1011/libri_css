#!/bin/bash

PYTHON=python

# args
prep_script=../python/gen_asrinput_raw_utterance.py
libricss_path=$EXPROOT/data
script_path=../scripts
asr_path=$AMPATH

echo "$prep_script --data_path $libricss_path --tool_path $script_path --asr_path $asr_path"

$PYTHON $prep_script --data_path $libricss_path --tool_path $script_path --asr_path $asr_path

