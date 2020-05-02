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

    

def main(args):
    logger = logging.getLogger('{} ({})'.format(__name__, os.path.basename(__file__)))
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s: %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    if args.refversion is not None:
        suffix = '_V{}'.format(args.refversion)
    else:
        suffix = ''

    if args.ignore_overlap:
        noverlaps = 1
        ctmfile = '{}/test_si_single{}.ctm'.format(args.decodedir, suffix)
    else:
        ctmfile = '{}/test_si{}.ctm'.format(args.decodedir, suffix)
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
        elif args.meeting == 'Speech011':
            noverlaps = 3
        elif args.meeting == 'Speech012':
            noverlaps = 9
        elif args.meeting == 'Speech013':
            noverlaps = 4
        elif args.meeting == 'Speech016':
            noverlaps = 4
        elif args.meeting == 'Speech019':
            noverlaps = 6
        elif args.meeting == 'Speech020':
            noverlaps = 6
        elif args.meeting == 'Speech099':
            noverlaps = 4
        elif args.meeting == 'Speech093':
            noverlaps = 6  # 8
        elif args.meeting == 'Speech109':
            noverlaps = 6  # 11
        elif args.meeting == 'Speech126':
            noverlaps = 6  # 11
    
    origctm = '{}/{}'.format(args.decodedir, args.ctmfile)
    shutil.copy2(origctm, ctmfile)

    stmfile = 'refs/{}/{}_nochannel{}.stm'.format(args.meeting, args.meeting, suffix)


    with tempfile.TemporaryDirectory(dir='.') as tmpdir:
        tmp_stm = os.path.join(tmpdir, 'ref.stm')
        tmp_ctm = os.path.join(tmpdir, 'test_si{}.ctm'.format(suffix))

        failed = False

        _glmfile = os.path.relpath(args.glmfile, start=args.sctkpath)
        _stmfile = os.path.relpath(stmfile, start=args.sctkpath)
        _ctmfile = os.path.relpath(ctmfile, start=args.sctkpath)
        _tmp_stm = os.path.relpath(tmp_stm, start=args.sctkpath)
        _tmp_ctm = os.path.relpath(tmp_ctm, start=args.sctkpath)
        

        if platform.system() == 'Windows':
            reldecodedir = os.path.relpath(args.decodedir)

            with cd(args.sctkpath):
                cmd = 'bash -c "dos2unix ./csrfilt.sh; ./csrfilt.sh -i stm -t ref -dh {} < {} > {}"'.format(_glmfile, _stmfile, _tmp_stm)
                runcmd(cmd)
                cmd = 'bash -c "./csrfilt.sh -i ctm -t hyp -dh {} < {} > {}"'.format(_glmfile, _ctmfile, _tmp_ctm)
                runcmd(cmd)
            cmd = r'bash -c "{}/asclite -f 6 -O {} -h {} ctm {} -r {} stm -adaptive-cost -time-prune 400 -word-time-align 400 -memory-limit 8 -difficulty-limit 8 -F -D -overlap-limit {} -memory-compression 256 -force-memory-compression -o sum rsum sgml"'.format(args.sctkpath, reldecodedir.replace('\\', '/'), tmp_ctm, args.meeting, tmp_stm, noverlaps)
            runcmd(cmd)            
                
        elif platform.system() == 'Linux':
            with cd(args.sctkpath):
                cmd = 'dos2unix ./csrfilt.sh; ./csrfilt.sh -i stm -t ref -dh {} < {} > {}'.format(_glmfile, _stmfile, _tmp_stm)
                runcmd(cmd)
                cmd = './csrfilt.sh -i ctm -t hyp -dh {} < {} > {}'.format(_glmfile, _ctmfile, _tmp_ctm)
                runcmd(cmd)
                
            cmd = r'{}/asclite -f 6 -O {} -h {} ctm {} -r {} stm -adaptive-cost -time-prune 400 -word-time-align 400 -memory-limit 8 -difficulty-limit 8 -F -D -overlap-limit {} -memory-compression 256 -force-memory-compression -o sum rsum sgml'.format(args.sctkpath, args.decodedir, tmp_ctm, args.meeting, tmp_stm, noverlaps)
            runcmd(cmd)            

        else:
            failed = True
            

    cmd = cmd.replace('\\', '/')

    if failed:
        import sys
        logger.error('Error: Only Windows and Linux supported.')
        sys.exit(1)

    logger.info('Done.')



def make_argparse():
    parser = argparse.ArgumentParser(description='Score SR output with asclite.')

    # Set up an argument parser.
    parser.add_argument('--decodedir', metavar='<dir>', 
                        help='Directory where ctm file is retrieved.')
    parser.add_argument('--meeting', choices=['Speech006', 'Speech007', 'Speech008', 'Speech009', 'Speech010', 'Speech011', 'Speech012', 'Speech013', 'Speech016', 'Speech019', 'Speech020', 'Speech093', 'Speech099', 'Speech109', 'Speech126'],  
                        help='Meeting name that appears in the CTM file.')
    parser.add_argument('--sctkpath', metavar='<path>', default=r'./bin/sctk-2.4.10',
                        help='Path to asclite.')
    parser.add_argument('--ctmfile', metavar='<file>', default='test.ctm', 
                        help='CTM file name to be scored.')
    parser.add_argument('--glmfile', metavar='<file>', default=r'./refs/en20040920.glm',
                        help='GLM file for text normalization.')    
    parser.add_argument('--ignore_overlap', action='store_true',
                        help='Score for only single-speaker segments.')
    parser.add_argument('--refversion', metavar='<ver string>', 
                        help='Reference version.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
