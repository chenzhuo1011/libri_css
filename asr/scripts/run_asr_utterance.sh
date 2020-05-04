#!/bin/bash

file=$1
outdir=$2
text=$3
graphdir=$4


#graphdir=/data/zhuc/libricss/opencss

while IFS= read line
do

session=`echo $line |awk -F"/" '{print $NF}' |awk -F".zip" '{print $1}'`

wav=$line

srcdir=$outdir/$session/LM_tgsmall
tgtdir=$outdir/$session/LM_fglarge

mkdir -p $srcdir $tgtdir

python $graphdir/pykaldi2/decode.py -config $graphdir/configs/decode_960.yaml \
-data_path $wav \
-batch_size 20   \
-model_path $graphdir/pykaldi2/exp/tr960_blstm_3x512_dp02.lr2e-4/model.mmi.tar \
-prior_path $graphdir/librispeech/s5/exp/tri6b/final.occs  \
-out_file $srcdir/loglikes.ark


graphdir=$graphdir/librispeech/s5/exp/tri6b/graph_tgsmall
alidir=$graphdir/librispeech/s5/exp/tri6b

latgen-faster-mapped-parallel --num-threads=12 --min-active=200 --max-active=7000 --max-mem=50000000 --beam=15 --lattice-beam=8 --acoustic-scale=0.1 --allow-partial=true --word-symbol-table=$graphdir/words.txt $alidir/final.mdl $graphdir/HCLG.fst "ark:$srcdir/logli
kes.ark" ark:$srcdir/lat.ark > $srcdir/decode.1.log 2>&1

wait

$graphdir/local/lmrescore_const_arpa.sh $graphdir/librispeech/s5/data/lang_test_tgsmall\
$graphdir/librispeech/s5/data/lang_test_fglarge $srcdir $tgtdir

$graphdir/local/score_opencss.sh $text $graphdir/librispeech/s5/data/lang_test_fglarge $tgtdir

done <"$file"
