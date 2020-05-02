#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys
import os
import logging
import datetime
import re
from collections import defaultdict, OrderedDict


def main(args):
    logger = logging.getLogger('{} ({})'.format(__name__, os.path.basename(__file__)))
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s: %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)


    # Create an output directory. 
    outputdir = os.path.dirname(os.path.abspath(args.output_stm))
    os.makedirs(outputdir, exist_ok=True)

    # Read the input STM. Comment lines are stripped off.
    lines = []
    comments = []
    header = True
    with open(args.input_stm) as f:
        for line in f.readlines():
            if line[:2] != ';;':
                lines.append(line.strip())
                header = False
            else:
                if header:
                    comments.append(line.strip())

        #lines = [ line.strip() for line in f.readlines() if line[:2] != ';;' ]

    # Create a pattern for matching.
    ptrn = re.compile('(\S+)\s+(\S+)\s+(\S+)\s+([0-9\.]+)\s+([0-9\.]+)\s+(\S+)')
    #Speech006 1 candacem 0.00 16.00 <O,06,F> IGNORE_TIME_SEGMENT_IN_SCORING    

    # Group the lines according to speaker ID.
    txs = defaultdict(list)
    spkr_attributes = OrderedDict()
    for line in lines:
        match = ptrn.match(line)
        if match is None:
            logger.error('Non-compliant lines: {}'.format(line))
            sys.exit(1)

        mtg = match.group(1)
        mic = match.group(2)
        spkr = match.group(3)
        start = float(match.group(4))
        end = float(match.group(5))
        aux = match.group(6)
        txs[spkr].append( (start, end, line) )

        spkr_attributes[spkr] = (mtg, mic, aux)


    # Get a sorted version of the segments to ignore. 
    ignore_segments = sorted(args.ignore_segment, key=lambda x: x[0])
    for i in range(len(ignore_segments)-1):
        if ignore_segments[i][1] >= ignore_segments[i+1][0]:
            logger.error('Provided segments are overlapping.')
            sys.exit(1)

    # Walk through the transcriptions and remove all utterances overlapping with the segments to ignore. 
    tmp = defaultdict(list)
    for ignore_start, ignore_end in ignore_segments:
        for spkr in txs:
            for utt_start, utt_end, trs in txs[spkr]:
                if utt_end <= ignore_start or utt_start >= ignore_end:
                    tmp[spkr].append( (utt_start, utt_end, trs) )
    txs = tmp

    # Insert IGNORE_TIME_SEGMENT_IN_SCORING directive at an appropriate place. 
    tmp = {}    
    for spkr in txs:
        mtg, mic, aux = spkr_attributes[spkr]

        trs_list = txs[spkr] + [(ignore_start, ignore_end, '{} {} {} {:.2f} {:.2f} {} IGNORE_TIME_SEGMENT_IN_SCORING'.format(mtg, mic, spkr, ignore_start, ignore_end, aux)) 
                                for ignore_start, ignore_end in ignore_segments]
        tmp[spkr] = sorted(trs_list, key=lambda x:x[0])
    txs = tmp

    # Output the new transcriptions. The order of the speakers is kept unchanged. 
    with open(args.output_stm, 'w') as f:
        # Subset information lines
        print(';; Modified {}'.format(datetime.datetime.now()), file=f)
        print(';;', file=f)
        for line in comments:
            print(line, file=f)

        for spkr in spkr_attributes:
            for _, _, line in txs[spkr]:
                print(line, file=f)                                                





    logger.info('Done.')



def make_argparse():
    parser = argparse.ArgumentParser(description='Insert IGNORE_TIME_SEGMENT_IN_SCORING segments to an STM file.')

    # Set up an argument parser.
    parser.add_argument('--input_stm', metavar='<path>', required=True, 
                        help='Input STM file.')
    parser.add_argument('--output_stm', metavar='<path>', required=True, 
                        help='Output STM file.')
    parser.add_argument('--ignore_segment', type=float, metavar='<float>', nargs=2, action='append', 
                        help='Beginning and ending times of a segment to ignore. This can be specified multiple times.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
