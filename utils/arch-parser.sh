#!/bin/sh

parseArch() {
    archArg=$@;
    arch64='x64 x86_64 amd64';
    arch32='ia32 i686';

    if [[ ! $arch64 =~ $archArg && ! $arch32 =~ $archArg ]]; then
        archArg=$(uname -m);
    fi

    #Validate arch type
    if [[ $arch64 =~ $archArg ]]; then
        echo 'x64';
    elif [[ $arch32  =~ $archArg ]]; then
        echo 'ia32';
    fi
}
