#!/bin/bash

# args
prep_script=../python/gen_asrinput_raw_continuous.py
libricss_path=$EXPROOT/data
script_path=../scripts
asr_path=$AMPATH

prep_script=$thisdir/../python/gen_asrinput_raw_continuous.py
libricss_path=$EXPROOT/data

script_path=$thisdir
asr_path=/data/zhuc/libricss/opencss

echo "$prep_script --data_path $libricss_path --tool_path $script_path --asr_path $asr_path"
python $prep_script --data_path $libricss_path --tool_path $script_path --asr_path $asr_path
