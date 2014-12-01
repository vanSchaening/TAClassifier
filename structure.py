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

    # Get positions for all toxins
    f = open(toxin_faa)
    for line in f:
        if line.startswith(">"):
            locus,positions = parseHeader(line)
            if not positions:
                continue
            loci[locus]['T'] = positions
    f.close()

    # Get positions for all antitoxins
    f = open(antitoxin_faa)
    for line in f:
        if line.startswith(">"):
            locus,positions = parseHeader(line)
            if not positions:
                continue
            loci[locus]['A'] = positions
    f.close()

    # Create and open output file
    outfile = ".".join([out,"structure","csv"])
    o = open(outfile,'w')
    # Write header for output file
    o.write("\t".join(["locus_ID","gene1_length","gene2_length",
                       "distance","overlap"])+"\n")

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

def parseHeader(header):
    head = header.strip().split("\t")
    if len(head) < 4:
        return header, False
    locus = head[2]
    positions = head[1].split(":")[1]
    positions = map(int,positions.split(".."))
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
