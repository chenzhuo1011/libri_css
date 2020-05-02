#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import logging
import subprocess
import fnmatch
import platform
import shutil
import tempfile
from collections import defaultdict


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)
        
        
        
def runcmd(cmd):
    subprocess.check_call(cmd.replace('\\', '/'), shell=True)


    
def make_consistent_ref_hyp(origstm, stmfile, origctm, ctmfile):
    reftx = defaultdict(list)
    with open(origstm) as f:
        for line in f:
            if line.strip()[:2] != ';;':
                channel = line.split(' ')[1]
                reftx[channel].append(line.strip())
    ref_channels = set(reftx.keys())

    hyptx = defaultdict(list)
    with open(origctm) as f:
        for line in f:
            channel = line.split(' ')[1]
            hyptx[channel].append(line.strip())
    hyp_channels = set(hyptx.keys())

    missing_from_hyp = ref_channels - hyp_channels
    missing_from_ref = hyp_channels - ref_channels
    all_channels = sorted(list(ref_channels | hyp_channels))

    for channel in missing_from_hyp:
        hyptx[channel].append('{} {} 0.0 0.1 dummy 0'.format(args.meeting, channel))
    for channel in missing_from_ref:
        reftx[channel].append('{} {} guest_false_alarm 0.0 0.1 <O,{},U> dummy'.format(args.meeting, channel, args.meeting[-2:]))

    with open(stmfile, 'w') as f:
        for channel in all_channels:
            for line in reftx[channel]:
                print(line, file=f)
    with open(ctmfile, 'w') as f:
        for channel in all_channels:
            for line in hyptx[channel]:
                print(line, file=f)



def main(args):
    logger = logging.getLogger('{} ({})'.format(__name__, os.path.basename(__file__)))
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s: %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    #if platform.system() == 'Windows':
    #    if os.path.isabs(args.decodedir):
    #        import sys
    #        logger.error('Error: For Windows systems, only relative path is allowed.')
    #        sys.exit(1)
    reldecodedir = os.path.relpath(args.decodedir)


    # Determine the ref file to contrast the hyp file against. 
    if args.refversion is not None:
        suffix = '_V{}'.format(args.refversion)
    else:
        suffix = ''


    # Modify the ref and hyp files so that make their channels consistent. 
    origstm = 'refs/{}/{}{}.stm'.format(args.meeting, args.meeting, suffix)
    stmfile = os.path.join(args.decodedir, 'test_sa{}.stm'.format(suffix))
    origctm = os.path.join(args.decodedir, args.ctmfilename)
    ctmfile = os.path.join(args.decodedir, 'test_sa{}.ctm'.format(suffix))

    make_consistent_ref_hyp(origstm, stmfile, origctm, ctmfile)


    # Work in a temp folder. 
    with tempfile.TemporaryDirectory(dir='.') as tmpdir:
        tmp_stm = os.path.join(tmpdir, 'ref.stm')
        tmp_ctm = os.path.join(tmpdir, 'test_sa{}.ctm'.format(suffix))

        failed = False

        _glmfile = os.path.relpath(args.glmfile, start=args.sctkpath)
        _stmfile = os.path.relpath(stmfile, start=args.sctkpath)
        _ctmfile = os.path.relpath(ctmfile, start=args.sctkpath)
        _tmp_stm = os.path.relpath(tmp_stm, start=args.sctkpath)
        _tmp_ctm = os.path.relpath(tmp_ctm, start=args.sctkpath)

        # Run evaluation for Windows.
        if platform.system() == 'Windows':
            with cd(args.sctkpath):
                cmd = 'bash -c "dos2unix ./csrfilt.sh; ./csrfilt.sh -i stm -t ref -dh {} < {} > {}"'.format(_glmfile, _stmfile, _tmp_stm)
                runcmd(cmd)
                cmd = 'bash -c "./csrfilt.sh -i ctm -t hyp -dh {} < {} > {}"'.format(_glmfile, _ctmfile, _tmp_ctm)
                runcmd(cmd)
            cmd = r'bash -c "{}/sclite -f 0 -O {} -h {} ctm {} -r {} stm -D -o sum dtl pra"'.format(args.sctkpath, reldecodedir.replace('\\', '/'), tmp_ctm, args.meeting, tmp_stm)
            runcmd(cmd)

        # Or Linux. 
        elif platform.system() == 'Linux':
            with cd(args.sctkpath):
                cmd = 'dos2unix ./csrfilt.sh; ./csrfilt.sh -i stm -t ref -dh {} < {} > {}'.format(_glmfile, _stmfile, _tmp_stm)
                runcmd(cmd)
                cmd = './csrfilt.sh -i ctm -t hyp -dh {} < {} > {}'.format(_glmfile, _ctmfile, _tmp_ctm)
                runcmd(cmd)
            cmd = r'{}/sclite -f 0 -O {} -h {} ctm {} -r {} stm -D -o sum dtl pra'.format(args.sctkpath, reldecodedir.replace('\\', '/'), tmp_ctm, args.meeting, tmp_stm)
            runcmd(cmd)

        # Other OSes are not supported. 
        else:
            failed = True

    if failed:
        import sys
        logger.error('Error: Only Windows and Linux supported.')
        sys.exit(1)

    logger.info('Done.')



def make_argparse():
    parser = argparse.ArgumentParser(description='Score SR output with sclite.')

    # Set up an argument parser.
    parser.add_argument('--decodedir', metavar='<dir>', 
                        help='Folder where ctm file is retrieved. For Windows systems, only relative path is accepted, which means that folders on other drives cannot be used.')
    parser.add_argument('--ctmfilename', metavar='<str>', default='test.ctm',
                        help='CTM file name.')
    parser.add_argument('--meeting', choices=['Speech006', 'Speech007', 'Speech008', 'Speech009', 'Speech010', 'Speech011', 'Speech012', 'Speech013', 'Speech016', 'Speech019', 'Speech020', 'Speech093', 'Speech099', 'Speech109'],  
                        help='Meeting name that appears in the CTM file.')
    parser.add_argument('--sctkpath', metavar='<path>', default=r'./bin/sctk-2.4.10',
                        help='Path to sclite.')
    parser.add_argument('--glmfile', metavar='<file>', default=r'./refs/en20040920.glm',
                        help='GLM file for text normalization.')
    parser.add_argument('--refversion', metavar='<version string>',
                        help='Reference version.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
