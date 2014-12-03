# Generate a negative mapping from the genbank file by filtering out
# hypothetical proteins and proteins known to be in TA systems
# Additional filters can be added. 

import argparse

from itertools import islice

from Bio import SeqIO

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

def gb_filter_it(features, filter_loci=[], filter_gi=[]):
    for feature in features:
        if feature.type == 'CDS':
            if 'hypothetical' in feature.qualifiers['product'][0]:
                continue
            if ('locus_tag' in feature.qualifiers and 
                set(feature.qualifiers['locus_tag']) & filter_loci):
                continue
            if ('gene' in feature.qualifiers and
                set(feature.qualifiers['gene']) & filter_loci):
                continue
            if ('db_xref' in feature.qualifiers and 
                set(feature.qualifiers['db_xref']) & filter_gi):
                continue
            yield feature

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--positive', help="positive mapping")
    parser.add_argument('-g', '--genbank')
    args = parser.parse_args()

    with open(args.positive, 'r') as f:
        pos_loci, pos_gi1, pos_gi2 = map(set, zip(*[line.strip().split() for line in f]))
        pos_gis = pos_gi1.union(pos_gi2)

    gb_handle = open(args.genbank, 'r')
    gb_record = SeqIO.read(gb_handle, 'gb')
    gb_record_id = gb_record.id
    gb_handle.close()

    get_gi = lambda feature:feature.qualifiers['db_xref'][0]
    get_strand = lambda feature:feature.location.strand

    print "#LOCUS GI:TOXIN GI:ANTITOXIN"
    for i, (left, right) in enumerate(window(
        gb_filter_it(gb_record.features, pos_loci, pos_gis))):
        if abs(get_strand(left) + get_strand(right)) == 2:
            print "{0}_N{1} {2} {3}".format(gb_record.id, i, get_gi(left), get_gi(right)) 


if __name__ == '__main__':
    main()
