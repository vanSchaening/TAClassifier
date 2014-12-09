def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files',
                        help="File with list of training/validation datasets")
    parser.add_argument('-d', '--depth', type=int, default=4,
                        help="maximum tree depth")
    parser.add_argument('-o', '--output',
                        help="output prefix")
    args = parser.parse_args()


    # Get training/validation sets
    with open(args.files) as f:
        datasets = [ line.strip().split("\t") for line in f ]

    # Train
    from sklearn import tree
    ensemble = []
    for train,test in datasets:
        clf = tree.DecisionTreeClassifier(max_depth=args.depth)
        X_trn,Y_trn = getData(train)
        clf = clf.fit(X_trn,Y_trn)
        ensemble.append(clf)

    # Make a classifier that aggregates ensemble output
    clf = Ensemble(ensemble)

    import cPickle as pickle
    clf_file = args.output + ".ensemble.pkl"
    with open(clf_file,'wb') as o:
        pickle.dump(clf,o)

# -------------------------------------------------------------------------------

class Ensemble:
    def __init__(self,trees):
        self.trees = trees
    def predict(self,X):
        predictions = [ clf.predict(X) for clf in self.trees ]
        Y_hat = [ sum(row) for row in zip(*predictions) ]
        return [ sign(y_hat) for y_hat in Y_hat ]
        
def sign(z):
    if z < 0:
        return -1
    else:
        return +1

def getData(infile):
    with open(infile) as f:
        #skip header
        f.readline()
        #Get features
        X = [ map(float,line.strip().split("\t")[3:]) 
              for line in f ]
        #Get labels
        f.seek(0)
        f.readline()
        Y = [ int(line.split("\t")[2]) 
              for line in f ]
    return X,Y

# -------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
