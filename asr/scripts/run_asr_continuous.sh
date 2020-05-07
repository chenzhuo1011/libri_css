#!/bin/bash

file=$1
outdir=$2
text=$3


pykaldi2=$PYKALDIPATH
amdir=$AMPATH

while IFS= read line
do

session=`echo $line |awk -F"/" '{print $NF}' |awk -F".zip" '{print $1}'`

wav=$line

srcdir=$outdir/$session/LM_tgsmall
tgtdir=$outdir/$session/LM_fglarge

mkdir -p $srcdir $tgtdir

python $pykaldi2/decode.py -config $pykaldi2/example/OpenCSS/configs/decode_960.yaml \
-data_path $wav \
-batch_size 10   \
-model_path $amdir/model.mmi.tar \
-prior_path $amdir/tri6b/final.occs  \
-out_file $srcdir/loglikes.ark


graphdir=$amdir/tri6b/graph_tgsmall
alidir=$amdir/tri6b

echo "running lattice generation ..."
latgen-faster-mapped-parallel --num-threads=12 --min-active=200 --max-active=7000 --max-mem=50000000 --beam=15 --lattice-beam=8 --acoustic-scale=0.1 --allow-partial=true --word-symbol-table=$graphdir/words.txt $alidir/final.mdl $graphdir/HCLG.fst "ark:$srcdir/loglikes.ark" ark:$srcdir/lat.ark > $srcdir/decode.1.log 2>&1

wait

$pykaldi2/example/OpenCSS/local/lmrescore_const_arpa.sh $amdir/lang_test_tgsmall \
   $amdir/lang_test_fglarge $srcdir $tgtdir

$pykaldi2/example/OpenCSS/local/score_ctm.sh $amdir/lang_test_fglarge $tgtdir $alidir/final.mdl

done <"$file"
