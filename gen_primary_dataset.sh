#/bin/bash

set -o nounset
set -o errexit

TAC=/Users/graceyeo/dropbox-mit/y1-fall/6.867-machinelearning/project/workspace/TAClassifier
TADB=$TAC/TADB
ANTITOXIN=$TADB/TADB_antitoxin_aa_v1-1.fas

# get organisms with the most number of TA systems (top 25)
for refid in $(grep '^>' $ANTITOXIN | cut -f 2 | cut -d ':' -f 1 | sort | uniq -c | \
    sort -n -r | head -n 30 | awk '{print $2}')
do
    echo $refid
    if [[ -d $refid ]]
    then
        echo "$refid exists!"
    else
        echo "making directory..."
        mkdir $refid
    fi
    
    echo "###### Generating files for $refid"
    cd $refid
    set -o xtrace
    bash $TAC/featurize_primary.sh -r $refid -c $TAC \
        2>&1 | tee $refid.gen.log
    set +o xtrace
    cd ..
    echo "###### ...done!"

done
