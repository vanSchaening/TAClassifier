# Download files and compute features given a reference sequence 

usage()
{
cat << EOF
usage:  options

OPTIONS:
    -h Show this message
    -r refseq ID
    -t TADB path (defaults to $TAC_PATH/TADB)
    -c TAClassifier path
EOF
}

REFID=
TAC_PATH=
TADB_PATH=

while getopts "hr:t:b:c:" OPTION
do
    case $OPTION in
    h)
        usage
        exit 1
        ;;
    r)
        REFID=$OPTARG
        ;;
    t)
        TADB_PATH=$OPTARG
        ;;
    b)
        BLAST_PATH=$OPTARG
        ;;
    c)
        TAC_PATH=$OPTARG
        ;;
    ?)
        usage
        exit
        ;;
    esac
done

if [[ -z $REFID ]] || [[ -z $TAC_PATH ]]
then 
    usage
    exit 1
fi

set -o nounset
set -o errexit

if ! [[ $TADB_PATH ]]
then
    echo "Expecting TADB in $TAC_PATH"
    TADB_PATH=$TAC_PATH/TADB
fi
TOXIN=$TADB_PATH/TADB_toxin_aa_v1-1.fas
ANTITOXIN=$TADB_PATH/TADB_antitoxin_aa_v1-1.fas

echo "Downloading gbk file..."
GET_GBK="get_gbk.py"
GBK=$REFID.gbk
if [[ -f $GBK ]]
then
    echo "...$GBK exists"
else
    set -o xtrace
    python $TAC_PATH/$GET_GBK -r $REFID -o $GBK
    set +o xtrace
    echo "...done! Wrote $GBK"
fi

echo "Generating positive mapping..."
POSITIVE_MAP="map_locus_gi.py"
POSITIVE=$REFID.positive
if [[ -f $POSITIVE.mapping.txt ]]
then
    echo "...$POSITIVE.mapping.txt exists"
else
    set -o xtrace
    python $TAC_PATH/$POSITIVE_MAP -g $GBK -r $REFID -t $TOXIN -a $ANTITOXIN \
        > $POSITIVE.mapping.txt
    set +o xtrace
    echo "...done! Wrote $POSITIVE.mapping.txt."
fi

echo "Generating negative mapping..."
NEGATIVE_MAP="gen_negative_mapping.py"
NEGATIVE=$REFID.negative
if [[ -f $NEGATIVE.mapping.txt ]]
then
    echo "...$NEGATIVE.mapping.txt exists"
else
    set -o xtrace
    python $TAC_PATH/$NEGATIVE_MAP -p $POSITIVE.mapping.txt -g $GBK \
        > $NEGATIVE.mapping.txt
    set +o xtrace
    echo "...done! Wrote $NEGATIVE.mapping.txt."
fi

echo "Computing all primary features..."
PRIMARY="compute_primary_features.py"
if [[ -f $POSITIVE.features.primary.txt ]]
then
    echo "...$POSITIVE.features.primary.txt exists"
else
    set -o xtrace
    python $TAC_PATH/$PRIMARY -g $GBK -m $POSITIVE.mapping.txt -c 1 \
        > $POSITIVE.features.primary.txt
    set +o xtrace
    echo "...done! Wrote $POSITIVE.features.primary.txt"
fi
if [[ -f $NEGATIVE.features.primary.txt ]]
then
    echo "...$NEGATIVE.features.primary.txt exists"
else
    set -o xtrace
    python $TAC_PATH/$PRIMARY -g $GBK -m $NEGATIVE.mapping.txt -c -1 \
        > $NEGATIVE.features.primary.txt
    set +o xtrace
    echo "...done! Wrote $NEGATIVE.features.primary.txt"
fi
