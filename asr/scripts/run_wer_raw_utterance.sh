#!/bin/bash

PYTHON=python

# args
prep_script=../python/get_wer.py
libricss_path=/data/zhuc/libricss/for_release
script_path=./scripts
experiment_setup=raw

decode_path=$libricss_path/baseline/utterance/decoding_result/utterances/LM_fglarge
result_path=$libricss_path/baseline/utterance/decoding_result

echo "$PYTHON $prep_script --data_path $libricss_path --decode_path $decode_path --experiment_setup $experiment_setup --result_path $result_path
"

$PYTHON $prep_script --data_path $libricss_path --decode_path $decode_path --experiment_setup $experiment_setup --result_path $result_path


