usage()
{
cat << EOF
usage: options
OPTIONS:
    -h Show this message
    -d data file
    -c TAClassifier path
    -o output directory
    -p output prefix
    -f Fraction of points in test
    -n number of sets to make
EOF
}
INFILE=
TAC_PATH=
OUT_PATH=
REFID=
F=
N=
B=
while getopts "hd:c:o:p:f:n:b:" OPTION
do 
    case $OPTION in
	h)
	    usage
	    exit 1;;
	d)
	    INFILE=$OPTARG;;
	c)
	    TAC_PATH=$OPTARG;;
	o)
	    OUT_PATH=$OPTARG;;
	p)
	    REFID=$OPTARG;;
	n)
	    N=$OPTARG;;
	f)
	    F=$OPTARG;;
	b)
	    B=$OPTARG;;
	?)
	    usage
	    exit 1
	    ;;
    esac
done

set -o nounset
set -o errexit

if [ ! -e $INFILE ]
then
    echo "Could not find file: $INFILE"
    exit 1
fi

if [ ! $F]
then
    echo "Using default value f=0.15"
    F=0.15
fi

if [ ! $B]
then 
    B=False
fi

if [ ! $N]
then
    N=1
fi

CROSS="crossValidationData.py"
CATALOG=$OUT_PATH/$REFID.sets.txt
echo "Generating train/test datasets"
if [[ $N != 1 ]]
then
for i in $(seq 1 $N)
do 
    python $TAC_PATH/$CROSS -i $INFILE -o $OUT_PATH/$REFID.$i -f $F -b $B 
    printf '%s\t%s\n' "$REFID.$i.train.txt" "$REFID.$i.test.txt" >> $CATALOG
    #echo "$REFID.$i.train.txt\t$REFID.$i.test.txt" >> $CATALOG
    echo "    $REFID.$i.train.txt, $REFID.$i.test.txt"

done
else
    python $TAC_PATH/$CROSS -i $INFILE -o $OUT_PATH/$REFID -f $F -b $B
    echo "    $REFID.train.txt, $REFID.test.txt"
fi
