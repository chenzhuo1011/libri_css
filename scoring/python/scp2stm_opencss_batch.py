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
    sessions = os.listdir(args.inputdir)

    for sess in sessions:
        srcdir = os.path.join(args.inputdir, sess)
        if not os.path.isdir(srcdir):
            continue

        srcdir = os.path.join(srcdir, 'ff')
        scpfiles = glob.glob(os.path.join(srcdir, '*.scp'))

        for scpfile in scpfiles:
            tgtdir = os.path.join(args.outputdir, sess)
            os.makedirs(tgtdir, exist_ok=True)

            basename = os.path.splitext(os.path.basename(scpfile))[0]
            stmfile = os.path.join(tgtdir, basename + '.stm')

            # overlap_ratio_0.0_sil0.1_0.5_session0_actual0.0
            fields = sess.split('_')
            if len(fields) != 7:
                raise RuntimeError('Invalid session name: {}'.format())

            overlap = float(fields[2])
            silence = (float(fields[3].replace('sil', '')), float(fields[4]))
            session_id = fields[5].replace('session', '')
            actual = fields[6].replace('actual', '')
            segment = basename.replace('_', '').upper()

            #OpenCSS_OVLP0.0_SIL0.1_0.5_SESS0_ACTUAL0.0_SEG0
            #O0.0_S0.1_0.5_S0_A0.0_S0
            mtgname = 'OpenCSS_OVLP{}_SIL{}_{}_SESS{}_ACTUAL{}_{}'.format(overlap, silence[0], silence[1], session_id, actual, segment)
            mtgname_short = 'O{}_S{}_{}_S{}_A{}_{}'.format(overlap, silence[0], silence[1], session_id, actual, segment.replace('SEG', 'S'))

            opts = []
            opts.append('--scpfile {}'.format(scpfile))
            opts.append('--stmfile {}'.format(stmfile))
            opts.append('--meeting_name {} {}'.format(mtgname, mtgname_short))

            execute_python_script('scp2stm_opencss', ' '.join(opts).split())



def make_argparse():
    parser = argparse.ArgumentParser(description='Convert a TSV file to an STM file.')

    # Set up an argument parser.
    parser.add_argument('--inputdir', metavar='<path>', required=True,
                        help='Input SCP file.')
    parser.add_argument('--outputdir', metavar='<path>', required=True, 
                        help='Output STM file to be created.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
