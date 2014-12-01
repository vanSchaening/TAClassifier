import argparse
import sys

from itertools import islice, izip

from Bio import SeqIO

from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC

def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    "http://stackoverflow.com/questions/6822725/rolling-or-sliding-window-iterator-in-python"
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result    
    for elem in it:
        result = result[1:] + (elem,)
        yield result

def gb_filter_it(features, ta_loci):
    " Iterator over gb file, filters out hypothetical and known ta proteins "
    for feature in features:
        if feature.type == 'CDS':
            # filter out hypotehtical proteins
            if 'hypothetical' in feature.qualifiers['product'][0]:
                continue
            # filter out ta loci
            if ('locus_tag' in feature.qualifiers and 
                set(feature.qualifiers['locus_tag']) & ta_loci):
                continue
            if ('gene' in feature.qualifiers and 
                set(feature.qualifiers['gene']) & ta_loci):
                continue
            yield feature

def process_adj(gb, ta, out, up=100):
    
    ta_loci = set([record.id for record in SeqIO.parse(ta, 'fasta')])
    with open(gb, 'r') as f:
        record = SeqIO.read(f, 'gb')
        for i, (left, right) in enumerate(window(gb_filter_it(record.features, ta_loci))):
            if left.location.strand + right.location.strand == 2:
                upstream_end = left.location.start
                upstream_start = max(0, upstream_end-up)
            elif left.location.strand + right.location.strand == -2:
                upstream_start = right.location.end
                upstream_end = min(len(record.seq), upstream_start+up)
            else:
                continue
            negative_id = "{0!s}.{1!s}".format(out, i)
            left_record = SeqRecord(Seq(left.qualifiers['translation'][0], IUPAC.protein),
                id='|'.join(left.qualifiers['db_xref']),
                description="\t{0}:{1}..{2}\t{3}".format(
                    record.id, left.location.start, left.location.end,
                    negative_id))
            right_record = SeqRecord(Seq(right.qualifiers['translation'][0], IUPAC.protein),
                id='|'.join(right.qualifiers['db_xref']),
                description="\t{0}:{1}..{2}\t{3}".format(
                    record.id, right.location.start, right.location.end,
                    negative_id))
            upstream_record = SeqRecord(record.seq[upstream_start:upstream_end],
                id = negative_id,
                description="\t{0}:{1}..{2}".format(
                    record.id, upstream_start, upstream_end))
            yield (left_record, right_record, upstream_record)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--ta')
    parser.add_argument('-g', '--gb')
    parser.add_argument('-o', '--out')
    args = parser.parse_args()

    lefts, rights, upstreams = izip(*process_adj(args.gb, args.ta, args.out))

    w1 = SeqIO.write(lefts, "{0}.toxin_aa.negative.fa".format(args.out), 'fasta')
    w2 = SeqIO.write(rights, "{0}.antitoxin_aa.negative.fa".format(args.out), 'fasta')
    w3 = SeqIO.write(upstreams, "{0}.upstream.negative.fa".format(args.out), 'fasta')

    assert w1 == w2
    assert w2 == w3

    print >> sys.stderr, "Wrote", w1, "records."

if __name__ == '__main__':
    main()
