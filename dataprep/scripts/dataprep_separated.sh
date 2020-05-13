

# Set some environment variables. 
pathscript=`dirname $0`/../../path.sh
if [ ! -f $pathscript ]
then
    echo "$pathscript not found."
    exit 1
fi

expdata_separated=$EXPROOT/data/separation_result

# https://drive.google.com/open?id=1rSLO-gFdvO9Pur3BdGY2xxc6QM1iPzql
# https://drive.google.com/open?id=1x3ok8AFTzNhmzGALKgjeLQtaC9sV8v1J
# Download and unzip the data. 

if [ ! -d $expdata_separated ]
then
    echo "Downloading LibriCSS separation data."    
    CWD=`pwd`
    mkdir -p $expdata_separated
  
    cd $expdata_separated

    # wget
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1rSLO-gFdvO9Pur3BdGY2xxc6QM1iPzql' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1rSLO-gFdvO9Pur3BdGY2xxc6QM1iPzql" -O utterance_separation.zip && rm -rf /tmp/cookies.txt

    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1x3ok8AFTzNhmzGALKgjeLQtaC9sV8v1J' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1x3ok8AFTzNhmzGALKgjeLQtaC9sV8v1J" -O continuous_separation.zip && rm -rf /tmp/cookies.txt

    # unzip
    unzip utterance_separation.zip
    unzip continuous_separation.zip

    # segmentation
    
    cd $CWD
fi
