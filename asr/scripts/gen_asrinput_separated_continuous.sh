#!/bin/bash

PYTHON=python

curdir=`dirname $0`
curdir=`realpath $curdir`

# args
prep_script=$curdir/../python/gen_asrinput_raw_continuous.py
libricss_path=$EXPROOT/data
script_path=$curdir/../scripts
asr_path=$AMPATH

$PYTHON $prep_script --multi_stream --input_path $libricss_path/separation_result/continuous_separation --decode_path $libricss_path/separation_baseline --tool_path $script_path --am_path $asr_path


