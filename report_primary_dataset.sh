#!/bin/bash
for refid in NC_*
do
    cd $refid
    echo ">>>Stats for $refid..."
    if [[ -f $refid.positive.features.primary.txt ]] && [[ -f $refid.negative.features.primary.txt ]]
    then
        echo "Number of positive data points: $(wc -l $refid.positive.features.primary.txt)"
        echo "Number of negative data points: $(wc -l $refid.negative.features.primary.txt)"
    else
        echo "Files missing."
    fi
    cd ..
done
