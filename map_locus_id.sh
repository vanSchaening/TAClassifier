usage()
{
cat << EOF
usage:  options
bash ../../TAClassifier/map_locus_id.sh -a NC_005125.antitoxin_aa.positive.fa -t NC_005125.toxin_aa.positive.fa

OPTIONS:
    -h Show this message
    -t toxin 
    -a anti-toxin (it's okay if these are switched!)
EOF
}

FILE=
while getopts "ht:a:" OPTION
do
    case $OPTION in
    h)
        usage
        exit 1
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

if [[ -z $TOXIN ]] || [[ -z $ANTITOXIN ]]
then 
    usage
    exit 1
fi

join -j 2 \
    <(grep '^>' $TOXIN | cut -f 1,3 | sed 's/^>//' | sort) \
    <(grep '^>' $ANTITOXIN | cut -f 1,3 | sed 's/^>//' | sort)
