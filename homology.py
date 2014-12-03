# ------------------------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--antitoxin', help="antitoxin faa") # antitoxin aa fasta
    parser.add_argument('-t', '--toxin', help="toxin faa") # toxin aa fasta
    parser.add_argument('-o', '--output', help="output prefix") # output prefix
    parser.add_argument('-d', '--database', default=False, # target database to
                        help="phage genome database") # blast against
    parser.add_argument('-e', '--evalue', type=int, default=20, # evalue, default is 20
                        help="expect value for alignments")
    args = parser.parse_args()

    t_out,a_out = homology(args.toxin, args.antitoxin, args.database, 
                           args.evalue, args.output)
# ------------------------------------------------------------------------------

from Bio.Blast.Applications import NcbitblastnCommandline as BlastCommandLine
def homology(toxin_faa,antitoxin_faa, # Input fasta aa files
             database, # Path to target database
             evalue, # E-value parameter for BLAST
             out): # Output prefix

    # Run TBLASTN for toxin
    t_result = ".".join([out,"tblastn","toxin","xml"])
    runTBLASTN(toxin_faa,t_result,evalue,database)
    # Run TBLASTN for antitoxin
    a_result = ".".join([out,"tblastn","antitoxin","xml"])
    runTBLASTN(antitoxin_faa,a_result,evalue,database)

    # Summarize results
    t_scores = summarizeResults(t_result)
    a_scores = summarizeResults(a_result)

    joinScores(t_scores,a_scores,out)

    # Store results into output files
    t_out = ".".join([out,"homology","toxin","txt"])
    a_out = ".".join([out,"homology","antitoxin","txt"])
    storeResults(t_scores,t_out)
    storeResults(a_scores,a_out)

    # Return output filenames
    return t_out,a_out


# ------------------------------------------------------------------------------
# Run tblastn (align aa seqs to translated nucleotide database) for
# given parameters
def runTBLASTN(query_file,outfile,evalue,db):
    # Build blast command
    blast_cline = BlastCommandLine(query=query_file, db=db,
                                   evalue=evalue,
                                   out=outfile,outfmt=5)
    # Run it, output will be stored in the files specified above
    stdout,stderr = blast_cline()
    return

def joinScores(a_scores,t_scores,prefix):
    # Get starting positions for each gene
    import cPickle as pickle
    with open(prefix+".startPositions.pkl",'rb') as s:
        start = pickle.load(s)

    # Write homology scores for all pairs, order genes in 
    # a pair by position, not by toxin/antitoxin
    mapfile = prefix+".mapping.txt"
    outfile = prefix+".homology.txt"
    with open(mapfile) as id_map, open(outfile,'w') as o:
        for line in id_map:
            if line.startswith("#"):
                continue
            locus,gene1,gene2 = line.strip().split()
            if start[gene1] < start[gene2]:
                o.write("\t".join([ locus,
                                    score(gene1,a_scores,t_scores),
                                    score(gene2,a_scores,t_scores) ])+"\n")
            else:
                o.write("\t".join([ locus,
                                    score(gene2,a_scores,t_scores),
                                    score(gene1,a_scores,t_scores) ])+"\n")
    return outfile

def score(gene,a_scores,t_scores):
    if gene in a_scores:
        return a_scores[gene]
    elif gene in t_scores:
        return t_scores[gene]
    else:
        return "0"

# Store a single, best value for each query sequence
from Bio.Blast import NCBIXML
def summarizeResults(blast_results):
        # Parse XML-formatted BLAST output
        handle = open(blast_results)
        records = NCBIXML.parse(handle)
        # For each query, store the best alignment score
        scores = dict()
        for record in records:
            name = record.query
            for alignment in record.alignments:
                scores[name] = max([ hsp.score for hsp in alignment.hsps ])
        handle.close()
        return scores

def storeResults(scores,outfile):
    with open(outfile,'w') as o:
        for name,score in scores.iteritems():
            o.write(name+"\t"+str(score)+"\n")


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
