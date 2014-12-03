from Bio.SeqUtils.ProtParam import ProteinAnalysis

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--antitoxin', help="antitoxin faa")
    parser.add_argument('-t', '--toxin', help="toxin faa")
    parser.add_argument('-o', '--output', help="output prefix")
    args = parser.parse_args()

    properties(args.toxin,args.antitoxin,args.output)

# ------------------------------------------------------------------------------

def properties(toxin_faa,antitoxin_faa,out):

    # Build a dictionary of {locus:[{properties:values},{properties:values}]}
    from collections import defaultdict
    loci = defaultdict(list)
    from Bio import SeqIO
    for f in [toxin_faa,antitoxin_faa]:
        # Parse FASTA files
        with open(f,'rU') as handle:
            for record in SeqIO.parse(handle,'fasta'):
                locus,start = getNameAndPosition(record)
                if not start:
                    continue
                aaseq = str(record.seq).strip("*")
                # Omit sequences with missing positions or premature stops
                # give them 0 as flag for missing data instead
                if "*" not in aaseq and "X" not in aaseq:
                    data = ProteinAnalysis(aaseq)
                    loci[locus].append({ 'start':  start,
                                         'pI':     data.isoelectric_point(),
                                         'weight': data.molecular_weight() })
                else:
                    loci[locus].append({ 'start': start,
                                         'pI': 0, 'weight':0 })

        
    # Order genes in a locus positionally
    loci = orderPairs(loci)

    # Write to output fil
    outfile = ".".join([out,"properties","txt"])
    with open(outfile,'w') as o:
        header = "\t".join(["locus",
                            "gene1_pI","gene2_pI",
                            "gene1_weight","gene2_weight"])
        o.write("#"+ header.upper() + "\n")
        for locus, gene in loci.iteritems():
            if len(gene) != 2:
                continue
            line = map(str, [ locus,gene[0]['pI'],gene[1]['pI'],
                              gene[0]['weight'],gene[1]['weight'] ])
            o.write("\t".join(line)+"\n")
    return outfile


# Every gene pair in in loci must be ordered by position
def orderPairs(loci):
    for locus, genes in loci.iteritems():
        if len(genes) != 2:
            continue
        if genes[0]['start'] > genes[1]['start']:
            loci[locus] = [ genes[1], genes[0] ]
    return loci


def getNameAndPosition(record):
    description = record.description.split("\t")
    locus = record.id.split("|")[0]
    start = int(description[1].split(":")[1].split("..")[0])
    return locus, start

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
