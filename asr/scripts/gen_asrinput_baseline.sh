#!/bin/bash

PYTHON=python

# args
prep_script=./python/gen_asrinput_baseline.py
libricss_path=/data/zhuc/libricss
script_path=./scripts

$PYTHON $prep_script --data_path $libricss_path --tool_path $script_path

