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

    ptrn = re.compile('^(.+)_(\d\.\d_\d\.\d)_(.+)$')

    for subdir in subdirs:
        #--inputfile \\air-speech2\UserData\tayoshio\OpenCSSMini\OpenCSSMini_mmi_clean460\TJIANWU_MCPIT_2.4_0.8_overlap_ratio_0.0_sil0.1_0.5_session0_actual0.0\LM_fglarge\12_0.0.ctm 
        #--outputdir \\air-speech2\UserData\tayoshio\OpenCSSMini\TJIANWU_MCPIT\2.4_0.8\overlap_ratio_0.0_sil0.1_0.5_session0_actual0.0\reco\ 
        #--session_name OpenCSS_OVLP0.0_SIL0.1_0.5_SESS0_ACTUAL0.0#

        srcdir = os.path.join(args.inputdir, subdir, 'LM_fglarge')
        if not os.path.isdir(srcdir):
            continue

        m = ptrn.match(subdir)
        if m is None:
            raise RuntimeError('Invalid subdir name: {}'.format(subdir))

        method_name = m.group(1)
        config_name = m.group(2)
        session_name = m.group(3)

        tgtdir = os.path.join(args.outputdir, method_name, config_name, session_name, args.model_name)

        # overlap_ratio_0.0_sil0.1_0.5_session0_actual0.0
        fields = session_name.split('_')
        if len(fields) != 7:
            raise RuntimeError('Invalid session name: {}'.format())

        overlap = float(fields[2])
        silence = (float(fields[3].replace('sil', '')), float(fields[4]))
        session_id = fields[5].replace('session', '')
        actual = fields[6].replace('actual', '')

        #OpenCSS_OVLP0.0_SIL0.1_0.5_SESS0_ACTUAL0.0
        mtgname = 'OpenCSS_OVLP{}_SIL{}_{}_SESS{}_ACTUAL{}'.format(overlap, silence[0], silence[1], session_id, actual)

        ctmfiles = glob.glob(os.path.join(srcdir, '*.ctm'))

        for srcfile in ctmfiles:
            opts = []
            opts.append('--inputfile {}'.format(srcfile))
            opts.append('--outputdir {}'.format(tgtdir))
            opts.append('--session_name {}'.format(mtgname))

            execute_python_script('opencss_ctm2ctm', ' '.join(opts).split())



def make_argparse():
    parser = argparse.ArgumentParser(description='Convert a TSV file to an STM file.')

    # Set up an argument parser.
    parser.add_argument('--inputdir', metavar='<path>', required=True,
                        help='Input SCP file.')
    parser.add_argument('--outputdir', metavar='<path>', required=True, 
                        help='Output STM file to be created.')
    parser.add_argument('--model_name', metavar='<str>', required=True, 
                        help='AM name.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
