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
    labels = getIDs(args.datafile)
    X = getData(args.datafile)
    # Make predictions
    Y_hat = clf.predict(X)

    with open(args.prefix+".predictions.txt",'w') as o:
        o.write("Gene1\tGene2\tPrediction\n")
        for ((loc1,loc2),y) in zip(labels,Y_hat):
            o.write("\t".join([loc1,loc2,str(y)])+"\n")
    
    return

def getIDs(datafile):
    with open(datafile) as data:
        data.readline()
        IDs = [ line.strip().split("\t")[0:2] for line in data 
                if not line.startswith("#") ]
    return IDs

def getData(datafile):
    with open(datafile) as data:
        data.readline()
        X = [ line.strip().split("\t")[2:] for line in data
              if not line.startswith("#") ]
    return [ map(float,x) for x in X ]

if __name__ == '__main__':
    main()
