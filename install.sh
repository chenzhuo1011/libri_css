#!/bin/bash

# If you have already installed SCTK on your machine, you may use it by pointing to the exising SCTK directory. 
SCTKPATH=external_tools/sctk
# If you have already installed PyKaldi2 on your machine, you may use it by pointing to the exising PyKaldi2 directory. 
PYKALDIPATH=external_tools/pykaldi2


##
## Installing SCTK. 
##

if [[ ! -d $SCTKPATH ]]
then
    read -p "Installing SCTK in $SCTKPATH. Hit Enter or type an alternative install path name: " ret
    if [ ! -z "$ret" ]
    then
        SCTKPATH=$ret
    fi

    if [[ ! -d $SCTKPATH ]]
    then
        CWD=`pwd`
        git clone https://github.com/usnistgov/SCTK.git $SCTKPATH
        cd $SCTKPATH
        make config
        make all
        make check
        make install
        make doc
        cd $CWD
    else
        echo "$SCTKPATH exists. Skip SCTK installation."    
    fi
fi

##
## Installing PyKaldi2
##

if [[ ! -d $PYKALDIPATH ]]
then
    read -p "Installing PyKaldi2 in $PYKALDIPATH. Hit Enter or type an alternative install path name: " ret
    if [ ! -z "$ret" ]
    then
        PYKALDIPATH=$ret
    fi

    if [[ ! -d $PYKALDIPATH ]]
    then
        CWD=`pwd`
        git clone https://github.com/jzlianglu/pykaldi2.git -b libcss $PYKALDIPATH
        cd $PYKALDIPATH
        sudo docker pull pykaldi2docker/horovod-pykaldi:libcss.v1.0
        cd $CWD
    else
        echo "$PYKALDIPATH exists. Skip PyKaldi2 installation."    
    fi
    
  cd $PYKALDIPATH

  wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/open?id=1Xon9jS2vEDOcwYAMrN2XAMrL-7PE2qXj' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1Xon9jS2vEDOcwYAMrN2XAMrL-7PE2qXj" -O libri_AM.zip && rm -rf /tmp/cookies.txt

    # unzip
  unzip libri_AM.zip
  cd $CWD  
fi

##
## Generate path.sh
##
SCTKPATH=`realpath $SCTKPATH`
echo "export SCTKPATH=$SCTKPATH" > path.sh 
PYKALDIPATH=`realpath $PYKALDIPATH`
echo "export PYKALDIPATH=$PYKALDIPATH" >> path.sh

echo "export AMPATH=$AMPATH/AM" >> path.sh


EXPROOT=`dirname $0`/exp
EXPROOT=`realpath $EXPROOT`
echo "export EXPROOT=$EXPROOT" >> path.sh
