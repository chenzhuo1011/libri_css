#!/bin/bash

PYTHON=python

# args
prep_script=../python/get_wer.py
libricss_path=$EXPROOT/data
experiment_setup=separated

decode_path=$libricss_path/separated_evaluation/utterance/decoding_result/utterance/LM_fglarge
result_path=$libricss_path/separated_evaluation/utterance/decoding_result

echo "$PYTHON $prep_script --data_path $libricss_path --decode_path $decode_path --experiment_setup $experiment_setup --result_path $result_path
"

$PYTHON $prep_script --data_path $libricss_path --decode_path $decode_path --experiment_setup $experiment_setup --result_path $result_path
