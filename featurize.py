import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--antitoxin', help="antitoxin faa") # antitoxin aa fasta
    parser.add_argument('-t', '--toxin', help="toxin faa") # toxin aa fasta
    parser.add_argument('-u', '--upstream', help="upstream fa") # upstream nuc fasta
    parser.add_argument('-o', '--output', help="output prefix") # output prefix
    args = parser.parse_args()

    # INPUT
    # header for aa fasta
    # >TADB_ID  REFSEQ:START..END   LOCUS_ID   FOO
    # OUTPUT
    # LOCUS_ID FEATURE1 FEATURE2 FEATURE3 ...
    # join -j 1 *

if __name__ == '__main__':
    main()
