import sys
import glob,os,tqdm
import soundfile as sf
import numpy as np
import zipfile
import argparse

def save_single_channel_wav(source_path,tgt_path):
	for item in glob.glob(source_path+'/*.wav'):
		s,f=sf.read(item)
		fname=os.path.basename(item)
		sf.write(tgt_path+'/'+fname,s[:,0],f)
		

# In[13]:
def main(args):
	
	base_dir=args.data_path
	asr_path=args.asr_path
	baseline_dir_utt=os.path.join(base_dir, 'monaural','utterances')
	zip_dir=os.path.join(base_dir,'baseline','utterance','zip')
	os.makedirs(zip_dir,exist_ok=True)
	tool_path=args.tool_path

	decoding_cmd=os.path.join(base_dir,'baseline','utterance','decoding_cmd')
	decoding_result=os.path.join(base_dir,'baseline','utterance','decoding_result')

	os.makedirs(decoding_cmd,exist_ok=True)
	os.makedirs(decoding_result,exist_ok=True)

	transcription_file=os.path.join(base_dir, 'monaural','utterance_transcription.txt')

	zip_file=zip_dir+'/'+'utterances.zip'
	zipf = zipfile.ZipFile(zip_file, 'w')

	all_wav=glob.glob(os.path.join(baseline_dir_utt,'*','*.wav'))

	for item in all_wav:
		info=item.split('/')
		fname=info[-2]+'_'+info[-1]
		zipf.write(item,arcname=fname)


	with open(decoding_cmd+'/meeting_list.scp','w') as f:
		f.write(zip_file+'\n')
	#  then make the decoding command
	os.makedirs(os.path.join('..','exp'),exist_ok=True)

	with open(os.path.join('..','exp','decode_raw_utterance.sh'),'w') as f:
		cmd='sh '+ tool_path +'/run_asr_utterance.sh ' + decoding_cmd+'/meeting_list.scp '+decoding_result+' '+transcription_file+' '+asr_path
		f.write(cmd+'\n')




def make_argparse():
	parser = argparse.ArgumentParser(description='Generate ASR input files')

	parser = argparse.ArgumentParser()
	parser.add_argument('--data_path', required=True)
	parser.add_argument('--tool_path', required=True)
	parser.add_argument('--asr_path', required=True)

	return parser
	# parser = argparse.ArgumentParser()
	# parser.add_argument('-base_path', default='/data/zhuc/libricss/for_release/', type=str, required=False)
	# parser.add_argument('-tool_path', default='/data/zhuc/libricss/opencss/pykaldi2/example/OpenCSS', type=str, required=False)
	# args = parser.parse_args()



if __name__ == '__main__':
	parser = make_argparse()
	args = parser.parse_args()
	main(args)
