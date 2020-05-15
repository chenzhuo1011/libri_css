#!/bin/bash

PYTHON=python

curdir=`dirname $0`
curdir=`realpath $curdir`

# args
prep_script=$curdir/../python/gen_asrinput_raw_continuous.py
libricss_path=$EXPROOT/data
script_path=$curdir/../scripts
asr_path=$AMPATH

$PYTHON $prep_script --input_path $libricss_path/monaural/segments --decode_path $libricss_path/baseline/segments --tool_path $script_path --am_path $asr_path
