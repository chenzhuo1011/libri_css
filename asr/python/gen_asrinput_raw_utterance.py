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
		

def main(args):
	
	tool_path = os.path.normpath(args.tool_path)
	decode_path = os.path.normpath(args.decode_path)
	input_path = os.path.normpath(args.input_path)

	# Create some directories. 

	zip_dir = os.path.join(decode_path, 'zip')
	os.makedirs(zip_dir, exist_ok=True)

	decoding_cmd = os.path.join(decode_path, 'decoding_cmd')
	os.makedirs(decoding_cmd, exist_ok=True)

	decoding_result = os.path.join(decode_path, 'decoding_result')
	os.makedirs(decoding_result, exist_ok=True)

	meeting = glob.glob(os.path.join(input_path, 'overlap*'))
	
	transcription_file=os.path.join(input_path, 'utterance_transcription.txt')

	zip_file=os.path.join(zip_dir,'utterances.zip')
	zipf = zipfile.ZipFile(zip_file, 'w')

	all_wav=glob.glob(os.path.join(input_path,'*','*.wav'))

	for meet in tqdm.tqdm(meeting):
		all_wav=glob.glob(os.path.join(meet,'*.wav'))
		meet_name=os.path.basename(meet)
		for item in all_wav:
			file_name=os.path.basename(item)
			fname=meet_name+'_'+file_name
			zipf.write(item,arcname=fname)
	
	zip_list=os.path.join(decoding_cmd,'zip_list.scp')
	with open(zip_list,'w') as f:
		f.write(zip_file+'\n')

	meeting_list=os.path.join(decoding_cmd,'meeting_list.scp')
	meeting=[os.path.basename(x) for x in meeting]
	with open(meeting_list,'w') as f:
		for item in meeting:
			f.write(item+'\n')
	
	#  then make the decoding command

	os.makedirs(os.path.join('..','exp'),exist_ok=True)

	with open(os.path.join(decoding_cmd, 'decode.sh'),'w') as f:
		cmd = 'sh {} {} {} {}'.format(os.path.join(tool_path, 'run_asr_utterance.sh'), 
										zip_list, 
										decoding_result, 
										transcription_file,
										)
		f.write(cmd+'\n')

		cmd = 'chown -R {}:{} {}'.format(os.getuid(), os.getgid(), decoding_result) 
		f.write(cmd+'\n')

		# then do the wer eval as well
		cmd = 'python {} --meeting_list {} --decode_path {} --experiment_setup {} --development_session {} --result_path {}'.format(os.path.normpath(os.path.join(tool_path, '../python/get_wer.py')), 
				meeting_list,os.path.join(decoding_result,'utterances','LM_fglarge'), args.experiment_setup, args.development_session, decoding_result)
	
		f.write(cmd+'\n')


def make_argparse():
	parser = argparse.ArgumentParser(description='Generate ASR input files')

	parser.add_argument('--input_path', metavar='<path>', required=True, 
						help='Directory where input audio files are retrieved.')
	parser.add_argument('--decode_path', metavar='<path>', required=True, 
						help='Directory in which decoding is to be performed')
	parser.add_argument('--tool_path', metavar='<path>', required=True)
	parser.add_argument('--experiment_setup', default='raw', type=str, required=False)
	
	parser.add_argument('--development_session', default='session0', type=str, required=False)
	

	return parser

if __name__ == '__main__':
	parser = make_argparse()
	args = parser.parse_args()
	main(args)
