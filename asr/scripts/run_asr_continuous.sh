#!/bin/bash

file=$1
outdir=$2
text=$3
asrdir=$4
#asrdir=/data/zhuc/libricss/opencss


while IFS= read line
do

session=`echo $line |awk -F"/" '{print $NF}' |awk -F".zip" '{print $1}'`

wav=$line

srcdir=$outdir/$session/LM_tgsmall
tgtdir=$outdir/$session/LM_fglarge

mkdir -p $srcdir $tgtdir

python $asrdir/pykaldi2/decode.py -config $asrdir/pykaldi2/example/OpenCSS/configs/decode_960.yaml \
-data_path $wav \
-batch_size 20   \
-model_path $asrdir/pykaldi2/exp/tr960_blstm_3x512_dp02.lr2e-4/model.mmi.tar \
-prior_path $asrdir/librispeech/s5/exp/tri6b/final.occs  \
-out_file $srcdir/loglikes.ark


graphdir=$asrdir/librispeech/s5/exp/tri6b/graph_tgsmall
alidir=$asrdir/librispeech/s5/exp/tri6b

latgen-faster-mapped-parallel --num-threads=12 --min-active=200 --max-active=7000 --max-mem=50000000 --beam=15 --lattice-beam=8 --acoustic-scale=0.1 --allow-partial=true --word-symbol-table=$graphdir/words.txt $alidir/final.mdl $graphdir/HCLG.fst "ark:$srcdir/logli
kes.ark" ark:$srcdir/lat.ark > $srcdir/decode.1.log 2>&1

wait

$asrdir/pykaldi2/example/OpenCSS/local/lmrescore_const_arpa.sh $asrdir/librispeech/s5/data/lang_test_tgsmall\
$asrdir/librispeech/s5/data/lang_test_fglarge $srcdir $tgtdir

$asrdir/pykaldi2/example/OpenCSS/local/score_ctm.sh $asrdir/librispeech/s5/data/lang_test_fglarge $tgtdir $alidir/final.mdl

done <"$file"
