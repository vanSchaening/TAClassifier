import argparse

# ------------------------------------------------------------------------------
#  MAIN FUNCTION
# ------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--antitoxin', help="antitoxin faa") # antitoxin aa fasta
    parser.add_argument('-t', '--toxin', help="toxin faa")         # toxin aa fasta
    parser.add_argument('-o', '--output', help="output prefix")    # output prefix
    args = parser.parse_args()

    structure(args.toxin,args.antitoxin,args.output)

# -----------------------------------------------------------------------------

start,end = 0,1

def structure(toxin_faa, antitoxin_faa,out):

    from collections import defaultdict
    loci = defaultdict(dict)

    from Bio import SeqIO
    with open(toxin_faa) as t, open(antitoxin_faa) as a:
        for record in SeqIO.parse(t,'fasta'):
            locus,positions = parseRecord(record)
            loci[locus]['T'] = positions

        for record in SeqIO.parse(a,'fasta'):
            locus,positions = parseRecord(record)
            loci[locus]['A'] = positions

    # Create and open output file
    outfile = ".".join([out,"structure","txt"])
    o = open(outfile,'w')
    # Write header for output file
    header = "\t".join(["locus_ID","gene1_length","gene2_length",
                        "distance","overlap"])
    o.write("#" + header.upper() + "\n")


    # Find operon structure infor for each TA
    # Note that it doesn't actually matter which gene is the toxin and 
    # which the antitoxin. For each pair, the features we are looking at
    # depend only on their relative positions. For example, the overlap is
    # always the distance between the end of the first gene and the start of 
    # the second one.

    for name,locus in loci.iteritems():
        if len(locus) != 2:
            continue
        if locus['A'][start] > locus['T'][start]:
            locus['A'],locus['T'] = locus['T'],locus['A']
        # Get structure info
        length1, length2 = geneLengths(locus)  
        distance = upstream(locus)
        overlp = overlap(locus)
        # Write to output file
        o.write("\t".join(map(str,[name,length1,length2,distance,overlp]))+"\n")
    o.close()
    return outfile

# Get locus ID and start,end positions from sequence record (from SeqIO)
def parseRecord(record):
    locus = record.id.split("|")[0]
    positions = record.description.split("\t")[1]
    positions = map(int,positions.split(":")[1].split(".."))
    return locus,tuple(positions)

def geneLengths(locus):
    l1 = locus['A'][end] - locus['A'][start]
    l2 = locus['T'][end] - locus['T'][start]
    return l1, l2

def upstream(locus):    
    return locus['T'][start] - locus['A'][start]

def overlap(locus):
    return locus['A'][end] - locus['T'][start]

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
