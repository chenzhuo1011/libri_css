#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, datetime, copy, re
from collections import defaultdict


def read_scp(scpfile, encoding='utf-8'):
    # 51	51571	7127	DID NOT THE DANCING AMUSE YOU NO
    ptrn = re.compile('^(\d+)\s+(\d+)\s+(\d+)\s+(\S.*)$')

    trs = defaultdict(list)
    fs = 16000

    # Load the file and read the transcriptions one by one. 
    with open(scpfile, encoding=encoding) as infile:

        for lineno, line in enumerate(infile):
            m = ptrn.match(line)

            if m is None:
                raise RuntimeError('Invalid line at {} in {}: {}'.format(lineno, scpfile, line))

            start_time = float(m.group(1)) / fs
            end_time = float(m.group(2)) / fs
            spkr = m.group(3)
            tr = m.group(4)

            # Append the obtained reference transcription. 
            trs[spkr].append((start_time, end_time, tr))

    return trs




def main(args):
    # Create an output directory. 
    outputdir = os.path.dirname(os.path.abspath(args.stmfile))
    os.makedirs(outputdir, exist_ok=True)


    # Read the TSV file. 
    trs = read_scp(args.scpfile)

    all_speakers = list(trs.keys())

    # Get the meeting name. 
    mtg_name = args.meeting_name[0]
    mtg_shortname = args.meeting_name[1]

    gender = 'N'


    # Open the STM file. 
    with open(args.stmfile, 'w') as outfile:
        # Subset information lines. 
        print(';; Reference file for {}, generated {}'.format(mtg_name, datetime.datetime.now()), file=outfile)

        for spk in all_speakers:
            for start_time, end_time, sent in trs[spk]:
                print('{} {} {} {:.2f} {:.2f} <O,{},{}> {}'.format(mtg_name, 
                                                                    0, 
                                                                    spk, 
                                                                    start_time, 
                                                                    end_time, 
                                                                    mtg_shortname, 
                                                                    gender, 
                                                                    sent), file=outfile)



    print('Done.')



def make_argparse():
    parser = argparse.ArgumentParser(description='Convert a TSV file to an STM file.')

    # Set up an argument parser.
    parser.add_argument('--scpfile', metavar='<path>', required=True,
                        help='Input SCP file.')
    parser.add_argument('--stmfile', metavar='<path>', required=True, 
                        help='Output STM file to be created.')
    parser.add_argument('--meeting_name', metavar=('<long name>', '<short name>'), nargs=2, required=True, 
                        help='Name of the session.')
    parser.add_argument('--endsil', type=float, metavar='<float>', default=0.0, 
                        help='Silence duration inserted at the end of each utterance.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
