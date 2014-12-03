# Get upstream sequences of length $window (according to strand in genbank)
# enumerate palindromes and return length and distance of best palindrome
# where the best palindrome is defined as the longest palindrome
# with the shortest length

import argparse

from Bio import SeqIO
from numpy import argmax, argmin

def enumerate_palindromes(s, minlen=2):
    # iterate over string, expand candidate palindrome at each position
    for i in range(len(s)):
        start = i
        end = i + 1
        while True:
            start = start - 1
            end = end + 1
            if start < 0:
                break
            if end > len(s):
                break
            candidate = s[start:end]
            if candidate[0] != candidate[-1]:
                break
            if len(candidate) > minlen:
                yield (start, end, candidate)

def best_palindrome(sequence, strand):
    # find longest and closest palindrome
    palindromes = [(start, end) for start, end, candidate in enumerate_palindromes(sequence)]
    if not palindromes:
        best_distance = len(sequence)
        best_length = 0
    else:
        lengths = [pend-pstart for pstart, pend in palindromes]
        best_palindrome = argmax(lengths) # greatest length
        if best_palindrome is list:
            best_length = lengths[best_palindrome[0]]
            palindromes = [palindromes[p] for p in best_palindrome]
            # distance to the end if strand == 1 else distance to the start
            distances = [len(sequence)-pend if strand == 1 else pstart+1 
                for pstart, pend in palindromes]
            best_palindrome = argmin(distances) # shortest distance
            if best_palindrome is list:
                best_distance = distances[best_palindrome][0]
            else:
                best_distance = distances[best_palindrome]
        else:
            best_length = lengths[best_palindrome]
            pstart, pend = palindromes[best_palindrome]
            best_distance = len(sequence)-pend if strand == 1 else pstart+1
    return (best_length, best_distance)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--genbank')
    parser.add_argument('-m', '--mapping')
    parser.add_argument('-w', '--window', type=int, default=50)
    args = parser.parse_args()

    gb_handle = open(args.genbank, 'r')
    gb_record = SeqIO.read(gb_handle, 'gb')
    gb_record_id = gb_record.id
    gb_record_seq = str(gb_record.seq).upper()
    gb_dict = {}
    for feature in gb_record.features:
        if feature.type == 'CDS':
            gb_dict[feature.qualifiers['db_xref'][0]] = feature
    gb_handle.close()

    upstream_window = args.window

    print "#LOCUS", "BEST_PALINDROME_LENGTH", "BEST_PALINDROME_DISTANCE"
    with open(args.mapping, 'r') as f:
        header = f.readline()
        if header[0] != '#':
            f.seek(0)
        for line in f:
            locus, tgi, agi = line.strip().split()
            strand = gb_dict[tgi].location.strand
            if strand == 1:
                upstream_end = min(gb_dict[tgi].location.start, gb_dict[agi].location.start)
                upstream_start = max(0, upstream_end - upstream_window)
            else:
                upstream_start = max(gb_dict[tgi].location.end, gb_dict[agi].location.end)
                upstream_end = min(len(gb_record_seq), upstream_start + upstream_window)
            upstream_seq = gb_record_seq[upstream_start:upstream_end]
            best_length, best_distance = best_palindrome(upstream_seq, strand)
            print locus, best_length, best_distance
            
if __name__ == '__main__':
    main()

