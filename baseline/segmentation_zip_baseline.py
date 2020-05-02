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
		
def get_zip(zip_dir,meeting,result_dir):
#     zip_dir=res_path+'/zip'
	os.makedirs(zip_dir,exist_ok=True)
	zipf = zipfile.ZipFile(zip_dir+'/'+meeting+'.zip', 'w')

	t1=glob.glob(result_dir+'/'+meeting+'/*.wav')

	for ite in tqdm.tqdm(t1):
		fname=os.path.basename(ite)
		zipf.write(ite,arcname=fname)
	return zip_dir+'/'+meeting+'.zip'

def save_single_channel_wav(source_path,tgt_path):
	for item in glob.glob(source_path+'/*.wav'):
		s,f=sf.read(item)
		fname=os.path.basename(item)
		sf.write(tgt_path+'/'+fname,s[:,0],f)
		

import argparse
# In[13]:
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-cut_margin', default=0.25, type=float, required=False)
	parser.add_argument('-merge_margin', default=1, type=float, required=False)
	parser.add_argument('-outfile', default=r'', type=str, required=False)
	parser.add_argument('-base_path', default='/data/zhuc/libricss/for_release', type=str, required=False)
	parser.add_argument('-tool_path', default='/data/zhuc/libricss/opencss/pykaldi2/example/OpenCSS', type=str, required=False)

	args = parser.parse_args()

	cut_margin=args.cut_margin
	merge_margin=args.merge_margin
	tool_path=args.tool_path
	base_path=args.base_path

	baseline_dir_seg=os.path.join(base_path,'baseline','segments')	
	os.makedirs(baseline_dir_seg,exist_ok=True)


# firstly create the single channel recordings for continous
	condition=['0L','0S','OV10','OV20','OV30','OV40']
	for cond in tqdm.tqdm(condition):
		meeting=glob.glob(os.path.join(base_path,cond,'overlap*'))
		for meet in meeting:
			meeting_name=os.path.basename(meet)
			source_data_path=os.path.join(meet,'record','segments')
			tgt_data_path = os.path.join(baseline_dir_seg,'single_channel_recording',meeting_name)
			os.makedirs(tgt_data_path,exist_ok=True)
			save_single_channel_wav(source_data_path,tgt_data_path)

# test one meeting

	decoding_cmd=os.path.join(base_path,'baseline','segments','decoding_cmd')
	decoding_result=os.path.join(base_path,'baseline','segments','decoding_result')
	os.makedirs(decoding_cmd,exist_ok=True)
	os.makedirs(decoding_result,exist_ok=True)
	
	result_dir=os.path.join(base_path,'baseline','segments','vad')
	zip_dir=os.path.join(result_dir,'zip')
	os.makedirs(zip_dir,exist_ok=True)
	seg=segmentor(merge_margin,cut_margin,res_path=result_dir,vad_setting=0)

	meeting_list=glob.glob(os.path.join(base_path,'*','overlap_ratio*'))
	meeting_list=[os.path.basename(x) for x in meeting_list]

	with open(decoding_cmd+'/meeting_list.scp','w') as f:

		for meeting in meeting_list:

			data_dir=os.path.join(base_path,'baseline','segments','single_channel_recording',meeting_name)

			all_wav=glob.glob(data_dir+'/*.wav')
			for audio in tqdm.tqdm(all_wav):
				seg.get_segment(audio,meeting)
			zip_file=get_zip(zip_dir,meeting,result_dir)
			# with open(decoding_cmd+'/meeting_list.scp','w') as f:
			f.write(zip_file+'\n')
		#  then make the decoding command

	with open(decoding_cmd+'/decode_batch_960.sh','w') as f:
		cmd='sh '+ tool_path +'/decode_batch_960.sh ' + decoding_cmd+'/meeting_list.scp '+decoding_result+' .'
		f.write(cmd+'\n')



