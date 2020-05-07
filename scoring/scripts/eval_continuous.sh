#!/bin/bash

decode_path=$1

eval_script=./python/asclite_libricss_batch.py
python $eval_script --decode_root $decode_path --sctkpath $SCTKPATH/bin
