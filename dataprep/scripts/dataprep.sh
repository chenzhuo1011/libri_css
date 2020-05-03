#!/bin/bash

# CHANGE THIS VALUE TO WHERE YOU DOWNLOADED THE LIBRICSS DATA.
LIBRICSS=/data/tayoshio/LibriCSS/orig
# CHANGE THIS VALUE TO WHERE YOU WANT TO DO EXPERIMENTS. 
EXPROOT=/data/tayoshio/LibriCSS/exp
# IF NECESSARY, CHANGE THIS VALUE TO THE PYTHON BINARY YOU WANT TO USE. 
PYTHON=python

prep_script=./python/dataprep.py
mono_path=$EXPROOT/monaural
full_path=$EXPROOT/7ch


# In this example, we generate data for monaural and 7-ch testing.
# If you need 3-ch testing data, you can generate them as "$PYTHON $prep_script --srcpath $LIBRICSS --tgtpath $mono_path --mics 1 3 5".
$PYTHON $prep_script --srcpath $LIBRICSS --tgtpath $full_path
$PYTHON $prep_script --srcpath $LIBRICSS --tgtpath $mono_path --mics 0

