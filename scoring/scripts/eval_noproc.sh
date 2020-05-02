#!/bin/bash

# Programs
PYTHON=python

# Scripts
eval_script=./python/asclite_libricss_batch.py
sctk_path=../../sctk/bin

# Input directory
decode_dir=../sample

$PYTHON $eval_script --decode_root $decode_dir --sctkpath $sctk_path --decode_cfgs 13_0.0
