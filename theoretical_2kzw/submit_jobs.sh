#!/bin/bash

while read LINE
do
    while [[ `jobs | wc -l` -ge 8 ]]
    do
        echo Waiting for some jobs to finish...
        sleep 30
    done
    oname=`echo $LINE | awk -F "/" '{print $2}'`
    echo "`date` submitting $oname"
    $LINE > $oname/output.log 2>&1 &
done < all_script.txt
wait
