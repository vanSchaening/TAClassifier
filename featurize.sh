usage()
{
cat << EOF
usage:  options

OPTIONS:
    -h Show this message
    -r refseq ID
    -t TADB toxin .faa
    -a TADB antitoxin .faa
EOF
}

REFID=
TOXIN=
ANTITOXIN=

while getopts "hr:t:a:" OPTION
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
        TOXIN=$OPTARG
        ;;
    a)
        ANTITOXIN=$OPTARG
        ;;
    ?)
        usage
        exit
        ;;
    esac
done

if [[ -z $REFID ]] || [[ -z $TOXIN ]] || [[ -z $ANTITOXIN ]]
then 
    usage
    exit 1
fi

set -o nounset
set -o errexit

TAC_DIR=/Users/graceyeo/dropbox-mit/y1-fall/6.867-machinelearning/project/workspace/TAClassifier

echo "Downloading gbk file..."
GET_GBK="get_gbk.py"
GBK=$REFID.gbk
if [[ -f $GBK ]]
then
    echo "...$GBK exists"
else
    python $TAC_DIR/$GET_GBK -r $REFID -o $GBK
    echo "...done!"
fi

echo "Downloading essentiality file..."
if [[ -f $REFID.essentiality.txt ]]
then
    echo "$REFID.essentiality.txt exists"
else
    wget http://cefg.uestc.edu.cn/geptop/prediction/$REFID.dat -O $REFID.essentiality.txt
fi

echo "Generating positive mapping..."
POSITIVE_MAP="map_locus_gi.py"
POSITIVE=$REFID.positive
if [[ -f $POSITIVE.mapping.txt ]]
then
    echo "...$POSITIVE.mapping.txt exists"
else
    python $TAC_DIR/$POSITIVE_MAP -g $GBK -r $REFID -t $TOXIN -a $ANTITOXIN \
        > $POSITIVE.mapping.txt
    echo "...done!"
fi

echo "Generating negative mapping..."
NEGATIVE_MAP="gen_negative_mapping.py"
NEGATIVE=$REFID.negative
if [[ -f $NEGATIVE.mapping.txt ]]
then
    echo "...$NEGATIVE.mapping.txt exists"
else
    python $TAC_DIR/$NEGATIVE_MAP -m $POSITIVE.mapping.txt -g $GBK \
        > $NEGATIVE.mapping.txt
    echo "...done!"
fi

echo "Getting .faa files..."
GET_FAA="get_faa_from_map.py"
for class in $POSITIVE $NEGATIVE
do
    if [[ -f $class.toxin.faa ]] && [[ -f $class.antitoxin.faa ]]
    then
        echo "...$class.*.faa exist"
    else
        python $TAC_DIR/$GET_FAA -g $GBK -m $class.mapping.txt -o $class
        echo "...done!"
    fi
done

echo "Scoring..."
ESSENTIALITY="score_essentiality.py"
UPALINDROMES="score_upstream_palindromes.py"
for class in $POSITIVE $NEGATIVE
do

    if [[ -f $class.essentiality.txt ]]
    then
        echo "$class.essentiality.txt exists"
    else
        python $TAC_DIR/$ESSENTIALITY -e $class.essentiality.txt -m $class.mapping.txt \
            > $class.essentiality.txt
        echo "Wrote $class.essentiality.txt"
    fi

    if [[ -f $class.upalindromes.txt ]]
    then
        echo "$class.upalindromes.txt exists"
    else
        python $TAC_DIR/$UPALINDROMES -g $GBK -m $class.mapping.txt \
            > $class.upalindromes.txt
        echo "Wrote $class.upalindromes.txt"
    fi

done
