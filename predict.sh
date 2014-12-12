usage()
{
cat <<EOF
usage: options
OPTIONS:
    -h Show this message
    -p Classifier in a .pkl
    -r RefSeq ID
    -d Data to classify
    -o Output file
    -c Path to TAClassifier
EOF
}

INFILE=
PKLFILE=
OUTFILE=
REFID=
TAC_PATH=
while getopts "hp:d:r:o:c:" OPTION
do
    case $OPTION IN
	h)
	    usage
	    exit 1;;
	p)
	    PKLFILE=$OPTARG;;
	d)
	    INFILE=$OPTARG;;
	r)
	    REFID=$OPTARG;;
	o)
	    OUTFILE=$OPTARG;;
	c)
	    TAC_PATH=$OPTARG;;
	?)
	    usage
	    exit 1;;
done

if ! [ -f $INFILE]
then
    echo "Featurizing test data"
    bash $TAC_PATH/featurize_test.sh -r $REFID -c $TAC_PATH 
    python $TAC_PATH/join.py -r $REFID
    echo "Wrote $REFID.data.txt"
fi

echo "Making predictions with $PKLFILE for points in $REFID.data.txt"
python $TAC_PATH/applyTree.py -d $REFID.data.txt -c $PKLFILE -r $REFID
echo "... done"
echo "Results stored in $REFID.predictions.txt"
