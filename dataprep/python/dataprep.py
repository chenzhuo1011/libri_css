#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, glob, tqdm, zipfile
import soundfile as sf



# Extract the first channel audio. 
def save_wav(source_path, tgt_path, mics=[0, 1, 2, 3, 4, 5, 6]):
    for item in glob.glob(source_path+'/*.wav'):
        s, f = sf.read(item)
        fname = os.path.basename(item)
        sf.write(tgt_path + '/' + fname, s[:, mics], f)



def main(args):
    os.makedirs(args.tgtpath, exist_ok=True)

    conditions = ('0L','0S','OV10','OV20','OV30','OV40')
    for cond in tqdm.tqdm(conditions):
        meeting = glob.glob(os.path.join(args.srcpath, cond, 'overlap*'))
        for meet in meeting:
            # Extract the signals of the selected microphones. 
            meeting_name = os.path.basename(meet)
            source_data_path = os.path.join(meet, 'record', 'segments')
            tgt_data_path = os.path.join(args.tgtpath, meeting_name)

            os.makedirs(tgt_data_path, exist_ok=True)
            save_wav(source_data_path, tgt_data_path, mics=args.mics)



def make_argparse():
    parser = argparse.ArgumentParser(description='Reorganize LibriCSS data.')

    parser = argparse.ArgumentParser()
    parser.add_argument('--srcpath', metavar='<path>', required=True, 
                        help='Original LibriCSS data path.')
    parser.add_argument('--tgtpath', metavar='<path>', required=True, 
                        help='Destination path.')
    parser.add_argument('--mics', type=int, metavar='<#mics>', nargs='+', default=[0, 1, 2, 3, 4, 5, 6], 
                        help='Microphone indices.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)


