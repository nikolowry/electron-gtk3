#!/bin/sh

local args;

#Extract and push cli args to array
argsToArray() {
    #Only parse if flags have been defined
    if [[ $flags ]]; then
        #iterate args
        while [[ $# > 1 ]]
        do
            #Match to flag
            index=0; while ((index < ${#flags[*]})); do
                #Get cases from flag array
                flagArr=(${flags[$index]//|/ })

                #If valid push to args
                case $1 in ${flagArr[0]}|${flagArr[1]})
                    args[${#args[@]}]="$1=$2"
                shift ;;
                esac
        	((index++)); done
        shift
        done
    fi

    #If args are present, declare them for return
    if [[ $args && ${#args[*]} > 0 ]]; then
        declare -p args;
    fi
}

#Get An Arg
getArg() {
    if [[ $flags && $args && ${#args[*]} > 0 ]]; then
        #TODO return if valid arg, for now echo fn parameter
        echo $@
    fi
}
