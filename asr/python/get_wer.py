import glob,os,tqdm
import numpy as np

def load_result_files(res_folder,meeting_list):
#     t1=glob.glob(r'\\ccpsofsep\Scratch3\users\zhuc\OpenCSS\res\mc_less_noise_no_stop_mvdr.tr960mmi\mc_less_noise_no_stop_mvdr.tr960mmi\mc_less_noise_no_stop_mvdr\LM_fglarge\result*')
	t1=glob.glob(res_folder+'/result*')
#     print(t1)
	all_res={}
	for item in tqdm.tqdm(t1):
		cond='_'.join(os.path.basename(item).split('_')[-2:])
		with open(item,'r') as f:
			lines=[line.rstrip() for line in f.readlines()]
		res_lines=[]
		for ite in lines:
			if 'err:' in ite and 'ref_len:' in ite:
				res_lines.append(ite)
		all_res[cond]=res_lines
		
	all_cond=list(all_res.keys())
	all_cond_res={}
	
	for cond in all_cond:
		this_res=all_res[cond]
		this_cond={}
		for item in meeting_list:
			this_meet=[]
			for ite in this_res:
				if ite[:len(item)]==item:
					this_meet.append(ite)
			this_cond[item]=this_meet
		all_cond_res[cond]=this_cond    
		
	return all_cond_res

def get_this_meet_res(this_meet,meet_id):
	assert(len(this_meet)%2==0)
	nseg=len(this_meet)/2
	
	ERR=[]
	REF=[]
	for i in range(int(nseg)):
		utt1=meet_id+'_utterance_'+str(i)+'_0'
		utt2=meet_id+'_utterance_'+str(i)+'_1'
		err1,ref1=find_line(this_meet,utt1)
		err2,ref2=find_line(this_meet,utt2)
		
		assert(ref1==ref2)
		err=np.min([err1,err2])
		ref=ref1
		ERR.append(err)
		REF.append(ref)
	return ERR,REF

def get_this_meet_res(this_meet,meet_id):
	assert(len(this_meet)%2==0)
	nseg=len(this_meet)/2
	
	ERR=[]
	REF=[]
	for i in range(int(nseg)):
		utt1=meet_id+'_utterance_'+str(i)+'_0'
		utt2=meet_id+'_utterance_'+str(i)+'_1'
		err1,ref1=find_line(this_meet,utt1)
		err2,ref2=find_line(this_meet,utt2)
		
		assert(ref1==ref2)
		err=np.min([err1,err2])
		ref=ref1
		ERR.append(err)
		REF.append(ref)
	return ERR,REF

def get_this_meet_res_raw(this_meet,meet_id):
#     assert(len(this_meet)%2==0)
	nseg=len(this_meet)
	
	ERR=[]
	REF=[]
	for i in range(int(nseg)):
		utt1=meet_id+'_utterance_'+str(i)
		err,ref=find_line(this_meet,utt1)
		ERR.append(err)
		REF.append(ref)
	return ERR,REF


def find_line(this_meet,utt):
	for ite in this_meet:
#         print(ite[:len(utt)],utt)
		if ite[:len(utt)]==utt:
			t1=ite.split(' ')
			err=int(t1[2])
			ref=int(t1[-1])
			return err,ref
		
def pick_setup(all_cond_res,session_id,setup='separated'):
	all_cond=list(all_cond_res.keys())
	this_cond=all_cond_res[all_cond[0]]
	all_key=list(this_cond.keys())
	E=0
	R=0
	cond_res=[]
	for cond in all_cond:
		this_cond=all_cond_res[cond]
		for item in all_key:
			if session_id in item:
				if setup=='separated':
					err,ref=get_this_meet_res(this_cond[item],item)
				elif setup=='raw':
					err,ref=get_this_meet_res_raw(this_cond[item],item)
				E+=np.sum(err)
				R+=np.sum(ref)
		cond_res.append(E/R)
	cond_idx=np.argmin(cond_res)
	return all_cond[cond_idx]

def get_all_res(all_cond_res,tgt_cond,kwd,setup='separated'):
	
# 14_1.0 is the best
# tgt_cond='14_0.0'
# then get all result 
	this_cond=all_cond_res[tgt_cond]
	all_key=list(this_cond.keys())

	res=[]
	for kw in kwd:
		E=0
		R=0
		for item in all_key:
			if kw in item:
				if setup=='separated':
					err,ref=get_this_meet_res(this_cond[item],item)
				elif setup=='raw':
					err,ref=get_this_meet_res_raw(this_cond[item],item)
				E+=np.sum(err)
				R+=np.sum(ref)
		res.append(E/R)
	return res


import argparse



def make_argparse():
	parser = argparse.ArgumentParser(description='Generate ASR input files')

	parser.add_argument('--data_path', default='', type=str, required=False)
	parser.add_argument('--decode_path', default='', type=str, required=False)
	parser.add_argument('--development_session', default='session0', type=str, required=False)
	parser.add_argument('--experiment_setup', default='raw', type=str, required=False)
	parser.add_argument('--result_path', default='', type=str, required=False)

	return parser



def main(args):

	base_dir=args.data_path
	decode_dir=args.decode_path

	# meeting_list=glob.glob(os.path.join(base_dir,'monaural','utterances','overlap_ratio*'))
	# meeting_list=[os.path.basename(x) for x in meeting_list]

	with open(os.path.join(base_dir,'meeting_list.scp'),'r') as f:
		meeting_list=[line.rstrip() for line in f.readlines()]

	kwd=['overlap_ratio_0.0_sil0.1_0.5','overlap_ratio_0.0_sil2.9_3.0','overlap_ratio_10.0_sil0.1_1.0',
	 'overlap_ratio_20.0_sil0.1_1.0','overlap_ratio_30.0_sil0.1_1.0','overlap_ratio_40.0_sil0.1_1.0']
	condition=['0S','0L','OV10','OV20','OV30','OV40']

	all_cond_res=load_result_files(decode_dir,meeting_list)

	# print(all_cond_res)

	tgt_cond=pick_setup(all_cond_res,args.development_session,setup=args.experiment_setup)
	all_res=get_all_res(all_cond_res,tgt_cond,kwd,setup=args.experiment_setup)
	
	with open(args.result_path+'/'+args.experiment_setup+'_wer.txt','w') as f:
		for i in range(len(condition)):
			f.write(condition[i]+': '+ str(all_res[i])+'\n')
			print(condition[i]+': '+ str(all_res[i]))


if __name__ == '__main__':
	parser = make_argparse()
	args = parser.parse_args()
	main(args)

