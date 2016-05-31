#!/bin/sh

helpMenu() {
    #ensure shell scripting compatability w echo for newline
    echo "Usage: ./build <command> <options>" && echo "";

    for cmd in $@; do
        if [[ $cmds ]]; then
            cmds="$cmds, $cmd";
        else
            cmds=$cmd;
        fi
    done

    echo "Where <command> is:";
    echo $cmds && echo "";
    echo "If no <command> is passed, all commands will be executed." && echo "";

    echo "Available <options>:";
    for flag in ${flags[*]}; do
        echo "  $flag";
    done
    echo "";
}
