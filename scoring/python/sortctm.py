#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys
import os
import re



def main(args):
    ptrn = re.compile('(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)')

    # Create the output directory. 
    outputdir = os.path.dirname(os.path.abspath(args.outputctm))
    os.makedirs(outputdir, exist_ok=True)

    # Read in the CTM file. 
    hyps = []
    with open(args.inputctm) as f:
        for line in f:
            match = ptrn.match(line.strip())

            if match is not None:
                hyps.append( (match.group(1), match.group(2), float(match.group(3)), match.group(4), match.group(5), match.group(6)) )
    
    # Sort by the start time. 
    hyps = sorted(hyps, key=lambda hyp: hyp[2])

    # Write the sorted version to the output CTM file. 
    with open(args.outputctm, 'w') as f:
        for mtg, ch, start, dur, wrd, conf in hyps:
            if args.remove_channel:
                print('{} 0 {:.2f} {} {} {}'.format(mtg, start, dur, wrd, conf), file=f)
            else:
                print('{} {} {:.2f} {} {} {}'.format(mtg, ch, start, dur, wrd, conf), file=f)

    print('[sorting] Done.')



def make_argparse():
    parser = argparse.ArgumentParser(description='Sort lines of a CTM file in time-ascending order.')

    # Set up an argument parser.
    parser.add_argument('--inputctm', metavar='<path>', required=True, 
                        help='Input CTM file.')
    parser.add_argument('--outputctm', metavar='<path>', required=True, 
                        help='Output CTM file to be created.')
    parser.add_argument('--remove_channel', action='store_true', 
                        help='Set the channel to zero.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
