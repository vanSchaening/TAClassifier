import argparse
import sys

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC

def makeSeqRecord(feature, refseq=""):
    return SeqRecord(Seq(feature.qualifiers['translation'][0], IUPAC.protein),
        id=feature.qualifiers['locus_tag'][0]+'|'+feature.qualifiers['db_xref'][0],
        description="\t{0}:{1}..{2}".format(refseq, 
            feature.location.start, feature.location.end),
        name = "",
        dbxrefs=feature.qualifiers['db_xref'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--genbank')
    parser.add_argument('-m', '--mapping') # map locus to gi
    parser.add_argument('-o', '--out')
    args = parser.parse_args()

    gb_handle = open(args.genbank, 'r')
    gb_record = SeqIO.read(gb_handle, 'gb')
    gb_record_id = gb_record.id
    gb_dict = {}
    for feature in gb_record.features:
        if feature.type == 'CDS':
            gb_dict[feature.qualifiers['db_xref'][0]] = feature
    gb_handle.close()

    with open(args.mapping, 'r') as f:
        header = f.readline() 
        if header[0] != '#':
            f.seek(0)
        locus, tgi, agi = zip(*[line.strip().split() for line in f])

    w1 = SeqIO.write((makeSeqRecord(gb_dict[gi], gb_record_id) for gi in tgi),
            args.out+'.toxin.faa', 'fasta')
    w2 = SeqIO.write((makeSeqRecord(gb_dict[gi], gb_record_id) for gi in agi),
            args.out+'.antitoxin.faa', 'fasta')

    assert w1 == w2

    print >> sys.stderr, "Wrote", w1, "records to each file."


if __name__ == '__main__':
    main()
