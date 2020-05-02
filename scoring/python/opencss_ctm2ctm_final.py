#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, sys, glob, re, importlib
from collections import defaultdict

scriptdir = os.path.dirname((os.path.abspath(__file__)))
sys.path.append(scriptdir)



def execute_python_script(script, args):
    print(args)
    script_as_module = importlib.import_module(script)
    p = script_as_module.make_argparse()
    namespace = p.parse_args(args)
    script_as_module.main( namespace )



def main(args):
    fs = 16000

    srcdir = os.path.join(args.inputdir, 'LM_fglarge')
    if not os.path.isdir(srcdir):
        raise RuntimeError('{} not found'.format(srcdir))

    ctmfiles = glob.glob(os.path.join(srcdir, '*.ctm'))

    for srcfile in ctmfiles:
        print('Processing {}'.format(srcfile))

        decparam = os.path.splitext(os.path.basename(srcfile))[0]

        hyps = defaultdict(list)

        # Read the input CTM file. 
        with open(srcfile) as f:
            for line in f:
                line = line.strip()

                # Split the whole line. 
                fields = line.split(' ')
                if len(fields) != 5:
                    raise RuntimeError('Number of fields must be five: {} in {}'.format(line, srcfile))

                start_time = float(fields[2])
                dur = float(fields[3])
                word =fields[4]
                
                # Split the original session field. 
                #fields = fields[0].split('_')  # overlap_ratio_0.0_sil2.9_3.0_session6_actual0.0_seg_*
                #if len(fields) < 9:
                #    raise RuntimeError('The first field format is invalid: {} in {}'.format(line, srcfile))

                fields = fields[0].split('_')  # overlap_ratio_0.0_sil0.1_0.5_session0_actual0.0_seg_7_0_232639_338560
                if len(fields) != 12 :
                    raise RuntimeError('The first field format is invalid: {} in {}'.format(line, srcfile))                

                start_time += float(fields[-2]) / fs

                session_name = '_'.join(fields[:7])  # overlap_ratio_0.0_sil0.1_0.5_session0_actual0.0
                segment_name = '_'.join(fields[7:9])
                fields = session_name.split('_')
                if len(fields) != 7:
                    raise RuntimeError('Invalid session name: {}'.format())

                overlap = float(fields[2])
                silence = (float(fields[3].replace('sil', '')), float(fields[4]))
                session_id = fields[5].replace('session', '')
                actual = fields[6].replace('actual', '')
                new_session_name = 'OpenCSS_OVLP{}_SIL{}_{}_SESS{}_ACTUAL{}'.format(overlap, silence[0], silence[1], session_id, actual)  #OpenCSS_OVLP0.0_SIL0.1_0.5_SESS0_ACTUAL0.0

                new_session_name = new_session_name + '_' + segment_name.upper().replace('_', '')
            
                hyps[(session_name, segment_name)].append( (new_session_name, 0, start_time, dur, word, 0) )


        # Write the sorted version to the output CTM file. 
        for (session, segment), hyp in hyps.items():
            outputdir = os.path.join(args.outputdir, session, args.model_name, decparam)
            outputfile = os.path.join(outputdir, segment + '.ctm')
            print('\tCreating {}'.format(outputfile))

            os.makedirs(outputdir, exist_ok=True)

            curhyp = sorted(hyp, key=lambda x: x[2])

            with open(outputfile, 'w') as f:
                for mtg, ch, start, dur, wrd, conf in curhyp:
                    print('{} {} {:.2f} {} {} {}'.format(mtg, ch, start, dur, wrd, conf), file=f)



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
