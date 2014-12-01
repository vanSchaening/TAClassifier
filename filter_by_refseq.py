import argparse
import sys

from Bio import SeqIO

def filter_by_refseq(infa, refseq):
    with open(infa) as f:
        for record in SeqIO.parse(f, 'fasta'):
            nc = record.description.split()[1].split(':')[0]
            if nc == refseq:
                record.description = record.description[:-1]
                yield record

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infa')
    parser.add_argument('-o', '--outfa')
    parser.add_argument('-r', '--refseq')
    args = parser.parse_args()

    wrote = SeqIO.write(filter_by_refseq(args.infa, args.refseq), args.outfa, 'fasta')
    print >> sys.stderr, "Wrote", wrote, "records for", args.refseq, "to", args.outfa

if __name__ == '__main__':
    main()
