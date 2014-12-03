#!/bin/bash
if [[ ! -d filter ]]
then
    mkdir filter
fi
for refid in NC_*
do
    cd $refid
    echo ">>>Stats for $refid..."
    if [[ -f $refid.positive.mapping.txt ]] && [[ -f $refid.negative.mapping.txt ]]
    then
        echo "Number of positive data points: $(wc -l $refid.positive.mapping.txt)"
        echo "Number of negative data points: $(wc -l $refid.negative.mapping.txt)"
        cd ..
    else
        echo "Files missing."
        cd ..
        mv $refid filter
    fi
done
