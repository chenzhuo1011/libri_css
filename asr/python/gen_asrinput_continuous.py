#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, glob, tqdm, zipfile, webrtcvad
import soundfile as sf

from get_vad import *



class segmentor():
    def __init__(self,merge_margin,cut_margin,res_path,vad_setting=0):
        self.merge_margin=merge_margin
        self.cut_margin=cut_margin
        self.vad=webrtcvad.Vad(vad_setting)
        self.sr=16000
        self.res_path=res_path


    def get_segment(self,audio, meeting_name):
        out=get_seg(audio, self.merge_margin,self.vad)
        self.seg_wav(audio,out,meeting_name,margin=self.cut_margin,sr=self.sr)
        return


    def seg_wav(self,audio,segments,meeting_name,margin=0.25,sr=16000):
        s,f=sf.read(audio)
        audio_name=os.path.basename(audio)[:-4]
        save_path=self.res_path+'/'+meeting_name
        os.makedirs(save_path,exist_ok=True)

        for segment in segments:
            st,en=segment
            st=int((st-margin)*sr)
            en=int((en+margin)*sr)
            if st<0:
                    st=0
            if en>s.shape[0] or en<0:
                    en=s.shape[0]

            this_seg=s[st:en]
            fname=save_path+'/'+meeting_name+'_'+audio_name+'_'+str(st)+'_'+str(en)+'.wav'
            sf.write(fname,this_seg,16000)
        return


def get_zip(zip_dir,meeting,result_dir):
    os.makedirs(zip_dir,exist_ok=True)
    zipf = zipfile.ZipFile(zip_dir+'/'+meeting+'.zip', 'w')

    t1=glob.glob(result_dir+'/'+meeting+'/*.wav')

    for ite in tqdm.tqdm(t1):
        fname=os.path.basename(ite)
        zipf.write(ite,arcname=fname)

    return zip_dir+'/'+meeting+'.zip'



def main(args):
    tool_path = os.path.normpath(args.tool_path)
    am_path = os.path.normpath(args.am_path)
    decode_path = os.path.normpath(args.decode_path)

    # Create some directories. 
    result_dir = os.path.join(decode_path, 'vad')
    zip_dir = os.path.join(result_dir, 'zip')
    os.makedirs(zip_dir, exist_ok=True)

    decoding_cmd = os.path.join(decode_path, 'decoding_cmd')
    os.makedirs(decoding_cmd, exist_ok=True)

    decoding_result = os.path.join(decode_path, 'decoding_result')
    os.makedirs(decoding_result, exist_ok=True)

    # In this baseline script, we create single channel audio files. the single channel data has been step 
    with open(decoding_cmd + '/zip_list.scp', 'w') as f:
        meeting = glob.glob(os.path.join(args.input_path, 'overlap*'))
        print(args.input_path)
        for meet in meeting:
            # Extract the first channel signals.            
            meeting_name = os.path.basename(meet)
            # Do segmentation.             
            seg = segmentor(args.merge_margin, args.cut_margin, res_path=result_dir, vad_setting=0)

            all_wav = glob.glob(meet + '/*.wav')
            for audio in tqdm.tqdm(all_wav):
                seg.get_segment(audio, meeting_name)

            # Zip up the segmented files and add the zip location to the output file list. 
            zip_file = get_zip(zip_dir, meeting_name, result_dir)
            f.write(zip_file + '\n')

    # Create an ASR script. 
    with open(os.path.join(decoding_cmd, 'decode.sh'),'w') as f:
        cmd = 'sh {} {} {} . {}'.format(os.path.join(tool_path, 'run_asr_continuous.sh'), 
                                        os.path.join(decoding_cmd, 'zip_list.scp'), 
                                        decoding_result, 
                                        am_path)
        f.write(cmd+'\n')
        if args.multi_stream:
            cmd = 'python {} --with_channel --inputdir {} --outputdir {}'.format(os.path.normpath(os.path.join(tool_path, '../python/sortctm.py')), 
                                                                decoding_result, 
                                                                decoding_result + '.sorted')
        else:
            cmd = 'python {} --inputdir {} --outputdir {}'.format(os.path.normpath(os.path.join(tool_path, '../python/sortctm.py')), 
                                                                decoding_result, 
                                                                decoding_result + '.sorted')
        f.write(cmd+'\n')
        cmd = 'chown -R {}:{} {}'.format(os.getuid(), os.getgid(), decoding_result) 
        f.write(cmd+'\n')
        cmd = 'chown -R {}:{} {}'.format(os.getuid(), os.getgid(), decoding_result + '.sorted') 
        f.write(cmd+'\n')



def make_argparse():
    parser = argparse.ArgumentParser(description='Generate ASR input files')

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', metavar='<path>', required=True, 
                        help='Directory where input audio files are retrieved.')
    parser.add_argument('--decode_path', metavar='<path>', required=True, 
                        help='Directory in which decoding is to be performed')
    parser.add_argument('--tool_path', metavar='<path>', required=True)
    parser.add_argument('--am_path', metavar='<path>', required=True)

    parser.add_argument('--cut_margin', default=0.25, metavar='<float>', type=float, 
                        help='Segmentation parameter.')
    parser.add_argument('--merge_margin', default=1, metavar='<float>', type=float, 
                        help='Segmentation parameter.')

    parser.add_argument('--multi_stream', action='store_true', 
                        help='Set this flag when processing CSS (or multi-stream) outputs.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
