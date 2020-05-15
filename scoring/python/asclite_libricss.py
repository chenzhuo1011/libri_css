#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, fnmatch, platform, shutil, tempfile, subprocess, glob, re



class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)
        os.environ['PATH'] += ':.'

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)
        


def runcmd(cmd):
    print('')
    print(runcmd)
    print('')
    subprocess.check_call(cmd.replace('\\', '/'), shell=True)

    

def run_asclite(orig_stmfile, orig_ctmfile, orig_glmfile, sctkpath, noverlaps):
    # tmpdir = 'temp0'
    # os.makedirs(tmpdir, exist_ok=True)
    # if True:

    # Work in a temp directory. 
    with tempfile.TemporaryDirectory(dir='.') as tmpdir:
        print(f'Tempoerary directory created: {tmpdir}')

        # Copy the stm and ctm files to the temp directory. 
        stmfile = os.path.join(tmpdir, 'orig.stm')
        shutil.copy2(orig_stmfile, stmfile)

        ctmfile = os.path.join(tmpdir, 'orig.ctm')
        shutil.copy2(orig_ctmfile, ctmfile)

        segment_name = os.path.splitext(os.path.basename(orig_ctmfile))[0]

        glmfile = os.path.join(tmpdir, 'orig.glm')
        shutil.copy2(orig_glmfile, glmfile)

        # Note that the stm/ctm files are text-normalized before use. 
        tmp_stm = os.path.join(tmpdir, 'test.stm')
        tmp_ctm = os.path.join(tmpdir, 'test.ctm')

        failed = False

        _glmfile = os.path.relpath(glmfile, start=sctkpath)
        _stmfile = os.path.relpath(stmfile, start=sctkpath)
        _ctmfile = os.path.relpath(ctmfile, start=sctkpath)
        _tmp_stm = os.path.relpath(tmp_stm, start=sctkpath)
        _tmp_ctm = os.path.relpath(tmp_ctm, start=sctkpath)

        if platform.system() == 'Windows':
            reldecodedir = os.path.relpath(tmpdir)

            with cd(sctkpath):
                cmd = 'bash -c "dos2unix ./csrfilt.sh; ./csrfilt.sh -i stm -t ref -dh {} < {} > {}"'.format(_glmfile, _stmfile, _tmp_stm)
                runcmd(cmd)
                cmd = 'bash -c "./csrfilt.sh -i ctm -t hyp -dh {} < {} > {}"'.format(_glmfile, _ctmfile, _tmp_ctm)
                runcmd(cmd)
            cmd = r'bash -c "{}/asclite -f 4 -O {} -h {} ctm {} -r {} stm -adaptive-cost -time-prune 400 -word-time-align 400 -memory-limit 8 -difficulty-limit 8 -F -D -overlap-limit {} -memory-compression 256 -force-memory-compression -o sum rsum sgml"'.format(sctkpath, reldecodedir.replace('\\', '/'), tmp_ctm, segment_name, tmp_stm, noverlaps)
            runcmd(cmd)            
                
        elif platform.system() == 'Linux':
            with cd(sctkpath):
                cmd = './csrfilt.sh -i stm -t ref -dh {} < {} > {}'.format(_glmfile, _stmfile, _tmp_stm)
                runcmd(cmd)
                cmd = './csrfilt.sh -i ctm -t hyp -dh {} < {} > {}'.format(_glmfile, _ctmfile, _tmp_ctm)
                runcmd(cmd)
                
            cmd = r'{}/asclite -f 4 -O {} -h {} ctm {} -r {} stm -adaptive-cost -time-prune 400 -word-time-align 400 -memory-limit 8 -difficulty-limit 8 -F -D -overlap-limit {} -memory-compression 256 -force-memory-compression -o sum rsum sgml'.format(sctkpath, tmpdir, tmp_ctm, segment_name, tmp_stm, noverlaps)
            runcmd(cmd)            

        else:
            failed = True

        # Copy the result files. 
        for ext in ('raw', 'sgml', 'sys'):
            src = os.path.join(tmpdir, 'test.ctm.{}'.format(ext))
            dst = os.path.join(os.path.dirname(orig_ctmfile), '{}.{}'.format(os.path.basename(orig_ctmfile), ext))
            shutil.copy2(src, dst)

    if failed:
        raise RuntimeError('Only Windows and Linux are supported.')



def main(args):
    ptrn = re.compile('.*(overlap_ratio[^/]+)')

    if args.ignore_overlap:
        noverlaps = 1
    else:
        noverlaps = 8

    # overlap_ratio_0.0_sil0.1_0.5_session0_actual0.0; or 
    # overlap_ratio_0.0_sil0.1_0.5_session0_actual0.0/**
    m = ptrn.match( os.path.abspath(args.decodedir) )
    if m is None:
        raise RuntimeError('Decoding directory name does not match the expected format: {}'.format(args.decodedir))
    session = m.group(1)

    ctmfiles = glob.glob(os.path.join(args.decodedir, '*.ctm'))
    for ctmfile in ctmfiles:
        basename = os.path.splitext(os.path.basename(ctmfile))[0]
        stmfile = os.path.join(args.refdir, session, basename + '.stm')

        if not os.path.isfile('{}.sys'.format(ctmfile)):
            run_asclite(stmfile, ctmfile, args.glmfile, args.sctkpath, noverlaps)



    # Summarize the results. 

    # | Speaker           |  #Snt   #Wrd |    Corr     Sub     Del     Ins     Err  S.Err |    NCE    |
    # | Sum               |    15    160 |     97      38      25       0      63       8 |  -26.119  |
    ptrn = re.compile('\|\s*Sum\s*\|\s*\d+\s+(\d+)\s*\|(.+)\|.+\|$')

    rawfiles = glob.glob(os.path.join(args.decodedir, '*.raw'))
    nwords = 0
    ncorr = 0
    nsub = 0
    ndel = 0
    nins = 0
    nerr = 0

    for rawfile in rawfiles:
        found = False
        with open(rawfile, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                m = ptrn.match(line)

                if m is not None:
                    nwords += int(m.group(1))
                    fields = m.group(2).strip().split()
                    if len(fields) != 6:
                        raise RuntimeError('Invalid format: {}'.format(line))
                    ncorr += int(fields[0])
                    nsub += int(fields[1])
                    ndel += int(fields[2])
                    nins += int(fields[3])
                    nerr += int(fields[4])

                    found = True

        if not found:
            raise RuntimeError('Summary line not found in {}'.format(rawfile))

    wer = float(nerr) / float(nwords) * 100

    outputfile = os.path.join(args.decodedir, 'summary.txt')
    with open(outputfile, 'w') as f:
        print('#words\t%wer', file=f)
        print('{}\t{:.2f}'.format(nwords, wer), file=f)



def make_argparse():
    scoring_base = os.path.dirname(os.path.dirname(__file__))    

    parser = argparse.ArgumentParser(description='Score SR output with asclite.')

    # Set up an argument parser.
    parser.add_argument('--decodedir', metavar='<dir>', required=True, 
                        help='Directory where CTM files are retrieved.')
    parser.add_argument('--sctkpath', metavar='<path>', required=True, 
                        help='Path to asclite.')
    parser.add_argument('--refdir', metavar='<dir>', default=os.path.join(scoring_base, 'references'),  
                        help='Directory where STM files are retrieved.')
    parser.add_argument('--glmfile', metavar='<file>', default=os.path.join(scoring_base, 'en20040920.glm'),
                        help='GLM file for text normalization.')    
    parser.add_argument('--ignore_overlap', action='store_true',
                        help='Score for only single-speaker segments.')
 
    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
