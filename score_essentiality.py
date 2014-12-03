# Use pre-computed essentiality scores

import argparse

def parse_essentiality_txt(essentiality_txt):
    
    with open(essentiality_txt, 'r') as f:
        line = f.readline()
        while line[0] == '#':
            line = f.readline() # Should get rid of header, which is an extra line
                                # after the comments
        for line in f:
            l = line.strip().split()
            score = float(l[1])
            gi = int(l[2].split('|')[1])
            yield (gi, score)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--essentiality')
    parser.add_argument('-m', '--mapping')
    args = parser.parse_args()

    essentiality_dict = {gi:score for gi, score in parse_essentiality_txt(args.essentiality)}
    get_gi = lambda gi:int(gi.split(':')[1])
    print "#LOCUS ES:TOXIN ES:ANTITOXIN"
    with open(args.mapping, 'r') as f:
        line = f.readline()
        if line[0] != '#':
            f.seek(0)
        for line in f:
            locus, gi1, gi2 = line.strip().split()
            print locus, essentiality_dict[get_gi(gi1)], essentiality_dict[get_gi(gi2)]


if __name__ == '__main__':
    main()
