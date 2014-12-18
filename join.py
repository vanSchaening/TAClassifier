def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--refid',
                        help="RefSeq ID")
    parser.add_argument('-o', '--outdir', default="",
                        help="Output directory")
    args = parser.parse_args()
    
    if args.outdir:
        if not args.outdir.endswith("/"):
            args.refid = args.outdir + "/" + args.refid
        else:
            args.refid = args.outdir + args.refid

    # Feature file names (without prefix)
    features = ["homology",
                "properties",
                "structure",
                "upalindromes",
                "essentiality"]

    from collections import defaultdict
    loci = defaultdict(dict)
    for feature in features:
        for locus,value in getFeature(args.refid,feature).iteritems():
            loci[locus][feature] = value

    with open(args.refid+".data.txt",'w') as o:
        o.write("\t".join(["locus_id","refseq",
                           "homology.toxin","homology.antitoxin",
                           "properties.gene1.pi","properties.gene2.pi",
                           "properties.gene1.weight","properties.gene2.weight",
                           "structure.gene1.length","structure.gene2.length",
                           "structure.distance","structure.overlap",
                           "upalindromes.length","upalindromes.distance",
                           "essentiality.toxin","essentiality.antitoxin",
                           "properties.ratio.pi","essentiality.ratio"])+"\n")
        for locus in loci:
            line = [ locus, args.refid ]
            line.extend([ "\t".join(values) for feature,values 
                          in loci[locus].iteritems() ])
            
            # Calculate isoelectric point ratio
            t_pi,a_pi = map(float,loci[locus]['properties'][1:3])
            line.append(str(t_pi/a_pi))
            # Calculate essentiality ratio
            t_ess,a_ess = map(float,loci[locus]['essentiality'])
            try:
                ratio = str(t_ess/a_ess)
            except ZeroDivisionError:
                ratio = "0"
            line.append(ratio)
            o.write("\t".join(line)+"\n")

    return

# ------------------------------------------------------------------------------
def getFeature(refid,feat_name):
    feat = dict()
    with open(refid+".features."+feat_name+".txt") as f:
        f.readline()
        for line in f:
            line = line.strip().split()
            feat[line[0]] = line[1:]
    return feat

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
    
