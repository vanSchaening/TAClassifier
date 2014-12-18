from learners.makeEnsemble import Ensemble

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--datafile",
                        help="set of points to classify")
    parser.add_argument('-c', "--classifier",
                        help="classifier in a .pkl")
    parser.add_argument('-r', "--prefix",
                        help="output prefix")
    args = parser.parse_args()

    # Import the classifier from the pickle
    try:
        # Ensembles must be imported with pickle
        import cPickle as pickle
        with open(args.classifier,'rb') as f:
            clf = pickle.load(f)
    except pickle.UnpicklingError:
        # Trees, random forests must be imported through sklearn's joblib
        from sklearn.externals import joblib
        clf = joblib.load(args.classifier)

    # A list of data and a list of corresponding labels
    labels = getIDs(args.datafile,args.prefix)
    X = getData(args.datafile)
    # Make predictions
    Y_hat = clf.predict(X)

    with open(args.prefix+".predictions.txt",'w') as o:
        o.write("Gene1\tGene2\tPrediction\n")
        for ((loc1,loc2),y) in zip(labels,Y_hat):
            o.write("\t".join([loc1,loc2,str(y)])+"\n")
    
    return

from itertools import izip
def getIDs(datafile,refid):
    with open(datafile) as data:
        attrs = len(data.readline().split("\t"))
        IDs = [ line.strip().split("\t")[0] for line in data ]
        data.seek(0)
        lens = [ len(line.split("\t")) for line in data ]
        IDs = [ i for i,size in izip(IDs,lens)
                if size == attrs ]
        print IDs
                #if len(line.split("\t")) == attrs ]
    with open(refid+".mapping.txt") as m:
        m.readline()
        loci = dict()
        for line in m:
            line = line.strip().split()
            loci[line[0]] = line[1:]
    IDs = [ loci[identifier] for identifier in IDs 
            if identifier in loci ]
    return IDs

def getData(datafile):
    with open(datafile) as data:
        num_attrs = len(data.readline().split("\t"))
        X = [ line.strip().split("\t")[2:] for line in data
              if not line.startswith("#") 
              and len(line.split("\t")) == num_attrs]
    return [ map(float,x) for x in X ]

if __name__ == '__main__':
    main()
