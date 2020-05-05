#!/bin/bash

PYTHON=python

# args
prep_script=../python/gen_asrinput_separated_utterance.py
libricss_path=/data/zhuc/libricss/for_release
script_path=./scripts

echo "$prep_script --data_path $libricss_path --tool_path $script_path"

$PYTHON $prep_script --data_path $libricss_path --tool_path $script_path

