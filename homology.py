phage_db = "phageDB/phage.genomes.fasta"

# ------------------------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--antitoxin', help="antitoxin faa") # antitoxin aa fasta
    parser.add_argument('-t', '--toxin', help="toxin faa")         # toxin aa fasta
    parser.add_argument('-o', '--output', help="output prefix")    # output prefix
    parser.add_argument('-d', '--database', default=False,         # target database to
                        help="phage genome database")              #    blast against
    parser.add_argument('-e', '--evalue', type=int, default=20,    # evalue, default is 20
                        help="expect value for alignments")  
    args = parser.parse_args()

    if args.database:
        phage_db = args.database

    homology(args.toxin, args.antitoxin, args.evalue, args.output)


# ------------------------------------------------------------------------------

from Bio.Blast.Applications import NcbitblastnCommandline as BlastCommandLine
def homology(toxin_faa,antitoxin_faa, # Input fasta aa files
             evalue,                  # E-value parameter for BLAST
             out):                    # Output prefix

    # Run TBLASTN for toxin
    t_result = ".".join([out,"tblastn","toxin","xml"])
    runTBLASTN(toxin_faa,t_result,evalue)
    # Run TBLASTN for antitoxin
    a_result = ".".join([out,"tblastn","antitoxin","xml"])
    runTBLASTN(toxin_faa,a_result,evalue)

    # Summarize results
    t_scores = summarizeResults(t_results)
    a_scores = summarizeResults(a_results)
    # Store results into output files
    t_out = ".".join([out,"homology","toxin","csv"])
    a_out = ".".join([out,"homology","antitoxin","csv"])
    storeResults(t_scores,t_out)
    storeResults(a_scores,a_out)
    # Return output filenames
    return t_out,a_out


# ------------------------------------------------------------------------------

# Run tblastn (align aa seqs to translated nucleotide database) for 
# given parameters
def runTBLASTN(query_file,outfile,evalue):
    # Build blast command
    blast_cline = BlastCommandLine(query=query_file, db=phage_db,
                                   evalue=evalue,
                                   out=outfile,outfmt=5)
    # Run it, output will be stored in the files specified above
    stdout,stderr = blast_cline()

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
    o = open(outfile,'w')
    for name,score in scores.iteritems():
        o.write(name+"\t"+str(score)+"\n")
    o.close()

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
