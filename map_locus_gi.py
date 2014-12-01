import argparse
import sys

from itertools import groupby, izip

from Bio import SeqIO

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--toxin')
    parser.add_argument('-a', '--antitoxin')
    parser.add_argument('-g', '--genbank')
    parser.add_argument('-r', '--refseq')
    args = parser.parse_args()

    gb_handle = open(args.genbank, 'r')
    gb_record = SeqIO.read(gb_handle, 'gb')
    gb_dict = {}
    for feature in gb_record.features:
        if feature.type == 'CDS':
            location = (int(feature.location.start)+1, int(feature.location.end))
            gb_dict[location] = feature
    gb_handle.close()
            
    toxin_handle = open(args.toxin, 'r')
    antitoxin_handle = open(args.antitoxin, 'r')
    toxin_parser = SeqIO.parse(toxin_handle, 'fasta')
    antitoxin_parser = SeqIO.parse(antitoxin_handle, 'fasta')

    by_refseq = lambda record:record.description.strip().split()[1].split(':')[0]
    by_locus_tag = lambda record:record.description.strip().split()[2]
    get_position = lambda record:tuple(map(int, 
        record.description.strip().split()[1].split(':')[1].split('..')))
    
    print "#LOCUS GI:TOXIN GI:ANTITOXIN"
    for (tr, tp), (ar, ap) in izip(groupby(toxin_parser, by_refseq), 
                       groupby(antitoxin_parser, by_refseq)):
        assert tr == ar
        if tr != args.refseq:
            continue
        for (tl, tli), (al, ali) in izip(groupby(tp, by_locus_tag), 
                                         groupby(ap, by_locus_tag)):
            assert tl == al
            tli = [t for t in tli]
            ali = [a for a in ali]
            if len(tli) > 1 or len(ali) > 1: # skip locus because multiple genes
                continue
        
            tlr = tli[0]
            alr = ali[0]
            try:
                tlb = gb_dict[get_position(tlr)]
                alb = gb_dict[get_position(alr)]
            except KeyError: 
                print >> sys.stderr, "Warning...skipping", tl
                continue 

            try:
                assert (tl in tlb.qualifiers['locus_tag'] or
                        tl in alb.qualifiers['locus_tag'])
            except AssertionError:
                assert (('gene' in tlb.qualifiers and tl in tlb.qualifiers['gene']) or 
                    ('gene' in alb.qualifiers and tl in alb.qualifiers['gene']))

            print tl, tlb.qualifiers['db_xref'][0], alb.qualifiers['db_xref'][0]

    gb_handle.close()
    toxin_handle.close()
    antitoxin_handle.close()

if __name__ == '__main__':
    main()
