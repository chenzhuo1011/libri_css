#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, sys, os, glob, re
from collections import defaultdict


def sortout_results(ctmfile, tgtdir):
    print('')
    print('{}'.format(ctmfile))
    print('    -> {}'.format(tgtdir))

    os.makedirs(tgtdir, exist_ok=True)

    # overlap_ratio_0.0_sil2.9_3.0_session0_actual0.0_segment_5_195199_384160 1 1.770 0.420 REMEMBER
    ptrn = re.compile('^overlap_ratio_([\d\.]+)_sil([\d\.]+)_([\d\.]+)_session(\d+)_actual([\d\.]+)_segment_(\d+)_(\d+)_(\d+)$')

    results = defaultdict(list)

    with open(ctmfile) as f:
        for line in f:
            fields = line.split()
            if len(fields) == 5:
                confidence = 1.0
            elif len(fields) == 6:
                confidence = float(fields[-1].strip())
            else:
                raise RuntimeError('Invalid CTM line in {}: {}'.format(ctmfile, line))

            if int(fields[1].strip()) != 1:
                raise RuntimeError('Channel index is supposed to be 1.')

            start = float(fields[2].strip())
            duration = float(fields[3].strip())
            word = fields[4].strip()

            m = ptrn.match(fields[0].strip())
            if m is None:
                raise RuntimeError('Invalid CTM line in {}: {}'.format(ctmfile, line))

            ratio = m.group(1)
            sil = (m.group(2), m.group(3))
            session = m.group(4)
            actual = m.group(5)
            segment = 'segment_{}'.format(m.group(6))
            cut = (float(m.group(7)) / 16000, float(m.group(8)) / 16000)

            tmp = {'word': word, 
                   'confidence': confidence, 
                   'channel': 0, 
                   'start': start + cut[0], 
                   'duration': duration, 
                   'session': 'OpenCSS_OVLP{}_SIL{}_{}_SESS{}_ACTUAL{}_SEG{}'.format(ratio, sil[0], sil[1], session, actual, m.group(6))
                   }
            results[segment].append(tmp)

    for segment in results:
        outputfile = os.path.join(tgtdir, '{}.ctm'.format(segment))

        res = sorted(results[segment], key=lambda x: x['start'])
        with open(outputfile, 'w') as f:
            for w in res:
                print('{} {} {:.2f} {} {} {}'.format(w['session'], w['channel'], w['start'], w['duration'], w['word'], w['confidence']), file=f)


def main(args):
    conditions = os.listdir(args.inputdir)
    for cond in conditions:
        decdir = os.path.join(args.inputdir, cond, 'LM_fglarge')
        ctmfiles = glob.glob(os.path.join(decdir, '*.ctm'))

        for ctmfile in ctmfiles:
            cfg = os.path.splitext(os.path.basename(ctmfile))[0]
            tgtdir = os.path.join(args.outputdir, cfg, cond)

            sortout_results(ctmfile, tgtdir)




    # # Write the sorted version to the output CTM file. 
    # for segment in hyps:
    #     outputdir = os.path.join(args.outputdir, os.path.splitext(os.path.basename(args.inputfile))[0])
    #     outputfile = os.path.join(outputdir, segment + '.ctm')

    #     os.makedirs(outputdir, exist_ok=True)

    #     curhyps = sorted(hyps[segment], key=lambda hyp: hyp[2])

    #     with open(outputfile, 'w') as f:
    #         for mtg, ch, start, dur, wrd, conf in curhyps:
    #             print('{} {} {:.2f} {} {} {}'.format(mtg, ch, start, dur, wrd, conf), file=f)




def make_argparse():
    parser = argparse.ArgumentParser(description='Sort lines of a CTM file in time-ascending order.')

    # Set up an argument parser.
    parser.add_argument('--inputdir', metavar='<path>', required=True, 
                        help='Raw ASR result directory.')
    parser.add_argument('--outputdir', metavar='<path>', required=True, 
                        help='Output directory.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
