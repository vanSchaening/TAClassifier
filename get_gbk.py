# Download genbank file given refseq id

import argparse
import sys

from Bio import Entrez

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--refid')
    parser.add_argument('-o', '--outfile')
    args = parser.parse_args()

    Entrez.email = "yhtgrace@gmail.com"
    net_handle = Entrez.esearch(db="nucleotide", 
        term="{0}[Primary Accession]".format(args.refid))
    record = Entrez.read(net_handle)
    assert record['Count'] == '1'
    net_handle = Entrez.efetch(db="nucleotide", id=record['IdList'][0], 
        rettype = 'gbwithparts', retmode="text")
    out_handle = open(args.outfile, 'w')
    out_handle.write(net_handle.read())
    out_handle.close()
    net_handle.close()

    print >> sys.stderr, "Saved to", args.outfile

if __name__ == '__main__':
    main()
