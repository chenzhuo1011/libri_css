#!/bin/bash

PYTHON=python

# args
prep_script=../python/gen_asrinput_separated_continuous.py
libricss_path=/data/zhuc/libricss/for_release
script_path=./scripts
asr_path=/data/zhuc/libricss./opencss

echo "$prep_script --data_path $libricss_path --tool_path $script_path  --asr_path $asr_path"

$PYTHON $prep_script --data_path $libricss_path --tool_path $script_path  --asr_path $asr_path

