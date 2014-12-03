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
EOF
}

INFILE=
TAC_PATH=
OUT_PATH=
REFID=

while getopts "hd:c:o:p:n:" OPTION
do
    case $OPTION in
	h)
	    usage
	    exit 1
	    ;;
	d)
	    INFILE=$OPTARG
	    ;;
	c)
	    TAC_PATH=$OPTARG
	    ;;
	o)
	    OUT_PATH=$OPTARG
	    ;;
	p)
	    REFID=$OPTARG
	    ;;
	n)
	    N=$OPTARG
	    ;;
	?)
	    usage
	    exit
	    ;;
    esac
done

set -o nounset
set -o errexit

# Check that input file exists
if  [ ! -e $INFILE ]
then
    echo "Could not find file: $INFILE"
    exit 1
fi

# Check that output directory exists. If not, create it.
if  [ ! -d $OUT_PATH ]
then 
    mkdir $OUT_PATH
    echo "Output directory not found"
    echo "Created output directory: $OUT_PATH"
fi
export PATH=$PATH:$OUT_PATH

# Get list of species above cutoff
TOP="topSpecies.py" 
SPECIES=$OUT_PATH/$REFID.topOrganisms.txt
if [ -f $SPECIES ] 
then
    echo "Prefix '$REFID' already in use in output directory"
    exit 1
else
    set -o xtrace
    python $TAC_PATH/$TOP -i $INFILE -o $OUT_PATH/$REFID -n $N
    set +o xtrace
fi


MAKEDATA="dataMinusSpecies.py" 
echo "Generating train/test datasets"
for NAME in $(cat $SPECIES)
do
#    set -o xtrace
    python $TAC_PATH/$MAKEDATA -i $INFILE -o $OUT_PATH/$REFID -s $NAME
    echo "    without_$NAME"
#    set +o xtrace
done
