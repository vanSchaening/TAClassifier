def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile',
                        help="Complete dataset") # Input file containing all points
    parser.add_argument('-o', '--output',
                        help="Output prefix")
    parser.add_argument('-n', '--number', type=int, default=5,
                        help="Minimum number of points for an organism for testing")
    args = parser.parse_args()

    counts = countSpecies(args.infile)
    top = topOrganisms(counts,args.number)
    outfile = args.output+".topOrganisms.txt"
    with open(outfile,'w') as o:
        o.write("\n".join(top))

    

# ------------------------------------------------------------------------------


def countSpecies(infile):

    # Count number of data points for each organism,
    # and store in a dictionary
    from collections import defaultdict
    speciesCounts = defaultdict(int)
    with open(infile) as f:
        for line in f:
            if line.startswith("#"):
                continue
            refseq = line.strip().split("\t")[1]
            speciesCounts[refseq] += 1
    return speciesCounts


def topOrganisms(speciesCounts,n):
    # Return a list of the n species with most training points
    import operator
    species_sorted = sorted(speciesCounts.items(), key=operator.itemgetter(1))
    return [ species for (species,count) in species_sorted if count >= n ]

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
