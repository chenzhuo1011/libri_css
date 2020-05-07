#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
from collections import defaultdict



def main(args):
    # Read all results. 
    subdirs = os.listdir(args.inputdir)
    res = defaultdict(list)

    for subdir in subdirs:
        #overlap_ratio_0.0_sil0.1_0.5_session0_actual0.0
        subdir_fields = subdir.split('_')
        if len(subdir_fields) != 7:
            raise RuntimeError('Invalid subdirectory name: {}'.format(subdir))

        tgtdir = os.path.join(args.inputdir, subdir, args.decode_cfg)
        if not os.path.isdir(tgtdir):
            continue

        fname = os.path.join(tgtdir, 'summary.txt')        
        if not os.path.isfile(fname):
            raise RuntimeError('File not found: {}'.format(fname))

        with open(fname) as f:
            found = False
            for lineno, line in enumerate(f):
                if lineno == 1:
                    fields = line.strip().split()

                    if len(fields) != 2:
                        raise RuntimeError('Invalid WER summary file: {}'.format(fname))
                    
                    nwords = int(fields[0])
                    wer = float(fields[1])
                    found = True

        if not found:
            raise RuntimeError('Invalid WER summary file: {}'.format(fname))

        cond = '_'.join(subdir_fields[:-2])
        res[cond].append( (nwords, wer) )

    
    # Print a report. 
    condmap = {'overlap_ratio_0.0_sil0.1_0.5': '0S', 
               'overlap_ratio_0.0_sil2.9_3.0': '0L', 
               'overlap_ratio_10.0_sil0.1_1.0': '10', 
               'overlap_ratio_20.0_sil0.1_1.0': '20', 
               'overlap_ratio_30.0_sil0.1_1.0': '30', 
               'overlap_ratio_40.0_sil0.1_1.0': '40'}
    verb_conds = sorted(list(res.keys()))

    print('')
    print('Result Summary')
    print('--------------')
    print('Condition: %WER')
    for cond in verb_conds:
        nwords = 0
        nerrs = 0
        for nw, ne in res[cond]:
            nwords += nw
            nerrs += ne/100 * nw
        wer = nerrs / nwords * 100
        print('{:9}: {:.1f}'.format(condmap[cond], wer))
        # print(wer)



def make_argparse():
    parser = argparse.ArgumentParser(description='Generate a WER report.')

    # Set up an argument parser.
    parser.add_argument('--inputdir', metavar='<dir>', required=True)
    parser.add_argument('--decode_cfg', metavar='<str>', default='', 
                        help='Decoder configuration (optional).')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)