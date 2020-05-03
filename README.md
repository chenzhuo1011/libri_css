# LibriCSS
Continuous speech separation (CSS) is an approach to handling overlapped speech in conversational audio signals. Most previous speech separation algorithms were tested on artificially mixed pre-segmented speech signals and thus bypassed overlap detection and speaker counting by implicitly assuming overlapped regions to be already extracted from the input audio. CSS is an attempt to directly process the continuously incoming audio signals with online processing. The main concept was established and its effectiveness was evaluated on real meeting recordings in [1]. As these recordings were proprietary, a publicly available dataset, called LibriCSS, has been prepared by the same research group in [2]. This repository contains the programs for LibriCSS evaluation. 

[1] T. Yoshioka et al., "Advances in Online Audio-Visual Meeting Transcription," 2019 IEEE Automatic Speech Recognition and Understanding Workshop (ASRU), SG, Singapore, 2019, pp. 276-283. 

[2] Z. Chen et al., "Continuous speech separation: dataset and analysis," ICASSP 2020 - 2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), Barcelona, Spain, 2020, accepted for publication.

## Data
LibriCSS consists of distant microphone recordings of concatenated LibriSpeech utterances played back from loudspeakers in an office room, which enables evaluation of speech separation algorithms that handle long form audio. See [2] for details of the data. 

The data can be downloaded at: 
https://drive.google.com/file/d/1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l/view

The archive file contains only the original "mini-session" recordings (see Section 3.1 of [2]) as well as the source signals played back from the loudspeakers. By following the instruction described in the README file, you should be able to generate the data for both utterance-wise evaluation (see Section 3.3.2 of [2]) and continuous input evaluation (Section 3.3.3 of [2]). 


## Repository Overview

This repository consists of two components: scoring and ASR tools. If you build your own ASR systems that can handle speech overlaps and want to evaluate them on the LibriCSS data, you just need thte scoring tools. If you build only front-ends, you may use the ASR tools provided here. Note that the ASR tools are currently being prepared for sharing. The status will be updated by 5/6. 



# Data preparation

Whether you use the ASR tools provided here or not, the first step is to reorganize the LibriCSS data. 

## Steps
1. Install the following Python packages. 
    1. Install PySoundFile. It is simlper to use Anaconda as noted at https://pypi.org/project/PySoundFile/.
    2. Install the following Python packages via pip. 
        - tqdm

2. Run the scripts/dataprep.sh. Be sure to change the paths (i.e., LIBRICSS and EXPROOT values) in dataprep.sh. 
```
cd dataprep
./scripts/dataprep.sh
```

## Task
As a result of Step2,  the 7-ch and 1-ch test data are created under $EXPROOT/7ch and $EXPROOT/monaural, respectively. 
These directories consist of subdirectories named overlap_ratio\_\*\_sil\*\_\*\_session\*\_actual\*, each containing chunked mini-session 
audio files segment\_\*.wav (see Section 3.3.3 of [2]). 

The task is to trascribe each file and save the result in the CTM format as segment\_\*.ctm. Refer to http://my.fit.edu/~vkepuska/ece5527/sctk-2.3-rc1/doc/infmts.htm#ctm_fmt_name_0 for the CTM format specification.  



# Scoring

## Steps
1. We use SCTK, the NIST Scoring Toolkit, for evaluation. This can be installed as follows. 
    1. Clone the source code from https://github.com/usnistgov/SCTK. 
    2. Compile and install SCTK by following the instructions contained in the cloned repository. 
2. Run evaluation. See the following example. 


## Example
Run the following command to see how scoring is performed. This script scores example ASR outputs that can be found in "sample" directory of this repository. Be sure to change PYTHON and sctk_path values as appropriate in scripts/eval_noproc.sh. 
```
cd scoring
./scripts/eval_noproc.sh
python ./python/report.py --inputdir ../sample --decode_cfg 13_0.0
```  
The last command should print out the baseline (i.e., w/o separation) WER for each overlap condition as follows. 
```  
Result Summary
--------------
Condition: %WER
0S       : 15.5
0L       : 11.5
10       : 21.9
20       : 27.1
30       : 34.7
40       : 40.8
```  
This corresponds to the "no separation" results of Table 2 in [2]. 



# ASR 

CAUTION: THIS IS CURRENTLY BEING PREPARED FOR SHARING. THE STATUS WILL BE UPDATED BY 5/6/20.

## Steps
1. We use PyKaldi2 for ASR, which can be downloaded at https://github.com/jzlianglu/pykaldi2. Follow Steps 1 and 2 of the instruction described in Section "How to install". 
2. Install webrtcvad via pip. This is used for VAD. 
3. Run ASR. 
