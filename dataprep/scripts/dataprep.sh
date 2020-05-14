#!/bin/bash

# Set some environment variables. 
pathscript=`dirname $0`/../../path.sh
if [ ! -f $pathscript ]
then
    echo "$pathscript not found."
    exit 1
fi

source $pathscript

origdata=$EXPROOT/data-orig
expdata=$EXPROOT/data


# Download and unzip the data. 
if [ ! -d $origdata ]
then
    echo "Downloading LibriCSS data."    
    CWD=`pwd`
    mkdir -p $origdata

    cd $origdata

    # wget
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l" -O for_release.zip && rm -rf /tmp/cookies.txt

    # unzip
    unzip for_release.zip

    # segmentation
    cd for_release
    python segment_libricss.py -data_path .

    cd $CWD
fi


# In this example, we generate data for monaural and 7-ch testing.
# If you need 3-ch testing data, you can generate them as "$PYTHON $prep_script --srcpath $origdata --tgtpath $mono_path --mics 1 3 5".
prep_script=`dirname $0`/../python/dataprep.py
mono_path=$expdata/monaural
full_path=$expdata/7ch

python $prep_script --srcpath $origdata/for_release --tgtpath $full_path
python $prep_script --srcpath $origdata/for_release --tgtpath $mono_path --mics 0

