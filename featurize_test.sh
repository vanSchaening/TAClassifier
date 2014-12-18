# Download files and compute features given a reference sequence 

usage()
{
cat << EOF
usage:  options

OPTIONS:
    -h Show this message
    -r refseq ID
    -b BLAST path (optional if already on path)
    -c TAClassifier path
EOF
}

REFID=
BLAST_PATH=
TAC_PATH=

while getopts "hr:b:c:" OPTION
do
    case $OPTION in
    h)
        usage
        exit 1
        ;;
    r)
        REFID=$OPTARG
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

## Resolve paths

if [[ $BLAST_PATH ]]
then
    echo "Appending $BLAST_PATH to path"
    export PATH=$PATH:$BLAST_PATH
fi

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

# Paste back here

echo "Generating data mapping..."
MAP="gen_mapping.py"
if [[ -f $REFID.mapping.txt ]]
then
    echo "...$REFID.mapping.txt exists"
else
    set -o xtrace
    python $TAC_PATH/$MAP -g $GBK \
        > $REFID.mapping.txt
    set +o xtrace
    echo "...done! Wrote $REFID.mapping.txt."
fi


echo "Getting .faa files..."
GET_FAA="get_faa_from_map.py"
GET_START="getStartingPositions.py"
if [[ -f $REFID.toxin.faa ]] && [[ -f $REFID.antitoxin.faa ]]
then
    echo "...$REFID.*.faa exist"
else
    set -o xtrace
    python $TAC_PATH/$GET_FAA -g $GBK -m $REFID.mapping.txt -o $REFID
    set +o xtrace
    echo "...done! Wrote $REFID.*.faa."
    fi

if [[ -f $REFID.startPositions.pkl ]]
then
    echo "...$REFID.startPositions.pkl exists"
else
    set -o xtrace
    python $TAC_PATH/$GET_START -o $REFID
    set -o xtrace
fi

# Moved to here

echo "Downloading essentiality file..."
if [[ -f $REFID.essentiality.txt ]]
then
    echo "$REFID.essentiality.txt exists"
else
    set -o xtrace
    wget http://cefg.uestc.edu.cn/geptop/prediction/$REFID.dat -O $REFID.essentiality.txt
    set +o xtrace
    echo "...done! Wrote $REFID.essentiality.txt"
fi

echo "Scoring..."
ESSENTIALITY="score_essentiality.py"
UPALINDROMES="score_upstream_palindromes.py"

if [[ -f $REFID.features.essentiality.txt ]]
then
    echo "...$REFID.features.essentiality.txt exists"
else
    set -o xtrace
    python $TAC_PATH/$ESSENTIALITY -e $REFID.essentiality.txt -m $REFID.mapping.txt \
        > $REFID.features.essentiality.txt
    set +o xtrace
    echo "...Wrote $REFID.essentiality.txt"
    fi

if [[ -f $REFID.features.upalindromes.txt ]]
then
    echo "...$REFID.features.upalindromes.txt exists"
else
    set -o xtrace
    python $TAC_PATH/$UPALINDROMES -g $GBK -m $REFID.mapping.txt \
        > $REFID.features.upalindromes.txt
    set +o xtrace
    echo "...Wrote $REFID.features.upalindromes.txt"
fi


STRUCTURE="structure.py"
HOMOLOGY="homology.py"
PROPERTIES="properties.py"
DATABASE=$TAC_PATH/phageDB/phage.genomes.fasta
echo "Finding protein properties, gene structure, and phage homology ... "

if [[ -f $REFID.features.structure.txt ]]
then
    echo "...$REFID.features.structure.txt exists"
else
    set -o xtrace
    python $STRUCTURE -t $REFID.toxin.faa -a $REFID.antitoxin.faa \
        -o $REFID.features
    set +o xtrace
    echo "...Wrote $REFID.features.structure.txt"
fi

if [[ -f $REFID.features.properties.txt ]]
then
    echo "...$REFID.features.properties.txt exists"
else
    set -o xtrace
    python $TAC_PATH/$PROPERTIES -t $REFID.toxin.faa -a $REFID.antitoxin.faa \
            -o $REFID.features
    set +o xtrace
    echo "...Wrote $REFID.features.properties.txt"
fi

if [[ -f $REFID.features.homology.txt ]]
then
    echo "...$REFID.features.homology.txt exists"
else
    set -o xtrace
    python $TAC_PATH/$HOMOLOGY -t $REFID.toxin.faa -a $REFID.antitoxin.faa \
        -d $DATABASE -o $REFID
    echo "...Wrote $REFID.features.homology.txt"
fi

python $TAC_PATH/join.py -r $REFID  
echo "Done. Wrote data to $REFID.data.txt"
