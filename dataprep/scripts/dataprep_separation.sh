

# Set some environment variables. 
pathscript=`dirname $0`/../../path.sh
if [ ! -f $pathscript ]
then
    echo "$pathscript not found."
    exit 1
fi

source $pathscript

expdata_separated=$EXPROOT/data/separation_result


if [ ! -d $expdata_separated ]
then
    echo "Downloading LibriCSS example separation data."    
    CWD=`pwd`
    mkdir -p $expdata_separated
  
    cd $expdata_separated

    # wget
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1iZeitPWFC6uMeeseyXMVPCx2IFNaxlv3' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1iZeitPWFC6uMeeseyXMVPCx2IFNaxlv3" -O continuous_separation.zip && rm -rf /tmp/cookies.txt

    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1px67memfWq5RwnK_r0-ohFW5SupWmuv-' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1px67memfWq5RwnK_r0-ohFW5SupWmuv-" -O utterance_separation.zip && rm -rf /tmp/cookies.txt

    # unzip
    unzip utterance_separation.zip
    unzip continuous_separation.zip

    cd $CWD
fi
