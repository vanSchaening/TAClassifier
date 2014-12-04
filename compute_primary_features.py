import argparse

from collections import Counter
from itertools import combinations, izip_longest, groupby, product
from operator import add

from Bio import SeqIO
from Bio.SeqUtils import CodonUsage
from Bio.SeqUtils.ProtParam import ProteinAnalysis

DNA_ALPHABET = sorted('ATCG')
DNA_ALPHABET_PAIR = list(combinations(DNA_ALPHABET, 2))
CODON_ALPHABET = sorted(CodonUsage.CodonsDict.keys())
AA_ALPHABET = sorted(CodonUsage.SynonymousCodons.keys())

header =  DNA_ALPHABET + ["".join(p) for p in DNA_ALPHABET_PAIR]
nc_headers = reduce(add, [[h+i for h in header] for i in ["", "1", "2", "3"]])
cu_headers = (["cupt_"+c for c in CODON_ALPHABET] + 
    reduce(add, [["rscu_"+c for c in CodonUsage.SynonymousCodons[aa]] 
    for aa in AA_ALPHABET])
    + ["cai"])
pf_headers = ["mw", "aromaticity", "instability", "isoelectric", 
              "gravy", "ssh", "sst", "sss"]
final_headers = nc_headers + cu_headers + pf_headers
final_headers = (['loci', 'gi_1', 'gi_2', 'class', 'aalen_1', 'aalen_2', 'distance'] + 
    [h+'_1' for h in final_headers] + [h+'_2' for h in final_headers])
#print gen_header()

def grouper(iterable, n, fillvalue = None):
    # https://docs.python.org/2/library/itertools.html
    # grouper('ABCDEF', 3, 'x')
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def composition_percentage(dna):
    nc_counter = Counter(dna)
    total = float(sum(nc_counter.values()))
    single = [nc_counter[n]/total for n in DNA_ALPHABET] 
    double = [(nc_counter[n[0]] + nc_counter[n[1]])/total for n in DNA_ALPHABET_PAIR]
    return single + double

def nucleotide_composition(dna):
    # % nucleotide frequency for DNA_ALPHABET overall, by position
    overall = composition_percentage(dna)
    position = reduce(add, [composition_percentage(dna[i::3]) for i in range(3)])
    #return zip(nc_headers, overall + position)
    return overall + position

def compute_rscu(codon_counter, aa):
    counts = [codon_counter[codon] for codon in CodonUsage.SynonymousCodons[aa]]
    mean = sum(counts)/float(len(counts))
    return [0 for count in counts] if mean == 0 else [count/mean for count in counts]

def compute_Nc(codon_counter):
    # broken
    groups = {6:3, 4:5, 3:1, 2:9}
    Nc = 2
    for group in groupby(sorted([(len(sc), sc) for aa, sc in
        CodonUsage.SynonymousCodons.iteritems()], reverse=True), lambda x:x[0]):
        sf_type, codon_class = group
        if sf_type < 2:
            continue
        F_sum = 0
        F_num = 0
        for n, codon_list in codon_class:
            n = float(n)
            codon_counts = [codon_counter[codon] for codon in codon_list
                if codon_counter[codon] != 0]
            total_codon_counts = float(sum(codon_counts))
            term = sum([((codon_count/total_codon_counts)**2) - 1 for codon_count in codon_counts])*n/(n-1)
            F_sum += term
            F_num += 1.
        Nc += groups[sf_type]/(F_sum/F_num)
    return Nc

def codon_usage(dna):

    codon_counter = Counter(CodonUsage.CodonsDict)
    codon_counter.update(("".join(codon) for codon in grouper(dna, 3) if len(codon) == 3))
    total_codons = float(sum(codon_counter.values()))
    
    # codon usage per thousand
    cupt = [ codon_counter[codon]*1000/total_codons for codon in CODON_ALPHABET ] 
    assert len(cupt) == len(CODON_ALPHABET)

    # relative synonymous codon usage is the ration of the observed frequency
    # of codons to the expected frequency given that all synonymous codons for
    # the same amino acids are used equally
    rscu = reduce(add, (compute_rscu(codon_counter, aa) for aa in AA_ALPHABET))
    try:
        assert len(rscu) == len(CODON_ALPHABET)
    except AssertionError:
        import pdb; pdb.set_trace()

    # codon adaptation index
    cai = CodonUsage.CodonAdaptationIndex().cai_for_gene(dna)
    

    # other features (see http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0072343#pone.0072343.s001)
    # - effective number of codons
    # Nc = compute_Nc(codon_counter)
    # - 2-tuple codon site specific nucleotide usage
    # - codon bias index
    # - frequency of optimal codons
    # - effective number of codons
    # - frequency of synonymous codons
    # - gene length (amino acids)

    return cupt + rscu + [cai]

def get_protein_analysis(aa):
    protein_analysis = ProteinAnalysis(aa)
    analyze = [protein_analysis.molecular_weight(), 
        protein_analysis.aromaticity(),
        protein_analysis.instability_index(),
        protein_analysis.isoelectric_point(),
        protein_analysis.gravy()] + list(
        protein_analysis.secondary_structure_fraction())
    return analyze

def compute_features(dna):
    aa = dna.translate(table=11, to_stop=True) # note that first aa should be M
    
    dna = str(dna).upper()
    aa = str(aa).upper()
    aa = 'M' + aa[1:-1]

    nuc_comp = nucleotide_composition(dna)
    codon_use = codon_usage(dna)
    protein_features = get_protein_analysis(aa)
    all_features = nuc_comp + codon_use + protein_features

    try:
        assert len(nuc_comp) == len(nc_headers)
        assert len(codon_use) == len(cu_headers)
        assert len(protein_features) == len(pf_headers)
    except AssertionError:
        import pdb; pdb.set_trace()

    return list(all_features)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--genbank')
    parser.add_argument('-m', '--mapping')
    parser.add_argument('-c', '--classs')
    args = parser.parse_args()

    gb_handle = open(args.genbank, 'r')
    gb_record = SeqIO.read(gb_handle, 'gb')
    gb_record_id = gb_record.id
    gb_record_seq = gb_record.seq
    gb_dict = {}
    for feature in gb_record.features:
        if feature.type == 'CDS':
            gb_dict[feature.qualifiers['db_xref'][0]] = feature
    gb_handle.close()


    print ','.join(final_headers) 

    with open(args.mapping, 'r') as f:
        header = f.readline() 
        if header[0] != '#':
            f.seek(0)

        for line in f:

            locus, tgi, agi = line.strip().split()
            
            t_record = gb_dict[tgi] 
            t_dna = t_record.location.extract(gb_record.seq)
            t_features = compute_features(t_dna)

            a_record = gb_dict[agi]
            a_dna = a_record.location.extract(gb_record.seq)
            a_features = compute_features(a_dna)

            # (a_start, a_end) (t_start, t_end)
            distance = t_record.location.start - a_record.location.end

            features = t_features + a_features
            features = ([locus, args.classs, tgi, agi, len(t_dna), len(a_dna), distance] 
                + t_features + a_features)
            assert len(features) == len(final_headers)
            print ','.join(str(f) for f in features)


if __name__ == '__main__':
    main()
