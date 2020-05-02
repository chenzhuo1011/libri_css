#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, sys, importlib

scriptdir = os.path.dirname((os.path.abspath(__file__)))
sys.path.append(scriptdir)



def execute_python_script(script, args):
    script_as_module = importlib.import_module(script)
    p = script_as_module.make_argparse()
    namespace = p.parse_args(args)
    script_as_module.main( namespace )


    
def main(args):
    subdirs = os.listdir(args.decode_root)

    for subdir in subdirs:
        subdir = os.path.join(args.decode_root, subdir, args.model_name)

        if not os.path.isdir(subdir):
            continue

        if args.decode_cfgs is None:
            decode_cfgs = os.listdir(subdir)
        else:
            decode_cfgs = args.decode_cfgs

        for decode_cfg in decode_cfgs:
            decodedir = os.path.join(subdir, decode_cfg)

            if not os.path.isdir(decodedir):
                continue

            opts = []
            opts.append('--decodedir {}'.format(decodedir))
            opts.append('--sctkpath {}'.format(args.sctkpath))
            execute_python_script('asclite_libricss', ' '.join(opts).split())



def make_argparse():
    parser = argparse.ArgumentParser(description='Score SR output with asclite for LibriCSS.')

    # Set up an argument parser.
    parser.add_argument('--decode_root', metavar='<dir>', required=True, 
                        help='Root of decoding directories.')                        
    parser.add_argument('--sctkpath', metavar='<path>', required=True, 
                        help='Path to asclite.')
    parser.add_argument('--model_name', metavar='<str>', default='mmi_tr960', 
                        help='AM name.')
    parser.add_argument('--decode_cfgs', nargs='+', 
                        help='Decoding configurations. If not specified, all results will be scored.')

 
    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
