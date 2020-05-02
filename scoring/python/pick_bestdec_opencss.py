#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os


    
def main(args):
    subdirs = os.listdir(args.tgtdir)

    for subdir in subdirs:
        summary_file = os.path.join(args.tgtdir, subdir, 'summary.txt')

        if not os.path.isfile(summary_file):
            continue

        with open(summary_file) as f:
            for lineno, line in enumerate(f):
                if lineno == 1:
                    fields = line.split()
                    print('{}\t: {}\t: {}'.format(subdir, fields[0], fields[1]))



def make_argparse():
    parser = argparse.ArgumentParser(description='Score SR output with asclite.')

    # Set up an argument parser.
    parser.add_argument('--tgtdir', metavar='<dir>', required=True, 
                        help='Target directory.')
 
    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
