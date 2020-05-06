#!/bin/bash

# args
thisdir=`dirname $0`
thisdir=`realpath $thisdir`

prep_script=$thisdir/../python/gen_asrinput_raw_continuous.py
libricss_path=$EXPROOT/data

script_path=$thisdir
asr_path=/data/zhuc/libricss/opencss

echo "$prep_script --data_path $libricss_path --tool_path $script_path --asr_path $asr_path"
python $prep_script --data_path $libricss_path --tool_path $script_path --asr_path $asr_path
