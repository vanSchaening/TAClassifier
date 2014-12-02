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
TOXIN=./TADB/TADB_toxin_aa_v1-1.fas
ANTITOXIN=./TADB/TADB_antitoxin_aa_v1-1.fas
BLASTPATH=

while getopts "hr:t:a:b:" OPTION
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
    b)
        BLASTPATH=$OPTARG
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

if [[ $BLASTPATH ]]
then
    echo "Appending $BLASTPATH to path"
    export PATH=$PATH:$BLASTPATH
fi

TAC_DIR=/Users/graceyeo/dropbox-mit/y1-fall/6.867-machinelearning/project/workspace/TAClassifier
#TAC_DIR=/home/cschaening/Documents/Research/Laub/TAClassifier

echo "Downloading gbk file..."
GET_GBK="get_gbk.py"
GBK=$REFID.gbk
if [[ -f $GBK ]]
then
    echo "...$GBK exists"
else
    set -o xtrace
    python $TAC_DIR/$GET_GBK -r $REFID -o $GBK
    set +o xtrace
    echo "...done! Wrote $GBK"
fi

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

echo "Generating positive mapping..."
POSITIVE_MAP="map_locus_gi.py"
POSITIVE=$REFID.positive
if [[ -f $POSITIVE.mapping.txt ]]
then
    echo "...$POSITIVE.mapping.txt exists"
else
    set -o xtrace
    python $TAC_DIR/$POSITIVE_MAP -g $GBK -r $REFID -t $TOXIN -a $ANTITOXIN \
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
    python $TAC_DIR/$NEGATIVE_MAP -p $POSITIVE.mapping.txt -g $GBK \
        > $NEGATIVE.mapping.txt
    set +o xtrace
    echo "...done! Wrote $NEGATIVE.mapping.txt."
fi

echo "Getting .faa files..."
GET_FAA="get_faa_from_map.py"
for class in $POSITIVE $NEGATIVE
do
    if [[ -f $class.toxin.faa ]] && [[ -f $class.antitoxin.faa ]]
    then
        echo "...$class.*.faa exist"
    else
        set -o xtrace
        python $TAC_DIR/$GET_FAA -g $GBK -m $class.mapping.txt -o $class
        set +o xtrace
        echo "...done! Wrote $class.*.faa."
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
        set -o xtrace
        python $TAC_DIR/$ESSENTIALITY -e $REFID.essentiality.txt -m $class.mapping.txt \
            > $class.essentiality.txt
        set +o xtrace
        echo "Wrote $class.essentiality.txt"
    fi

    if [[ -f $class.upalindromes.txt ]]
    then
        echo "$class.upalindromes.txt exists"
    else
        set -o xtrace
        python $TAC_DIR/$UPALINDROMES -g $GBK -m $class.mapping.txt \
            > $class.upalindromes.txt
        set +o xtrace
        echo "Wrote $class.upalindromes.txt"
    fi

done

STRUCTURE="structure.py"
HOMOLOGY="homology.py"
PROPERTIES="properties.py"
DATABASE=$TAC_DIR/phageDB/phage.genomes.fasta
echo "Finding protein properties, gene structure, and phage homology ... "
for class in $POSITIVE $NEGATIVE
do

    if [[ -f $class.structure.txt ]]
    then
        echo "$class.structure.txt exists"
    else
        set -o xtrace
        python $TAC_DIR/$STRUCTURE -t $class.toxin.faa -a $class.antitoxin.faa  -o $class
        set +o xtrace
        echo "Wrote $class.structure.txt"
    fi

    if [[ -f $class.properties.txt ]]
    then
	    echo "$class.properties.txt exists"
    else
	    set -o xtrace
	    python $TAC_DIR/$PROPERTIES -t $class.toxin.faa -a $class.antitoxin.faa -o $class
	    set +o xtrace
	    echo "Wrote $class.properties.txt"
    fi

    if [[ -f $class.homology.txt ]]
    then
	    echo "$class.homology.txt exists"
    else
	    set -o xtrace
	    python $TAC_DIR/$HOMOLOGY -t $class.toxin.faa -a $class.antitoxin.faa \
            -d $DATABASE -o $class
	    set +o xtrace
	    echo "Wrote $class.homology.txt"
    fi

done
