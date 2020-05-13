import collections
import contextlib
import sys
import wave
import webrtcvad
import glob,os,tqdm
from get_vad import *
import soundfile as sf
import numpy as np
import zipfile
import argparse


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
	#         print(s.shape,st,en)
			this_seg=s[st:en]
			fname=save_path+'/'+meeting_name+'_'+audio_name+'_'+str(st)+'_'+str(en)+'.wav'
			sf.write(fname,this_seg,16000)
		return
		
def get_zip(zip_dir,meeting,res_path):
#     zip_dir=res_path+'/zip'
	os.makedirs(zip_dir,exist_ok=True)
	zipf = zipfile.ZipFile(zip_dir+'/'+meeting+'.zip', 'w')
	t1=glob.glob(res_path+'/'+meeting+'/*.wav')
	for ite in tqdm.tqdm(t1):
		fname=os.path.basename(ite)
		zipf.write(ite,arcname=fname)
	return zip_dir+'/'+meeting+'.zip'


def make_argparse():
	parser = argparse.ArgumentParser(description='Generate ASR input files')

	parser = argparse.ArgumentParser()
	parser.add_argument('--data_path', required=True)
	parser.add_argument('--tool_path', required=True)
	parser.add_argument('--asr_path', required=True)

	parser.add_argument('--cut_margin', default=0.25, type=float)
	parser.add_argument('--merge_margin', default=1, type=float)
	# parser.add_argument('--outfile', default=r'', type=str, required=False)

	return parser


def main(args):
	
	cut_margin=args.cut_margin
	merge_margin=args.merge_margin
	tool_path=args.tool_path
	asr_path=args.asr_path
	base_path=args.data_path

	vad_dir=os.path.join(base_path,'separated_evaluation','continuous','vad')
	zip_dir=os.path.join(base_path,'separated_evaluation','continuous','zip')
	os.makedirs(vad_dir,exist_ok=True)
	os.makedirs(zip_dir,exist_ok=True)

	decoding_cmd=os.path.join(base_path,'separated_evaluation','continuous','decoding_cmd')
	decoding_result=os.path.join(base_path,'separated_evaluation','continuous','decoding_result')
	os.makedirs(decoding_cmd,exist_ok=True)
	os.makedirs(decoding_result,exist_ok=True)
    
	wav_dir=os.path.join(base_path,'separation_result','continuous_separation')

	seg=segmentor(merge_margin,cut_margin,res_path=vad_dir,vad_setting=0)

	meeting_list=glob.glob(os.path.join(wav_dir,'overlap_ratio*'))
	meeting_list=[os.path.basename(x) for x in meeting_list]

	# print(meeting_list)

	with open(os.path.join(decoding_cmd,'meeting_list.scp'),'w') as f:

		for meeting in meeting_list:
			all_wav=glob.glob(os.path.join(wav_dir,meeting,'*.wav'))
			
			for audio in tqdm.tqdm(all_wav):
				seg.get_segment(audio,meeting)
			zip_file=get_zip(zip_dir,meeting,vad_dir)

			f.write(zip_dir+'/'+meeting+'.zip'+'\n')
	#  then make the decoding command

	os.makedirs(os.path.join('..','exp'),exist_ok=True)
	with open(os.path.join('..','exp','decode_separate_continuous.sh'),'w') as f:
		cmd = 'sh '+ args.tool_path +'/run_asr_continuous.sh ' + decoding_cmd + '/meeting_list.scp ' + decoding_result + ' . ' +asr_path
		f.write(cmd+'\n')

if __name__ == '__main__':
	parser = make_argparse()
	args = parser.parse_args()
	main(args)