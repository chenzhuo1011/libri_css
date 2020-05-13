import sys
import glob,os,tqdm
import soundfile as sf
import numpy as np
import zipfile
import argparse



def make_argparse():
	parser = argparse.ArgumentParser(description='Generate ASR input files')

	parser = argparse.ArgumentParser()
	parser.add_argument('--data_path', required=True)
	parser.add_argument('--tool_path', required=True)
	parser.add_argument('--asr_path', required=True)
# parser.add_argument('-base_path', default='/data/zhuc/libricss/for_release/', type=str, required=False)
# 	parser.add_argument('-tool_path', default='/data/zhuc/libricss/opencss/pykaldi2/example/OpenCSS', type=str, required=False)
	return parser


def main(args):

	base_dir=args.data_path
	tool_path=args.tool_path
	asr_path=args.asr_path

	baseline_dir_utt=os.path.join(base_dir,'separated_evaluation','utterance')
	wav_dir=os.path.join(base_dir,'separation_result','utterance_separation')
	zip_dir=os.path.join(baseline_dir_utt,'zip')
	decoding_cmd=os.path.join(baseline_dir_utt,'decoding_cmd')
	decoding_result=os.path.join(baseline_dir_utt,'decoding_result')

	os.makedirs(zip_dir,exist_ok=True)
	os.makedirs(wav_dir,exist_ok=True)
	os.makedirs(decoding_cmd,exist_ok=True)
	os.makedirs(decoding_result,exist_ok=True)

	# os.chdir(base_dir)
	all_wav=glob.glob(os.path.join(wav_dir,'*.wav'))
	
	# first get all transcription

	print('load transcription dictionary')# which is put in the zip folder
	

	with open(os.path.join(wav_dir, 'utterance_transcription.txt'),'r') as f:
		lines=[line.rstrip() for line in f.readlines()] 


	all_transcription={}

	for item in lines:
		utt_id,trans=item.split('\t')
		all_transcription[utt_id]=trans
	
	# print(lines[:10])
#  form decoding transcription

	lines=[]
	for item in all_wav:
		fname=os.path.basename(item)[:-4]
		source_name='_'.join(fname.split('_')[:-1])
		trans=all_transcription[source_name]
		lines.append(os.path.basename(item)[:-4]+'\t'+trans)

	print(lines[:10])
	with open(os.path.join(decoding_cmd,'transcription.scp'),'w') as f:
		for item in lines:
			f.write(item +'\n')
	
	print('zipping wave')
	zip_file=os.path.join(zip_dir,'utterances.zip')
	zipf = zipfile.ZipFile(zip_file, 'w')

	all_wav=glob.glob(os.path.join(wav_dir,'*.wav'))
	for item in all_wav:
		fname=os.path.basename(item)
		zipf.write(item,arcname=fname)

	print('make decoding command')
	with open(decoding_cmd+'/meeting_list.scp','w') as f:
		f.write(zip_file+'\n')

	os.makedirs(os.path.join('..','exp'),exist_ok=True)
	print(os.getcwd())
	print(os.path.join('..','exp'))
	with open(os.path.join('..','exp','decode_separate_utterance.sh'),'w') as f:
		cmd='sh '+ tool_path +'/run_asr_utterance.sh ' + decoding_cmd+'/meeting_list.scp '+decoding_result+' '+os.path.join(decoding_cmd,'transcription.scp')+' '+asr_path
		f.write(cmd+'\n')


if __name__ == '__main__':
	parser = make_argparse()
	args = parser.parse_args()
	main(args)