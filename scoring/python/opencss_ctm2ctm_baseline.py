#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, sys, os, re
from collections import defaultdict


def main(args):
    ptrn = re.compile('(\S+_\d+)\D\S*\D(\d+)_(\d+)')
    hyps = defaultdict(list)

    fs = 16000

    # Read the input CTM file. 
    with open(args.inputfile) as f:
        for line in f:
            line = line.strip()
            fields = line.split(' ')
            if len(fields) != 5:
                raise RuntimeError('Number of fields must be five: {} in {}'.format(line, args.inputfile))

            start_time = float(fields[2])
            dur = float(fields[3])
            word =fields[4]

            m = ptrn.match(fields[0])
            if m is None:
                raise RuntimeError('The first field format is invalid: {} in {}'.format(line, args.inputfile))

            segment_name = m.group(1)
            session_name = args.session_name + '_' + segment_name.upper().replace('_', '')

            start_time += float(m.group(2)) / fs
            
            hyps[segment_name].append( (session_name, 0, start_time, dur, word, 0) )


    # Write the sorted version to the output CTM file. 
    for segment in hyps:
        outputdir = os.path.join(args.outputdir, os.path.splitext(os.path.basename(args.inputfile))[0])
        outputfile = os.path.join(outputdir, segment + '.ctm')

        os.makedirs(outputdir, exist_ok=True)

        curhyps = sorted(hyps[segment], key=lambda hyp: hyp[2])

        with open(outputfile, 'w') as f:
            for mtg, ch, start, dur, wrd, conf in curhyps:
                print('{} {} {:.2f} {} {} {}'.format(mtg, ch, start, dur, wrd, conf), file=f)




def make_argparse():
    parser = argparse.ArgumentParser(description='Sort lines of a CTM file in time-ascending order.')

    # Set up an argument parser.
    parser.add_argument('--inputfile', metavar='<path>', required=True, 
                        help='Input CTM file.')
    parser.add_argument('--outputdir', metavar='<path>', required=True, 
                        help='Output directory.')
    parser.add_argument('--session_name', metavar='<str>', required=True, 
                        help='Session name.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
