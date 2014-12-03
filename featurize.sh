usage()
{
cat << EOF
usage:  options

OPTIONS:
    -h Show this message
    -r refseq ID
    -t TADB path (defaults to $TAC_PATH/TADB)
    -b BLAST path (optional if already on path)
    -c TAClassifier path
EOF
}

REFID=
BLAST_PATH=
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

## Resolve paths

if [[ $BLAST_PATH ]]
then
    echo "Appending $BLAST_PATH to path"
    export PATH=$PATH:$BLAST_PATH
fi

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

echo "Getting .faa files..."
GET_FAA="get_faa_from_map.py"
GET_START="getStartingPositions.py"
for class in $POSITIVE $NEGATIVE
do
    if [[ -f $class.toxin.faa ]] && [[ -f $class.antitoxin.faa ]]
    then
        echo "...$class.*.faa exist"
    else
        set -o xtrace
        python $TAC_PATH/$GET_FAA -g $GBK -m $class.mapping.txt -o $class
        set +o xtrace
        echo "...done! Wrote $class.*.faa."
    fi

    if [[ -f $class.startPositions.pkl ]]
    then
	echo "...$class.startPositions.pkl exists"
    else
	set -o xtrace
	python $TAC_PATH/$GET_START -o $class
	set -o xtrace
    fi
done



echo "Scoring..."
ESSENTIALITY="score_essentiality.py"
UPALINDROMES="score_upstream_palindromes.py"
for class in $POSITIVE $NEGATIVE
do

    if [[ -f $class.features.essentiality.txt ]]
    then
        echo "...$class.features.essentiality.txt exists"
    else
        set -o xtrace
        python $TAC_PATH/$ESSENTIALITY -e $REFID.essentiality.txt -m $class.mapping.txt \
            > $class.features.essentiality.txt
        set +o xtrace
        echo "...Wrote $class.essentiality.txt"
    fi

    if [[ -f $class.features.upalindromes.txt ]]
    then
        echo "...$class.features.upalindromes.txt exists"
    else
        set -o xtrace
        python $TAC_PATH/$UPALINDROMES -g $GBK -m $class.mapping.txt \
            > $class.features.upalindromes.txt
        set +o xtrace
        echo "...Wrote $class.features.upalindromes.txt"
    fi

done

STRUCTURE="structure.py"
HOMOLOGY="homology.py"
PROPERTIES="properties.py"
DATABASE=$TAC_PATH/phageDB/phage.genomes.fasta
echo "Finding protein properties, gene structure, and phage homology ... "
for class in $POSITIVE $NEGATIVE
do

    if [[ -f $class.features.structure.txt ]]
    then
        echo "...$class.features.structure.txt exists"
    else
        set -o xtrace
        python $TAC_PATH/$STRUCTURE -t $class.toxin.faa -a $class.antitoxin.faa \
            -o $class.features
        set +o xtrace
        echo "...Wrote $class.features.structure.txt"
    fi

    if [[ -f $class.features.properties.txt ]]
    then
	    echo "...$class.features.properties.txt exists"
    else
	    set -o xtrace
	    python $TAC_PATH/$PROPERTIES -t $class.toxin.faa -a $class.antitoxin.faa \
            -o $class.features
	    set +o xtrace
	    echo "...Wrote $class.features.properties.txt"
    fi

    if [[ -f $class.features.homology.txt ]]
    then
	    echo "...$class.features.homology.txt exists"
    else
	    set -o xtrace
	    python $TAC_PATH/$HOMOLOGY -t $class.toxin.faa -a $class.antitoxin.faa \
            -d $DATABASE -o $class
        gjoin -j 1 $class.homology.toxin.txt \
            $class.homology.antitoxin.txt \
            > $class.features.homology.txt
	    set +o xtrace
	    echo "...Wrote $class.features.homology.txt"
    fi

done
