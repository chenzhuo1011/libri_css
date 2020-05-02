#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import logging
import subprocess
import fnmatch
import platform
import shutil
import re



def main(args):
    logger = logging.getLogger('{} ({})'.format(__name__, os.path.basename(__file__)))
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s: %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    tmpdir = os.path.join(args.decodedir, 'tmp')
    os.makedirs(tmpdir, exist_ok=True)

    if args.refversion is not None:
        suffix = '_V{}'.format(args.refversion)
    else:
        suffix = ''

    stmfile = 'refs/{}/{}_nochannel{}.stm'.format(args.meeting, args.meeting, suffix)

    # Run scoring against all segments. 
    ctmfile_all = '{}/sagwer{}.ctm'.format(tmpdir, suffix)
    if args.meeting == 'Speech006':
        noverlaps = 6
    elif args.meeting == 'Speech007':
        noverlaps = 7
    elif args.meeting == 'Speech008':
        noverlaps = 5
    elif args.meeting == 'Speech009':
        noverlaps = 4
    elif args.meeting == 'Speech010':
        noverlaps = 4
    elif args.meeting == 'Speech013':
        noverlaps = 4
    elif args.meeting == 'Speech016':
        noverlaps = 4
    
    origctm = '{}/{}'.format(args.decodedir, args.ctmfile)
    shutil.copy2(origctm, ctmfile_all)

    if platform.system() == 'Windows':
        cmd = r'bash -c "{} -f 6 -O {} -h {} ctm {} -r {} stm -adaptive-cost -time-prune 400 -word-time-align 400 -memory-limit 8 -difficulty-limit 8 -F -D -overlap-limit {} -memory-compression 256 -force-memory-compression -o sum rsum sgml"'.format(args.asclitepath, tmpdir, ctmfile_all, args.meeting, stmfile, noverlaps)
    elif platform.system() == 'Linux':
        cmd = r'{} -f 6 -O {} -h {} ctm {} -r {} stm -adaptive-cost -time-prune 400 -word-time-align 400 -memory-limit 8 -difficulty-limit 8 -F -D -overlap-limit {} -memory-compression 256 -force-memory-compression -o sum rsum sgml'.format(args.asclitepath, tmpdir, ctmfile_all, args.meeting, stmfile, noverlaps)
    else:
        import sys
        logger.error('Only Windows and Linux supported.')
        sys.exit(1)

    cmd = cmd.replace('\\', '/')

    subprocess.check_call(cmd, shell=True)


    # Run scoring against single-speaker segments. 
    ctmfile_single = '{}/sagwer_single{}.ctm'.format(tmpdir, suffix)
    noverlaps = 1
    shutil.copy2(origctm, ctmfile_single)

    if platform.system() == 'Windows':
        cmd = r'bash -c "{} -f 6 -O {} -h {} ctm {} -r {} stm -adaptive-cost -time-prune 400 -word-time-align 400 -memory-limit 8 -difficulty-limit 8 -F -D -overlap-limit {} -memory-compression 256 -force-memory-compression -o sum rsum sgml"'.format(args.asclitepath, tmpdir, ctmfile_single, args.meeting, stmfile, noverlaps)
    elif platform.system() == 'Linux':
        cmd = r'{} -f 6 -O {} -h {} ctm {} -r {} stm -adaptive-cost -time-prune 400 -word-time-align 400 -memory-limit 8 -difficulty-limit 8 -F -D -overlap-limit {} -memory-compression 256 -force-memory-compression -o sum rsum sgml'.format(args.asclitepath, tmpdir, ctmfile_single, args.meeting, stmfile, noverlaps)
    else:
        import sys
        logger.error('Only Windows and Linux supported.')
        sys.exit(1)

    cmd = cmd.replace('\\', '/')

    subprocess.check_call(cmd, shell=True)

    # Calculate the WERs for the single-speaker and overlapped segments. 
    p = re.compile('\s*\|\s*Sum\s*\|\s*[0-9]+\s*([0-9]+)\s*\|\s*[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+\s+([0-9]+)\s+[0-9]+\s*\|')
    # | Sum               |   1011   6632 |   3808    1333    1491      77    2901     604 |   0.471   |

    rawfile = '{}.raw'.format(ctmfile_all)
    with open(rawfile) as f:
        for l in f.readlines():
            m = p.match(l)
            if m is not None:
                wrd_all = int(m.group(1))
                err_all = int(m.group(2))

    rawfile = '{}.raw'.format(ctmfile_single)
    with open(rawfile) as f:
        for l in f.readlines():
            m = p.match(l)
            if m is not None:
                wrd_single = int(m.group(1))
                err_single = int(m.group(2))

    wrd_overlap = wrd_all - wrd_single
    err_overlap = err_all - err_single

    output_file = '{}/sagwer{}.txt'.format(args.decodedir, suffix)

    with open(output_file, 'w') as f:
        print('segments without overlaps: wer={:6.2f}, nwords={}'.format(err_single / wrd_single * 100, wrd_single), file=f)
        print('segments with overlaps   : wer={:6.2f}, nwords={}'.format(err_overlap / wrd_overlap * 100, wrd_overlap), file=f)
        print('all segments             : wer={:6.2f}, nwords={}'.format(err_all / wrd_all * 100, wrd_all), file=f)

    logger.info('Done.')



def make_argparse():
    parser = argparse.ArgumentParser(description='Calculate speaker-agnostic WERs. This generates a file named sagwer.txt or sagwer_V?.txt.')

    # Set up an argument parser.
    parser.add_argument('--decodedir', metavar='<dir>', 
                        help='Directory where ctm file is retrieved.')
    parser.add_argument('--meeting', choices=['Speech006', 'Speech007', 'Speech008', 'Speech009', 'Speech010', 'Speech013', 'Speech016'],  
                        help='Meeting name that appears in the CTM file.')
    parser.add_argument('--asclitepath', metavar='<path>', default=r'/home/tayoshio/GitHub/sctk/sctk-2.4.10/bin/asclite',
                        help='Path to asclite.')
    parser.add_argument('--ctmfile', metavar='<file>', default='test.ctm', 
                        help='CTM file name to be scored.')
    parser.add_argument('--refversion', type=int, metavar='<ver#>', 
                        help='Reference version number.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
