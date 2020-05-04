#!/bin/bash

# If you have already installed SCTK on your machine, you may use it by pointing to the exising SCTK directory. 
SCTKPATH=$HOME/sctk
# If you have already installed PyKaldi2 on your machine, you may use it by pointing to the exising PyKaldi2 directory. 
PYKALDIPATH=$HOME/pykaldi2


##
## Installing SCTK. 
##

if [[ ! -d $SCTKPATH ]]
then
    read -p "Installing SCTK in $SCTKPATH. Hit Enter or type a target path name: " ret
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
    read -p "Installing PyKaldi2 in $PYKALDIPATH. Hit Enter or type a target path name: " ret
    if [ ! -z "$ret" ]
    then
        PYKALDIPATH=$ret
    fi

    if [[ ! -d $PYKALDIPATH ]]
    then
        CWD=`pwd`
        git clone https://github.com/jzlianglu/pykaldi2.git $PYKALDIPATH
        cd $PYKALDIPATH
        docker pull pykaldi2docker/horovod-pykaldi:torch1.2
        cd $CWD
    else
        echo "$PYKALDIPATH exists. Skip PyKaldi2 installation."    
    fi
fi


##
## Generate path.sh
##
echo "export SCTKPATH=$SCTKPATH" > path.sh 
echo "export PYKALDIPATH=$PYKALDIPATH" >> path.sh

EXPROOT=`dirname $0`/exp
EXPROOT=`realpath $EXPROOT`
echo "export EXPROOT=$EXPROOT" >> path.sh
