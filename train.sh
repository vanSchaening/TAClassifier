usage()
{
cat <<EOF
usage: options
OPTIONS:
    -h Show this message
    -i Data file
    -c TAClassifier path
    -o Output directory
    -p Output prefix
    -e Number of trees, if ensemble
    -r Number of trees, if random forest
    -d Maximum depth
EOF
}

INFILE=
OUT_PATH=
PREFIX=
TAC_PATH=
E=
R=
D=

while getopts "hi:o:c:p:e:r:d:" OPTION
do
    case $OPTION in
	h)
	    usage
	    exit 1;;
	i)
	    INFILE=$OPTARG;;
	o)
	    OUT_PATH=$OPTARG;;
	p)
	    PREFIX=$OPTARG;;
	c)
	    TAC_PATH=$OPTARG;;
	e)
	    E=$OPTARG;;
	r)
	    R=$OPTARG;;
	d)
	    D=$OPTARG;;
	?)
	    usage
	    exit;;
	esac
done

#if [[ $REFID ]] && [[ $PREFIX ]]
#then
#    REFID=$REFID/$PREFIX
#else
#    REFID=$PREFIX
#fi

set -o nounset
set -o errexit

if ! [[ $D ]]
then
    echo "Using default value for d"
    echo "max_depth = 4"
    D=4
fi

if [[ $E ]] && [[ $R ]]
then
    usage
    echo "Use either ensembles or random forests"
    exit 1
fi 

ENSEMBLE=$TAC_PATH/learners/makeEnsemble.py
TREE=$TAC_PATH/learners/makeTree.py

# Train an ensemble of decision trees
if [[ $E ]]
then
    echo "Building training/validation datasets"
    bash $TAC_PATH/crossValidation.sh -d $INFILE -c $TAC_PATH -o $OUT_PATH -p $PREFIX -n $E
    echo "Building an ensemble of $E trees of maximum depth $D."
    python $ENSEMBLE -f $OUT_PATH/$PREFIX.sets.txt -o $OUT_PATH/$PREFIX 
    echo "... stored in $PREFIX.ensemble.pkl"
fi

if [[ $R ]]
then
    echo "Building training/validation datasets"
    bash $TAC_PATH/crossValidation.sh -d $INFILE -c $TAC_PATH -o $OUT_PATH -p $PREFIX
    echo "Building a random forest of $R trees of maximum depth $D."
    python $TREE -r $OUT_PATH/$PREFIX.train.txt -s $OUT_PATH/$PREFIX.test.txt -o $OUT_PATH/$PREFIX -n $R
    echo "... stored in $PREFIX.forest.pkl"
fi

# Train a single decision tree
if ! [[ $E || $R ]]
then
    echo "Building training/validation datasets"
    bash $TAC_PATH/crossValidation.sh -d $INFILE -c $TAC_PATH -o $OUT_PATH -p $PREFIX -f 0.05
    echo "Building a decision tree of maximum depth $D."
    python $TREE -r $OUT_PATH/$PREFIX.train.txt -s $OUT_PATH/$PREFIX.test.txt -o $OUT_PATH/$PREFIX
    echo "... stored in $OUT_PATH/$PREFIX.tree.pkl"
fi
