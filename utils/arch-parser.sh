#!/bin/sh

archParser() {
    arg=$@;
    arch64='x64 x86_64 amd64';
    arch32='ia32 i686';

    if [[ ! $arch64 =~ $arg && ! $arch32 =~ $arg ]]; then
        arg=$(uname -m);
    fi

    #Validate arch type
    if [[ $arch64 =~ $arg ]]; then
        echo 'x64';
    elif [[ $arch32  =~ $arg ]]; then
        echo 'ia32';
    fi
}
