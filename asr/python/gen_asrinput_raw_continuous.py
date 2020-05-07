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


# Extract the first channel audio. 
def save_single_channel_wav(source_path, tgt_path):
    for item in glob.glob(source_path+'/*.wav'):
        s, f = sf.read(item)
        fname = os.path.basename(item)
        sf.write(tgt_path + '/' + fname, s[:, 0], f)



def main(args):
    data_path = args.data_path
    asr_path=args.asr_path
    # We wenerate ASR input data under the original data directory. 
    baseline_dir_seg = os.path.join(data_path, 'baseline', 'segments')
    single_channel_dir =  os.path.join(data_path, 'monaural','segments')
    
    os.makedirs(baseline_dir_seg, exist_ok=True)

    # Create some directories. 
    result_dir = os.path.join(baseline_dir_seg, 'vad')
    zip_dir = os.path.join(result_dir, 'zip')
    os.makedirs(zip_dir,exist_ok=True)

    decoding_cmd = os.path.join(baseline_dir_seg, 'decoding_cmd')
    os.makedirs(decoding_cmd, exist_ok=True)

    decoding_result = os.path.join(baseline_dir_seg, 'decoding_result')
    os.makedirs(decoding_result, exist_ok=True)

    # In this baseline script, we create single channel audio files. the single channel data has been step 
    with open(decoding_cmd + '/meeting_list.scp', 'w') as f:
        meeting = glob.glob(os.path.join(single_channel_dir,'overlap*'))
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
    os.makedirs(os.path.join('..','exp'),exist_ok=True)

    with open(os.path.join('..','exp','decode_raw_continuous.sh'),'w') as f:
        cmd = 'sh '+ args.tool_path +'/run_asr_continuous.sh ' + decoding_cmd + '/meeting_list.scp ' + decoding_result + ' . ' +asr_path
        f.write(cmd+'\n')


def make_argparse():
    parser = argparse.ArgumentParser(description='Generate ASR input files')

    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', required=True)
    parser.add_argument('--tool_path', required=True)
    parser.add_argument('--asr_path', required=True)

    parser.add_argument('--cut_margin', default=0.25, type=float)
    parser.add_argument('--merge_margin', default=1, type=float)
    parser.add_argument('--outfile', default=r'', type=str, required=False)

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)


