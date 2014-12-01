#/bin/bash

set -o nounset
set -o errexit

TADB=/Users/graceyeo/dropbox-me/TAclassifier/TADB
TOXIN=$TADB/TADB_toxin_aa_v1-1.fas
ANTITOXIN=$TADB/TADB_antitoxin_aa_v1-1.fas

TAC_DIR=/Users/graceyeo/dropbox-mit/y1-fall/6.867-machinelearning/project/workspace/TAClassifier

# get organisms with the most number of TA systems (top 8)
for refid in $(grep '^>' $ANTITOXIN | cut -f 2 | cut -d ':' -f 1 | sort | uniq -c | \
    sort -n -r | head -n 8 | awk '{print $2}')
do
    echo $refid
    if [[ -d $refid ]]
    then
        echo "$refid exists. Skipping..."
    else
        echo "###### Generating files for $refid"
        mkdir $refid
        cd $refid
        set -o xtrace
        bash $TAC_DIR/featurize.sh -r $refid -t $TOXIN -a $ANTITOXIN \
            2>&1 | tee $refid.gen.log
        set +o xtrace
        cd ..
        echo "###### ...done!"
    fi
done
