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

# parser.add_argument('-base_path', default='/data/zhuc/libricss/for_release/', type=str, required=False)
# 	parser.add_argument('-tool_path', default='/data/zhuc/libricss/opencss/pykaldi2/example/OpenCSS', type=str, required=False)
    return parser




# In[13]:
def main(args):

	base_dir=args.data_path
	tool_path=args.tool_path
	
	baseline_dir_utt=os.path.join(base_dir,'result','utterance_eval')
	wav_dir=os.path.join(baseline_dir_utt,'separated_wavs')
	zip_dir=os.path.join(baseline_dir_utt,'zip')
	decoding_cmd=os.path.join(baseline_dir_utt,'decoding_cmd')
	decoding_result=os.path.join(baseline_dir_utt,'decoding_result')

	os.makedirs(zip_dir,exist_ok=True)
	os.makedirs(wav_dir,exist_ok=True)
	os.makedirs(decoding_cmd,exist_ok=True)
	os.makedirs(decoding_result,exist_ok=True)

	os.chdir(base_dir)
	all_wav=glob.glob(os.path.join(wav_dir,'*.wav'))
	
	# first get all transcription

	print('form transcription dictionary')
	all_trans=glob.glob(base_dir+'/*/*/*/utt*.txt')
	all_transcription={}

	for it in all_trans:
	    with open(it,'r') as f:
	        lines=[line.rstrip() for line in f.readlines()]

	    info=it.split('/')
	    cond=info[-4]
	    meeting=info[-3]

	    for item in lines:
	        utt_id,trans=item.split('\t')
	        full_utt_id=meeting+'_'+utt_id.split('.')[0]
	        all_transcription[full_utt_id]=trans
	lines=[]
	for item in all_wav:
	    fname=os.path.basename(item)[:-4]
	    source_name='_'.join(fname.split('_')[:-1])
	    trans=all_transcription[source_name]
	    lines.append(os.path.basename(item)[:-4]+'\t'+trans)

	with open(os.path.join(decoding_cmd,'decoding_scp.scp'),'w') as f:
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

	with open(decoding_cmd+'/decode_batch_960.sh','w') as f:
	    cmd='sh '+ tool_path +'/decode_batch_960_utt.sh ' + decoding_cmd+'/meeting_list.scp '+decoding_result+' '+os.path.join(decoding_cmd,'decoding_scp.scp')
	    f.write(cmd+'\n')




if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
