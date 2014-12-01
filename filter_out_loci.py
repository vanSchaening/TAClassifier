import argparse
import sys

from Bio import SeqIO

def filter_by_loci(infa, loci):
    with open(infa) as f:
        for record in SeqIO.parse(f, 'fasta'):
            test = record.description.split()[2]
            if test != loci:
                yield record

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infa')
    parser.add_argument('-o', '--outfa')
    parser.add_argument('-l', '--loci')
    args = parser.parse_args()

    wrote = SeqIO.write(filter_by_loci(args.infa, args.loci), args.outfa, 'fasta')
    print >> sys.stderr, "Wrote", wrote, "records for", args.loci, "to", args.outfa

if __name__ == '__main__':
    main()
