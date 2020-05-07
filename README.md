# LibriCSS
Continuous speech separation (CSS) is an approach to handling overlapped speech in conversational audio signals. Most previous speech separation algorithms were tested on artificially mixed pre-segmented speech signals and thus bypassed overlap detection and speaker counting by implicitly assuming overlapped regions to be already extracted from the input audio. CSS is an attempt to directly process the continuously incoming audio signals with online processing. The main concept was established and its effectiveness was evaluated on real meeting recordings in [1]. As these recordings were proprietary, a publicly available dataset, called LibriCSS, has been prepared by the same research group in [2]. This repository contains the programs for LibriCSS evaluation. 

[1] T. Yoshioka et al., "Advances in Online Audio-Visual Meeting Transcription," 2019 IEEE Automatic Speech Recognition and Understanding Workshop (ASRU), SG, Singapore, 2019, pp. 276-283. 

[2] Z. Chen et al., "Continuous speech separation: dataset and analysis," ICASSP 2020 - 2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP), Barcelona, Spain, 2020, accepted for publication.

## Requirements

We use SCTK (https://github.com/usnistgov/SCTK), the NIST Scoring Toolkit, for evaluation and PyKaldi2 (https://github.com/jzlianglu/pykaldi2), a Python internface to Kaldi for ASR. They can be installed as follows. Note that you need to have Docker enabled on your machine as required by PyKaldi2. 
```
./install.sh
source ./path.sh
```
The second command defines some environmental variables, where path.sh is generated as a result of the first command. 

We also use some Python packages. Assuming you are using conda, the simplest way to install all required dependencies is to create a conda environment as follows. 
```
conda env create -f conda_env.yml
conda activate libricss_release
```
The second command activates the newly created environment named libricss_release. 


## Getting Started


### Continuous input evaluation
To perform continuous input evaluation, you may follow the steps below. 
1. First, the data can be downloaded and preprocessed as follows. 
    ```
    cd dataprep
    ./scripts/dataprep.sh
    ```
2. Then, ASR can be run as 
    ```
    cd ..
    sh activate.sh
    source path.sh
    source asr/scripts/asr_path.sh
    cd asr/script
    ./gen_asrinput_raw_continuous.sh
    cd ../exp
    . decode_raw_continuous.sh
    ```
    This will generate CTM files for each mini session, under exp/data/baseline/segments/decoding_result
    If you want to use your own ASR system, you may skip this step. 
    
    Also you might want to change the permission of intermediate files before you exit the docker by Ctrl-d, as by default the files generated in docker have root acess
    ```
    chmod -R 777 $EXPROOT
    ```
    
3. Finally, the ASR results can be scored as follows. 
    ```
    cd scoring
    ./scripts/eval_continuous.sh ../sample
    python ./python/report.py --inputdir ../sample
    ```  
    This performs evaluation for the sample CTM files provided under "sample" directory, which correspond to the "no separation" results of Table 2 in [2].
    The last Python script, scoring/python/report.py, will print out the results as follows. 
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

### Utterance-wise evaluation

We assume that you have already downloaded the AM and PyKaldi2 as described above. 

1. Activate the docker, by running:
    ```
    sudo sh activate.sh
    source path.sh
    source asr/scripts/asr_path.sh
    ```

2. Then the decoding command can be generated, and perform decoding
    ```
    cd asr/script
    ./gen_asrinput_raw_utterance.sh
    cd ../exp
    . decode_raw_utterance.sh
    
    ```
  
    Also you might want to change the permission of intermediate files before you exit the docker by Ctrl-d, as by default the files generated in docker have root acess
    ```
    chmod -R 777 $EXPROOT
    ```
  
3. Finally, collect the wer with following command
    ```
    cd ../scripts
    . run_wer_raw_utterance.sh
    ```
    And the result will be print, can be found exp/data/baseline/utterance/decoding_result
    
    ```
    0S       : 0.11458333333333333
    0L       : 0.11254386680812863
    OV10       : 0.1828377230246389
    OV20       : 0.2641803896243677
    OV30       : 0.34600058314705023
    OV40       : 0.43238971784502395
    ```

## Plan

The current repository generates only the baseline results without separation processing. For those of you focusing on front-end speech separation algorithms, we are planning to add example CSS output waveforms and ASR scripts using them. 



## Some Details

### Data
NOTE: WE RECOMMEND THAT YOU USE dataprep/scripts/dataprep.sh MENTIONED ABOVE TO OBTAIN THE DATA.

LibriCSS consists of distant microphone recordings of concatenated LibriSpeech utterances played back from loudspeakers in an office room, which enables evaluation of speech separation algorithms that handle long form audio. See [2] for details of the data. The data can be downloaded at https://drive.google.com/file/d/1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l/view. The archive file contains only the original "mini-session" recordings (see Section 3.1 of [2]) as well as the source signals played back from the loudspeakers. By following the instruction described in the README file, you should be able to generate the data for both utterance-wise evaluation (see Section 3.3.2 of [2]) and continuous input evaluation (Section 3.3.3 of [2]). 

The original directory structure is different from that the ASR/scoring tools expect. Python script dataprep/python/dataprep.py reorganizes the recordings. To see how it can be used, refer to dataprep/scripts/dataprep.sh (which executes all the necessary steps to start experiments). 



### Task (continuous input evaluation)
As a result of the data preparation step,  the 7-ch and 1-ch test data are created by default under $EXPROOT/7ch and $EXPROOT/monaural, respectively (EXPROOT is defined in path.sh). 
These directories consist of subdirectories named overlap_ratio\_\*\_sil\*\_\*\_session\*\_actual\*, each containing chunked mini-session 
audio files segment\_\*.wav (see Section 3.3.3 of [2]). 

The task is to trascribe each file and save the result in the CTM format as segment\_\*.ctm. Refer to http://my.fit.edu/~vkepuska/ece5527/sctk-2.3-rc1/doc/infmts.htm#ctm_fmt_name_0 for the CTM format specification. The result directory has to retain the original subdirectory structure, as in the "sample" directory. Then, your ASR CTM files can be evaluated with scoring/scripts/eval_continuous.sh. 

### Task (utterance-wise evaluation)

The data stucture is the same as the continuous evaluation, organized by mini session, where each utterance in the mini session are pre-segmented with ground truth boundary information.

The utterance-wise evaluation transcribe each utterance individually,as did in most speech separation/enhancement task, when multiple separation result are generated for one input mix utterance, the permutation with lowest wer will be picked as the final result.



