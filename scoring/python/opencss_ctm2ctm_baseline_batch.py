#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, sys, glob, re, importlib

scriptdir = os.path.dirname((os.path.abspath(__file__)))
sys.path.append(scriptdir)



def execute_python_script(script, args):
    print(args)
    script_as_module = importlib.import_module(script)
    p = script_as_module.make_argparse()
    namespace = p.parse_args(args)
    script_as_module.main( namespace )



def main(args):
    subdirs = os.listdir(args.inputdir)

    for subdir in subdirs:
        if args.data == 'farfield' and '_ff_single' not in subdir:
            continue
        if args.data == 'closetalk' and '_ct' not in subdir:
            continue

        srcdir = os.path.join(args.inputdir, subdir, 'LM_fglarge')
        if not os.path.isdir(srcdir):
            continue

        # overlap_ratio_0.0_sil0.1_0.5_session0_actual0.0_ff_single
        fields = subdir.split('_')
        if args.data == 'farfield' and len(fields) != 9:
            continue
        if args.data == 'closetalk' and len(fields) != 8:
            continue

        overlap = float(fields[2])
        silence = (float(fields[3].replace('sil', '')), float(fields[4]))
        session_id = fields[5].replace('session', '')
        actual = fields[6].replace('actual', '')

        if args.data == 'farfield':
            session_name = '_'.join(fields[:-2])
            tgtdir = os.path.join(args.outputdir, 'FarField', 'CenterMic', session_name, args.model_name)
        else:
            session_name = '_'.join(fields[:-1])
            tgtdir = os.path.join(args.outputdir, 'CloseTalk', 'Mixed', session_name, args.model_name)

        #OpenCSS_OVLP0.0_SIL0.1_0.5_SESS0_ACTUAL0.0
        mtgname = 'OpenCSS_OVLP{}_SIL{}_{}_SESS{}_ACTUAL{}'.format(overlap, silence[0], silence[1], session_id, actual)

        ctmfiles = glob.glob(os.path.join(srcdir, '*.ctm'))

        for srcfile in ctmfiles:
            opts = []
            opts.append('--inputfile {}'.format(srcfile))
            opts.append('--outputdir {}'.format(tgtdir))
            opts.append('--session_name {}'.format(mtgname))

            execute_python_script('opencss_ctm2ctm_baseline', ' '.join(opts).split())



def make_argparse():
    parser = argparse.ArgumentParser(description='Convert a TSV file to an STM file.')

    # Set up an argument parser.
    parser.add_argument('--inputdir', metavar='<path>', default=r'\\ccpsofsep\Scratch2\users\zhuc\large_cts\baseline\baseline_seg',
                        help='Input directory root.')
    parser.add_argument('--outputdir', metavar='<path>', required=True, 
                        help='Output directory root.')
    parser.add_argument('--model_name', metavar='<str>', required=True, 
                        help='AM name.')
    parser.add_argument('--data', choices=['farfield', 'closetalk'], required=True, 
                        help='Data type')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
