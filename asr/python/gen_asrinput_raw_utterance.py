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
	baseline_dir_utt=os.path.join(base_dir, 'monaural','utterances')
	zip_dir=os.path.join(base_dir,'baseline','utterance','zip')
	os.makedirs(zip_dir,exist_ok=True)
	tool_path=args.tool_path

	decoding_cmd=os.path.join(base_dir,'baseline','utterance','decoding_cmd')
	decoding_result=os.path.join(base_dir,'baseline','utterance','decoding_result')
	os.makedirs(decoding_cmd,exist_ok=True)
	os.makedirs(decoding_result,exist_ok=True)

	all_lines=[]
	condition=['0L','0S','OV10','OV20','OV30','OV40']

	for cond in condition:
		all_trans=glob.glob(os.path.join(base_dir,cond,'*'))
		for meeting in all_trans:
			meeting_id=os.path.basename(meeting)

			with open(os.path.join(base_dir,cond,meeting_id,'transcription','utterance_transcription.txt'),'r') as f:
				for line in f.readlines():
					utterances_id,trans=line.rstrip().split('\t')
					all_lines.append(meeting_id+'_'+utterances_id[:-4]+'\t'+trans)
				
	with open(os.path.join(decoding_cmd,'all_transcription.scp'),'w') as f:
		for item in all_lines:
			f.write(item+'\n')


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

	with open(decoding_cmd+'/decode_batch_960.sh','w') as f:
		cmd='sh '+ tool_path +'/decode_batch_960_utt.sh ' + decoding_cmd+'/meeting_list.scp '+decoding_result+' '+os.path.join(decoding_cmd,'all_transcription.scp')
		f.write(cmd+'\n')




def make_argparse():
	parser = argparse.ArgumentParser(description='Generate ASR input files')

	parser = argparse.ArgumentParser()
	parser.add_argument('--data_path', required=True)
	parser.add_argument('--tool_path', required=True)

	return parser
	# parser = argparse.ArgumentParser()
	# parser.add_argument('-base_path', default='/data/zhuc/libricss/for_release/', type=str, required=False)
	# parser.add_argument('-tool_path', default='/data/zhuc/libricss/opencss/pykaldi2/example/OpenCSS', type=str, required=False)
	# args = parser.parse_args()



if __name__ == '__main__':
	parser = make_argparse()
	args = parser.parse_args()
	main(args)
